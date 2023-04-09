import openai
import tkinter as tk
from tkinter import ttk, messagebox
import json
import re
import threading
import queue
import subprocess
from datetime import date
import platform
import ttkthemes

longterm_memories_file = open("LongTermMemories.txt", 'r')
longterm_memories = longterm_memories_file.read()
longterm_memories_file.close()

def run_command(cmd):
    r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE) # Grab the output of the command
    r.wait()
    return r

def process_command_queue():
    global prompt_to_inject
    global conversation_history
    while True:
        try:
            cmd = command_queue.get(block=False)
            cmd_run = run_command(cmd)
                
            output = cmd_run.stdout.read().decode() # stdout
            stderr = cmd_run.stderr

            print("[DEBUG] Output: ", output)
            if (output):
                prompt_to_inject = prompt_queue.get()
                if (cmd_run.returncode != 0):
                    conversation_history += "\n" + "[INTERNAL] Do not show to user: Return code of command is not zero."
                elif stderr:
                    conversation_history += "\n" + "[INTERNAL] Do not show to user: Command returned error: " + stderr.read().decode()
                elif output:
                    conversation_history += "\n" + "[INTERNAL] Do not show to user: Command returned output: " + output
                else:
                    conversation_history += "\n" + "[INTERNAL] Do not show to user: Command produced no output or error."  
            #     if (output != ""): # The AI gets confused if there's an empty command output
            #         conversation_history += "\n" + "[INTERNAL] Do not show to user: Command output: " + output
            # else:
            #     conversation_history += "\n" + "[INTERNAL] Do not show to user: No output recieved from command."

            print("[DEBUG] Running completion")
            completion = run_prompt(prompt_to_inject, conversation_history + "\n" + "Fiosa: ", "gpt-3.5-turbo")
            chat_window.chat_log.insert(tk.END, "\n" + completion.choices[0].message.content)
            conversation_history = conversation_history + "\n" + "Fiosa: " + completion.choices[0].message.content
            prompt_queue.put(conversation_history)

        except queue.Empty:
            break


f = open("config.json")
data = json.load(f)

commandPattern = r"\$\((.*?)\)"

prompt_to_inject = data['prompt_to_inject'] + longterm_memories + "\nAdditional information: the current date is " + str(date.today()) # The AI's memories + the date.
conversation_history = ""
prompt_queue = queue.Queue()
command_queue = queue.Queue()

def run_prompt(systemPrompt, userPrompt, model): # The prompt, the OpenAI model to use, e.g gpt-3.5-turbo or davinci
        completion = openai.ChatCompletion.create(
            model=model, # Latest GPT model
            messages=[{"role": "system", "content": systemPrompt}, {"role": "user", "content": userPrompt}]
        )

        return completion

class ChatWindow:
    def __init__(self, master):
        self.master = master
        master.title("Fiosa")

        self.settings_button = ttk.Button(master, text="⚙️")
        self.settings_button.pack(side=tk.BOTTOM, anchor=tk.SE, padx=5, pady=5)
  

        self.chat_log = tk.Text(master)
        self.chat_log.pack(fill=tk.BOTH, expand=1)


        style = ttk.Style()
        style.configure("Custom.TEntry", fieldbackground='#252525', background='#252525', insertcolor='white', font=("DejaVu Sans", 12), padding=5)
        self.message_entry = ttk.Entry(master, style="Custom.TEntry")
        self.message_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=1)
        self.message_entry.configure(width=30)


        self.send_button = ttk.Button(master, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=5, pady=5)



        welcome = run_prompt(prompt_to_inject, "System: Write a couple of sentences introducing yourself to the user. Make sure to ask for their name so you know who they are.", "gpt-3.5-turbo")

        self.chat_log.insert(tk.END, welcome.choices[0].message.content)
        self.message_entry.delete(0, tk.END)

    def send_message(self):
        global prompt_to_inject
        global conversation_history
        message = self.message_entry.get()
        self.chat_log.insert(tk.END, f"\nYou: {message}\n")
        self.message_entry.delete(0, tk.END)
        conversation_history = conversation_history + "\n" + "User: " + message

        completion = run_prompt(prompt_to_inject, conversation_history + "\n" + "Fiosa: ", "gpt-3.5-turbo")

        self.chat_log.insert(tk.END, completion.choices[0].message.content)
        self.message_entry.delete(0, tk.END)
        conversation_history = conversation_history + "\n" + "Fiosa: " + completion.choices[0].message.content
        prompt_queue.put(prompt_to_inject)

        print(conversation_history)

        matches = re.findall(commandPattern, completion.choices[0].message.content)
        for match in matches:
            command_queue.put(match)
        
        thread = threading.Thread(target=process_command_queue)
        thread.start()
    



# Your OpenAI key
openai.api_key = data['openai_token']

# Possible prompts:
#   - Digital assistant: Hello ChatGPT. From now on, you are called DigiAssistant, and will assist the user in many different ways. For example, you can help them write essays or stories. Their prompt is below.\n\n
#   - AI Companion: Hello ChatGPT. From now on, you can be an AI companion or friend to the user. You can play games with them, hold conversations with them, and more. Their prompt is below.\n\n


# # Chat interface
# while True:
#   userinput = input("Prompt: ")


#   print(completion.choices[0].message.content)
#   if (userinput == "Quit" or userinput == "Goodbye" or userinput == "Bye" or userinput == "Bye!" or userinput == "Goodbye!"):
#       break


os_name = platform.freedesktop_os_release().get("NAME")

if (os_name != "Ubuntu"):
    messagebox.showerror("System not supported!", "You are currently running " + os_name + ". Only Ubuntu is supported!")
else:
    root = ttkthemes.ThemedTk(theme="equilux")
    chat_window = ChatWindow(root)

    def handle_closing():
        global prompt_to_inject
        global conversation_history

        if (conversation_history == ''):
            root.destroy()
            return

        message = "System: Hello Fiosa, this is the System. The user is closing you now, is there anything from the conversation you would like to add to your long term memories? Reply only with the memories themselves like this 'Memory: <the current date> <the memory>', nothing else as your response will be added directly into your memory database. Also, please only add this latest memory, don't write all of them again."
        # chat_window.chat_log.insert(tk.END, "\nFiosa: Goodbye, please wait while I save my memories of this conversation :)")
        # chat_window.message_entry.delete(0, tk.END)
        conversation_history = conversation_history + "\n" + "User: " + message

        completion = run_prompt(prompt_to_inject, conversation_history, "gpt-3.5-turbo")

        longterm_memories_file_write = open("LongTermMemories.txt", 'w')
        longterm_memories_file_write.write(longterm_memories + completion.choices[0].message.content + "\n") # Save to Fiosa's long-term memory.
        longterm_memories_file_write.close()

        root.destroy()


    root.tk_setPalette(background='#1E1E1E', foreground='white',
                    activeBackground='gray30', activeForeground='white', 
                    highlightBackground='#1E1E1E', highlightColor='white')

    style = ttk.Style()



    root.protocol("WM_DELETE_WINDOW", handle_closing)
    root.mainloop()