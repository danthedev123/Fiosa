# Command parser
# -- Author: danthedev123
# -- Description:
#   Fixes the following issues
#       - the sudo problem (GUI sudo)

import platform
import subprocess
import tkinter as tk
from tkinter import messagebox

def darwinElevCommandRun(command):

    isUserAdmin = None

    cmd = "osascript -e 'do shell script \"dseditgroup -o checkmember -m $USER admin\" with administrator privileges' >/dev/null 2>&1"
    result = subprocess.run(cmd, shell=False)

    # Check if the command succeeded (exit code 0) or failed (non-zero exit code)
    if result.returncode == 0:
        isUserAdmin = True
    else:
        isUserAdmin = False

    win = tk.Tk()

    if (isUserAdmin == True):
        tk.Label(win, text="To continue with that command, please enter your password below:").pack()

        password = tk.Entry(win)
        password.insert(0, "Password")
        password.pack()


        def button_click():
            password_string = password.get() # get() -> str
            sudo_command = "echo {} | sudo -S {}".format(password_string, command)
            subprocess.run(sudo_command, shell=False)
            win.destroy()
        
        tk.Button(win, text="Submit", command=button_click).pack()

        
    elif (isUserAdmin == False):
        tk.Label(win, text="To continue with that command, please enter an admin username and password below:").pack()

        username = tk.Entry(win)
        username.insert(0, "Username")
        username.pack()

        password = tk.Entry(win)
        password.insert(0, "Password")
        password.pack()

        def button_click():
            password_string = password.get()
            username_string = username.get()

            sudo_command = "echo {} | sudo -S -u {} {}".format(password_string, username_string, "echo {} | sudo -S -p '' {}".format(password_string, command))

            subprocess.run(sudo_command, shell=True)
            win.destroy()
        
        tk.Button(win, text="Submit", command=button_click).pack()

    win.mainloop()
    

def run_shell_command(command):
    if platform.system() == "Linux":
        if subprocess.call(["which", "pkexec"]) == 0:
            command = command.replace("sudo", "pkexec")
            subprocess.run(command, shell=False)
        else:
            subprocess.run(command, shell=False) # We don't have pkexec. TODO: Do something here
            messagebox.showwarning("Warning", "pkexec not found on system, executing using sudo (assuming you are running via CLI).")
    elif platform.system() == "Darwin":
        if "sudo" in command:
            darwinElevCommandRun(command.replace("sudo", ""))
        else:
            subprocess.run(command, shell=False)
    else:
        subprocess.run(command, shell=False)
