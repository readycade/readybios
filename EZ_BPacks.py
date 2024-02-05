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
from tkinter.filedialog import askopenfile
from tkinter import ttk, messagebox, simpledialog, Scrollbar, Text
import os
from PIL import Image, ImageTk
import platform
import subprocess
import shutil
import sys
import time
from tqdm import tqdm

# Get the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the relative path to the EULA.txt file
eula_path = os.path.join(script_dir, "EULA.txt")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
 
    return os.path.join(base_path, relative_path)

def show_eula():
    # Load EULA from EULA.txt
    with open(eula_path, "r") as file:
        eula_text = file.read()

    # Create a new window for displaying the EULA
    eula_window = tk.Toplevel()
    eula_window.title("End User License Agreement")

    # Add a Text widget for displaying the EULA text with a scroll bar
    text_box = Text(eula_window, wrap=tk.WORD, height=24, width=70, padx=15, pady=15)
    text_box.insert(tk.END, eula_text)
    text_box.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # Add a scrollbar
    scrollbar = Scrollbar(eula_window, command=text_box.yview)
    scrollbar.grid(row=0, column=1, sticky="nsew")
    text_box['yscrollcommand'] = scrollbar.set

    # Add "Agree" and "Disagree" buttons
    def agree():
        eula_window.destroy()
        root.deiconify()

    agree_button = tk.Button(eula_window, text="Agree", command=agree)
    agree_button.grid(row=1, column=0, padx=5, pady=5)

    # Adjust the size of the EULA window
    eula_window.geometry("640x480")

    # Force the focus on the EULA window
    eula_window.focus_force()

    # Handle window closure
    eula_window.protocol("WM_DELETE_WINDOW", agree)

def check_windows():
    if platform.system() != 'Windows':
        messagebox.showerror("Error", "This script is intended to run on Windows only. Exiting.")
        sys.exit(1)

# Call the function to check the platform
check_windows()

# If the platform check passed, continue with the rest of your code
print("Script is running on Windows. Continue execution.")

# CHECK NETWORK SHARE
print("Checking if the network share is available...")

