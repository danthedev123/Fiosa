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
import sys
import webbrowser


def requestOpenAIKey():
    global setKey
    setKey = None
    root = tk.Tk()
    root.title("Enter OpenAI key")

    prompt_label = tk.Label(root, text="Please enter your OpenAI API token. If you are unsure, press the help button for instructions and details :)")
    prompt_label.pack()

    input_entry = tk.Entry(root)
    input_entry.pack()
    input_entry.focus()


    def submit():
        global setKey
        input_val = input_entry.get()
        root.destroy()
        setKey = input_val

    submit_button = tk.Button(root, text="Submit", command=submit)
    submit_button.pack()

    def help():
        webbrowser.open("https://www.example.com") # TODO Replace


    help_button = tk.Button(root, text="Help", command=help)
    help_button.pack()

    root.mainloop()

    return setKey

def modifyOpenAIKey():
    key = requestOpenAIKey()
    data['openai_token'] = key

    print(key)

    jsonObj = json.dumps(data, indent=4)

    with open("config.json", "w") as outfile:
        outfile.write(jsonObj)



longterm_memories_file = open("LongTermMemories.txt", 'r')
longterm_memories = longterm_memories_file.read()
longterm_memories_file.close()


os_name = None
os_type = None

if (sys.platform == "linux"):
    os_name = platform.freedesktop_os_release().get("NAME")
    os_type = "linux"
elif (sys.platform == "darwin"): # OSX/MacOS
    os_name = "Darwin/OSX " + platform.mac_ver()[0]
    os_type = "mac"
else:
    os_name = "Unknown (version unknown)"
    os_type = "Unknown"


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

prompt_to_inject = None

if (os_type == "linux"):
    prompt_file = open("prompts/linux.txt")
    prompt = prompt_file.read()
    prompt_file.close()
    prompt_to_inject = prompt + longterm_memories + "\nAdditional information: the current date is " + str(date.today()) # The AI's memories + the date.
elif (os_type == "mac"):
    prompt_file = open("prompts/mac.txt")
    prompt = prompt_file.read()
    prompt_file.close()
    prompt_to_inject = prompt + longterm_memories + "\nAdditional information: the current date is " + str(date.today()) + " and the MacOS version is " + os_name # The AI's memories + the date.

conversation_history = ""
prompt_queue = queue.Queue()
command_queue = queue.Queue()

if (data['openai_token'] == ''):
    modifyOpenAIKey()


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

        self.settings_button = ttk.Button(master, text="⚙️", command=modifyOpenAIKey)
        self.settings_button.pack(side=tk.BOTTOM, anchor=tk.SE, padx=5, pady=5)
  

        self.chat_log = tk.Text(master)
        self.chat_log.pack(fill=tk.BOTH, expand=1)

        self.message_entry = ttk.Entry(master)
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


if (os_name != "Ubuntu" and os_type != "mac"):
    messagebox.showerror("System not supported!", "You are currently running " + os_name + ". Only Ubuntu is supported!")
else:
    root = None
    if (os_type == "mac"):
        root = tk.Tk() # MacOS actually has a good standard system toolkit (Cocoa) so we are OK with the system managing the theme
    else: # Linux
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


    style = ttk.Style()



    root.protocol("WM_DELETE_WINDOW", handle_closing)
    root.mainloop()