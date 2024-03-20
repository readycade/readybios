"""
************************************************************************** 
* READYCADE CONFIDENTIAL
* __________________
* 
*  [2024] Readycade Incorporated 
*  All Rights Reserved.
* 
* NOTICE:  All information contained herein is, and remains* the property of Readycade Incorporated and its suppliers,
* if any.  The intellectual and technical concepts contained* herein are proprietary to Readycade Incorporated
* and its suppliers and may be covered by U.S. and Foreign Patents,
* patents in process, and are protected by trade secret or copyright law.
* Dissemination of this information or reproduction of this material
* is strictly forbidden unless prior written permission is obtained
* from Readycade Incorporated.
**************************************************************************
* Author Michael Cabral 2024
* Title: EZ_Bios_Packs
* GPL-3.0 License
* Description: Downloads and Installs Bios Packs (Recalbox 9/9.1+) to your Readycade
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import Tk, Label, StringVar, Button, Scrollbar, Text
from tkinter.filedialog import askopenfile
from tkinter import messagebox
import os
import requests
from PIL import Image, ImageTk
import platform
import subprocess
import shutil
import sys
import time
from tqdm import tqdm

script_dir = os.path.dirname(os.path.abspath(__file__))

eula_path = os.path.join(script_dir, "EULA.txt")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
 
    return os.path.join(base_path, relative_path)

def show_eula():
    with open(eula_path, "r") as file:
        eula_text = file.read()

    eula_window = tk.Toplevel()
    eula_window.title("End User License Agreement")

    text_box = Text(eula_window, wrap=tk.WORD, height=24, width=70, padx=15, pady=15)
    text_box.insert(tk.END, eula_text)
    text_box.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    scrollbar = Scrollbar(eula_window, command=text_box.yview)
    scrollbar.grid(row=0, column=1, sticky="nsew")
    text_box['yscrollcommand'] = scrollbar.set

    def agree():
        eula_window.destroy()
        root.deiconify()

    agree_button = tk.Button(eula_window, text="Agree", command=agree)
    agree_button.grid(row=1, column=0, padx=5, pady=5)

    eula_window.geometry("640x480")

    eula_window.focus_force()

    eula_window.protocol("WM_DELETE_WINDOW", agree)

def check_windows():
    if platform.system() != 'Windows':
        messagebox.showerror("Error", "This script is intended to run on Windows only. Exiting.")
        sys.exit(1)

check_windows()

print("Script is running on Windows. Continue execution.")

print("Checking if the network share is available...")

try:
    subprocess.run(["ping", "-n", "1", "RECALBOX"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Network share found.")
except subprocess.CalledProcessError:
    print("Error: Could not connect to the network share \\RECALBOX.")
    print("Please make sure you are connected to the network and try again.")
    
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", "Network Share not found. Please make sure you are connected to the network and try again.")
    sys.exit()

print()

root = tk.Tk()

installDir = "C:\\Program Files\\7-Zip"

version = "2301"

downloadURL = f"https://www.7-zip.org/a/7z{version}-x64.exe"

seven_zip_installed = os.path.exists(os.path.join(installDir, "7z.exe"))

if seven_zip_installed:
    print("7-Zip is already installed.")
else:
    print("Authentication successful. Proceeding with installation...")

    localTempDir = os.path.join(os.environ["APPDATA"], "readycade", "temp")

    os.makedirs(localTempDir, exist_ok=True)
    downloadPath = os.path.join(localTempDir, "7z_installer.exe")
    with requests.get(downloadURL, stream=True) as response, open(downloadPath, 'wb') as outFile:
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        with tqdm(total=total_size, unit='B', unit_scale=True, desc='Downloading 7-Zip') as pbar:
            for data in response.iter_content(block_size):
                pbar.update(len(data))
                outFile.write(data)

    subprocess.run(["start", "/wait", "", downloadPath], shell=True)

    if not os.path.exists(os.path.join(installDir, "7z.exe")):
        print("Installation failed.")
        sys.exit()

    print("7-Zip is now installed.")

status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var, font="open-sans")
status_label.grid(columnspan=3, column=0, row=4)

def update_status(message):
    status_var.set(message)
    root.update_idletasks()

def cleanup():
    def update_gui_cleanup():
        root.update_idletasks()
        root.after(100, update_gui_cleanup)

    update_gui_cleanup()

    shutil.rmtree(os.path.join(os.environ['APPDATA'], 'readycade', 'biospacks'), ignore_errors=True)

    update_status("Deleting Temporary Files... Please Wait...")
    print("Deleting Temporary Files... Please Wait...")

    time.sleep(2)

    status_var.set("")

def open_file():
    browse_text.set("loading...")

    def update_gui():
        root.update_idletasks()
        root.after(100, update_gui)

    update_gui()

    file = askopenfile(parent=root, mode='rb', title="Choose a Bios Pack (recalbox MUST in the name .zip or .7z only)", filetype=[("ZIP files", "*.zip;*.7z")])
    if file:
        if "recalbox" in os.path.basename(file.name).lower():
            appdata_path = os.path.join(os.environ['APPDATA'], 'readycade', 'biospacks')
            temp_path = r'\\RECALBOX\share'

            os.makedirs(appdata_path, exist_ok=True)
            os.makedirs(temp_path, exist_ok=True)

            update_status("Extracting Files...")

            print("Extracting Files...")

            status_var.set("")

            extract_command = r'"C:\Program Files\7-Zip\7z.exe" x "{}" -o"{}"'.format(file.name, appdata_path)

            subprocess.run(extract_command, shell=True)

            update_status("Copying Bios Files to your Readycade...")

            print("Copying to Bios Files to your Readycade...")

            for root_dir, dirs, files in os.walk(appdata_path):
                for file in files:
                    if not file.startswith('.'):
                        src_file = os.path.join(root_dir, file)
                        dst_file = os.path.join(temp_path, os.path.relpath(src_file, appdata_path))
                        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                        shutil.copy(src_file, dst_file)

            print("Success", "Extraction and Copying completed. Please reboot your Readycade now.")

            messagebox.showinfo("Success", "Extraction and Copying completed. Please reboot your Readycade now.")

        else:
            print("Selected file does not contain 'recalbox' in the name.")
            messagebox.showerror("Error", "Selected file does not contain 'recalbox' in the name.")

    browse_text.set("Browse")

    cleanup()

root.withdraw()

show_eula()

root.title("Readycade™")

icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
root.iconbitmap(icon_path)

logo_path = os.path.join(os.path.dirname(__file__), 'logo.png')
logo = Image.open(logo_path)
logo = ImageTk.PhotoImage(logo)
logo_label = tk.Label(image=logo)
logo_label.image = logo
logo_label.grid(column=1, row=0)

Instructions = tk.Label(root, text="Select a Bios Pack on your computer to install to your Readycade", font="open-sans")
Instructions.grid(columnspan=3, column=0, row=1)

status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var, font="open-sans")
status_label.grid(columnspan=3, column=0, row=4)

browse_text = tk.StringVar()
browse_btn = tk.Button(root, textvariable=browse_text, command=open_file, font="open-sans", bg="#ff6600", fg="white", height=2, width=15)
browse_text.set("Browse")
browse_btn.grid(column=1, row=2)

canvas = tk.Canvas(root, width=600, height=50)
canvas.grid(columnspan=3)

cleanup()

root.mainloop()