try:
    subprocess.run(["ping", "-n", "1", "RECALBOX"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Network share found.")
except subprocess.CalledProcessError:
    print("Error: Could not connect to the network share \\RECALBOX.")
    print("Please make sure you are connected to the network and try again.")
    
    # Show a message box
    #root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showerror("Error", "Network Share not found. Please make sure you are connected to the network and try again.")
    sys.exit()

print()

# Initialize Tkinter
root = tk.Tk()

# Define the installation directory for 7-Zip
installDir = "C:\\Program Files\\7-Zip"

# Define the 7-Zip version you want to download
version = "2301"

# Define the download URL for the specified version
downloadURL = f"https://www.7-zip.org/a/7z{version}-x64.exe"

# Check if 7-Zip is already installed by looking for 7z.exe in the installation directory
seven_zip_installed = os.path.exists(os.path.join(installDir, "7z.exe"))

if seven_zip_installed:
    print("7-Zip is already installed.")
else:
    # Echo a message to inform the user about the script's purpose
    print("Authentication successful. Proceeding with installation...")

    # Define the local directory to save the downloaded installer
    #localTempDir = os.path.expandvars(r"%APPDATA%\readycade\temp")

    # Define the relative path to the localTempDir
    localTempDir = os.path.join(os.environ["APPDATA"], "readycade", "temp")

    # Download the 7-Zip installer using curl and retain the original name
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

    # Run the 7-Zip installer and wait for it to complete
    subprocess.run(["start", "/wait", "", downloadPath], shell=True)

    # Check if the installation was successful
    if not os.path.exists(os.path.join(installDir, "7z.exe")):
        print("Installation failed.")
        sys.exit()

    # Additional code to run after the installation is complete
    print("7-Zip is now installed.")

# Function to update the status label
def update_status(message):
    status_var.set(message)
    root.update_idletasks()

# Function to perform cleanup
def cleanup():
    # Update the GUI more frequently during the cleanup process
    def update_gui_cleanup():
        root.update_idletasks()
        root.after(100, update_gui_cleanup)

    update_gui_cleanup()  # Start updating the GUI

    # Clean up downloaded and extracted files
    shutil.rmtree(os.path.join(os.environ['APPDATA'], 'readycade', 'biospacks'), ignore_errors=True)

    # Update status label
    update_status("Deleting Temporary Files... Please Wait...")
    print("Deleting Temporary Files... Please Wait...")

    # Sleep for 2 seconds
    time.sleep(2)

    # Clear status label
    status_var.set("")

# Status label
status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var, font="open-sans")
status_label.grid(columnspan=3, column=0, row=4)

def open_file():
    browse_text.set("loading...")

    # Update the GUI more frequently during the process
    def update_gui():
        root.update_idletasks()
        root.after(100, update_gui)

    update_gui()  # Start updating the GUI

    file = askopenfile(parent=root, mode='rb', title="Choose a file", filetype=[("ZIP files", "*.zip;*.7z")])
    if file:
        # Check if the file name contains "recalbox"
        if "recalbox" in os.path.basename(file.name).lower():
            # Define paths
            appdata_path = os.path.join(os.environ['APPDATA'], 'readycade', 'biospacks')
            #temp_path = r'F:\Readycade\TEMP\share'
            temp_path = r'\\RECALBOX\share'

            # Ensure the directories exist
            os.makedirs(appdata_path, exist_ok=True)
            os.makedirs(temp_path, exist_ok=True)

            # Update status label
            update_status("Extracting Files...")

            print("Extracting Files...")

            # Clear status label
            status_var.set("")

            # Extract using 7-Zip (adjust the path to 7z.exe accordingly)
            extract_command = '7z x "{}" -o"{}"'.format(file.name, appdata_path)

            subprocess.run(extract_command, shell=True)

            # Update status label
            update_status("Copying Bios Files to your Readycade...")

            print("Copying to Bios Files to your Readycade...")

            # Copy the extracted contents to the destination directory
            shutil.copytree(appdata_path, temp_path, dirs_exist_ok=True)

            # Update status label
            print("Success", "Extraction and Copying completed. Please reboot your Readycade now.")

            # Show messagebox
            messagebox.showinfo("Success", "Extraction and Copying completed. Please reboot your Readycade now.")

        else:
            print("Selected file does not contain 'recalbox' in the name.")
            messagebox.showerror("Error", "Selected file does not contain 'recalbox' in the name.")

    # Set button text back to "Browse" regardless of whether a file was selected or not
    browse_text.set("Browse")

    # Move cleanup outside the if condition to ensure it's called even if the user cancels the file selection
    cleanup()


# Hide the main window initially
root.withdraw()

# Show EULA before creating the main window
show_eula()

# set the window title
root.title("Readycade™")

# Remove the TK icon
#root.iconbitmap(default="icon.ico")

# Set the window icon
icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')  # Replace 'icon.ico' with your actual icon file
root.iconbitmap(icon_path)

# Logo
logo_path = os.path.join(os.path.dirname(__file__), 'logo.png')
logo = Image.open(logo_path)
logo = ImageTk.PhotoImage(logo)
logo_label = tk.Label(image=logo)
logo_label.image = logo
logo_label.grid(column=1, row=0)

# Instructions
Instructions = tk.Label(root, text="Select a Bios Pack on your computer to install to your Readycade", font="open-sans")
Instructions.grid(columnspan=3, column=0, row=1)

# Status label
status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var, font="open-sans")
status_label.grid(columnspan=3, column=0, row=4)

# Browse Button
browse_text = tk.StringVar()
browse_btn = tk.Button(root, textvariable=browse_text, command=open_file, font="open-sans", bg="#ff6600", fg="white", height=2, width=15)
browse_text.set("Browse")
browse_btn.grid(column=1, row=2)

canvas = tk.Canvas(root, width=600, height=50)
canvas.grid(columnspan=3)

root.mainloop()