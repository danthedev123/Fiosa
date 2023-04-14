# (c) 2023 Fiosa Project
# Authored DTD-123 (danthedev123)
# Co-authored ChatGPT

import tkinter
import pathlib
import os
import subprocess
import shutil

pl = pathlib.Path()
home = pl.home()

root = tkinter.Tk()
root.title("MacOS Installer App")

install_text = tkinter.Label(root, text="MacOS Install (this will install to your local user account)")
install_text.pack()

def install():
    fiosa_dir = os.path.join(home, "Fiosa")
    if not os.path.exists(fiosa_dir):
        os.mkdir(fiosa_dir)
    fiosa_files = ["fiosa.py", "config.json"]
    for f in fiosa_files:
        src_file = f
        dest_file = os.path.join(fiosa_dir, f)
        if not os.path.exists(dest_file):
            shutil.copy(src_file, dest_file)
    memories_file = os.path.join(fiosa_dir, "LongTermMemories.txt")
    if not os.path.exists(memories_file):
        open(memories_file, "w").close()
    subprocess.run(["pip3", "install", "openai", "ttkthemes"])
    python_dir = os.path.join(fiosa_dir, "python3")
    pip_dir = os.path.join(fiosa_dir, "pip3")
    subprocess.run(["which", "python3"], stdout=open(python_dir, "w"))
    subprocess.run(["which", "pip3"], stdout=open(pip_dir, "w"))

install_button = tkinter.Button(root, text="Install", command=install)
install_button.pack()

root.mainloop()
