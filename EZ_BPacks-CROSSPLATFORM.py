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

## DISCLAIMER: This script is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement.

## This script is intended for educational and informational purposes only. The authors and ReadyCade, Inc. do not support or condone the illegal downloading or distribution of video games. Downloading video games
## without proper authorization is illegal and can result in severe penalties. Users are solely responsible for ensuring that their actions comply with applicable laws.

## This script does not actually download or store any video games. It is solely for mounting an online source, and no content will remain on your ReadyCade upon reboot.

## In no event shall the authors or ReadyCade, Inc. be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the script
## or the use or other dealings in the script. USE AT YOUR OWN RISK. YOU ASSUME ALL LIABILITY FOR ANY ACTIONS TAKEN BASED ON THIS SCRIPT.
#################################################################################################################

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
from playsound import playsound  # Cross-platform sound playback

# Get the user's home directory
home_directory = os.path.expanduser("~")

# Define the target directory for cleanup
target_directory = os.path.join(home_directory, "readycade", "biospacks")

# Determine the installation directory for 7-Zip
if platform.system() == 'Windows':
    # On Windows, use a common location for program installations
    install_dir = os.path.join("C:", "Program Files", "7-Zip")
else:
    # On Linux and macOS, use a common system-wide location for program installations
    install_dir = "/usr/bin"

# Get the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the relative path to the EULA.txt file
eula_path = os.path.join(script_dir, "EULA.txt")

# Define the relative path to the ready.wav file
sound_file_path = os.path.join(script_dir, "ready.wav")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
 
    return os.path.join(base_path, relative_path)

def play_ready_sound():
    if platform.system() == 'Windows':
        import winsound
        winsound.PlaySound(sound_file_path, winsound.SND_FILENAME)
    else:
        playsound(sound_file_path)

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

# Instead of exiting, inform the user and proceed if necessary (CROSS PLATFORM)
def check_platform():
    current_platform = platform.system()
    if current_platform not in ['Windows', 'Darwin', 'Linux']:
        messagebox.showerror("Error", "This script is intended to run on Windows, Mac, or Linux only. Exiting.")
        sys.exit(1)

# Call the function to check the platform
check_platform()

# If the platform check passed, continue with the rest of your code
print(f"Script is running on {platform.system()}. Continue execution.")

# CHECK NETWORK SHARE
def check_network_share():
    if platform.system() == 'Windows':
        command = ["ping", "-n", "1", "RECALBOX"]
    else:
        command = ["ping", "-c", "1", "RECALBOX"]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Network share found.")
    except subprocess.CalledProcessError:
        print("Error: Could not connect to the network share \\RECALBOX.")
        print("Please make sure you are connected to the network and try again.")
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror("Error", "Network Share not found. Please make sure you are connected to the network and try again.")
        sys.exit()

check_network_share()

# Define the 7-Zip version and download URLs
version = "2406"
download_urls = {
    "Windows": f"https://www.7-zip.org/a/7z{version}-x64.msi",
    "Linux_x86_64": f"https://www.7-zip.org/a/7z{version}-linux-x64.tar.xz",
    "Linux_arm64": f"https://www.7-zip.org/a/7z{version}-linux-arm64.tar.xz",
    "macOS": f"https://www.7-zip.org/a/7z{version}-mac.tar.xz"
}

# Determine the current platform
current_platform = platform.system()
if current_platform == 'Linux':
    arch = platform.machine()
    if arch == 'x86_64':
        downloadURL = download_urls["Linux_x86_64"]
    elif arch == 'aarch64':
        downloadURL = download_urls["Linux_arm64"]
    else:
        print(f"Unsupported Linux architecture: {arch}")
        exit_code = 1
elif current_platform == 'Darwin':
    downloadURL = download_urls["macOS"]
elif current_platform == 'Windows':
    downloadURL = download_urls["Windows"]
else:
    print(f"Unsupported platform: {current_platform}")
    exit_code = 1

# Define the installation directory for 7-Zip
if current_platform == 'Windows':
    installDir = "C:\\Program Files\\7-Zip"
    executable_name = "7z.exe"
elif current_platform in ['Linux', 'Darwin']:
    installDir = "/usr/bin"
    executable_name = "7zz"
else:
    print(f"Unsupported platform: {current_platform}")
    exit_code = 1

# Check if 7-Zip is already installed
if not os.path.exists(os.path.join(installDir, executable_name)):
    # Define the temporary directory for downloading the installer
    home_directory = os.path.expanduser("~")
    tempDir = os.path.join(home_directory, "readycade", "7zip_temp")
    os.makedirs(tempDir, exist_ok=True)
    downloadPath = os.path.join(tempDir, os.path.basename(downloadURL))

    # Download the installer
    with requests.get(downloadURL, stream=True) as response, open(downloadPath, 'wb') as outFile:
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        with tqdm(total=total_size, unit='B', unit_scale=True, desc='Downloading 7-Zip') as pbar:
            for data in response.iter_content(block_size):
                pbar.update(len(data))
                outFile.write(data)

    # Run the installer based on the platform
    if current_platform == 'Windows':
        try:
            subprocess.run(["msiexec", "/i", downloadPath], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Installation failed with error: {e}")
            exit_code = 1
    elif current_platform == 'Linux' or current_platform == 'Darwin':
        try:
            with tarfile.open(downloadPath, 'r:xz') as tar:
                tar.extractall(path=tempDir)
        except Exception as e:
            print(f"Installation failed with error: {e}")
            exit_code = 1

        # Move binaries to install directory and make them executable
        extracted_folder = os.path.join(tempDir, f"7z{version}")
        binaries = [os.path.join(extracted_folder, f) for f in os.listdir(extracted_folder) if os.path.isfile(os.path.join(extracted_folder, f))]
        for binary in binaries:
            try:
                os.rename(binary, os.path.join(installDir, executable_name))
                os.chmod(os.path.join(installDir, executable_name), 0o755)  # Make executable
            except Exception as e:
                print(f"Error moving binary {binary} to {installDir}: {e}")

        print("7-Zip is now installed.")
else:
    print("7-Zip is already installed.")


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
    shutil.rmtree(target_directory, ignore_errors=True)

    # Clear status label
    status_var.set("")

    # Update status label
    update_status("Deleting Temporary Files... Please Wait...")
    print("Deleting Temporary Files... Please Wait...")

    # Sleep for 2 seconds
    time.sleep(2)

    # Clear status label
    status_var.set("")

# Function to open a file
def open_file():
    browse_text.set("loading...")

    # Update the GUI more frequently during the process
    def update_gui():
        root.update_idletasks()
        root.after(100, update_gui)

    update_gui()  # Start updating the GUI

    # Prompt the user to select a file using askopenfile
    file = askopenfile(parent=root, mode='rb', title="Choose a Bios Pack (recalbox MUST in the name .zip or .7z only)", filetypes=[("Archives", "*.zip;*.7z")])
    if file:
        # Check if the file name contains "recalbox"
        if "recalbox" in os.path.basename(file.name).lower():
            # Define paths
            appdata_path = os.path.join(home_directory, "readycade", "biospacks")
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
            extract_command = r'"C:\Program Files\7-Zip\7z.exe" x "{}" -o"{}"'.format(file.name, appdata_path)

            subprocess.run(extract_command, shell=True)

            # Update status label
            update_status("Copying Bios Files to your Readycade...")

            print("Copying to Bios Files to your Readycade...")

            # Copy the extracted contents to the destination directory
            for root_dir, dirs, files in os.walk(appdata_path):
                for file in files:
                    if not file.startswith('.'):
                        src_file = os.path.join(root_dir, file)
                        dst_file = os.path.join(temp_path, os.path.relpath(src_file, appdata_path))
                        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                        shutil.copy(src_file, dst_file)

            # Update status label
            print("Success", "Extraction and Copying completed. Please reboot your Readycade now.")
            update_status("Ready!")
            play_ready_sound()
            # Show messagebox
            messagebox.showinfo("Success", "Extraction and Copying completed. Please reboot your Readycade now.")

        else:
            print("Selected file does not contain 'recalbox' in the name.")
            messagebox.showerror("Error", "Selected file does not contain 'recalbox' in the name.")

    # Set button text back to "Browse" regardless of whether a file was selected or not
    browse_text.set("Browse")

    # Move cleanup outside the if condition to ensure it's called even if the user cancels the file selection
    cleanup()


# Initialize Tkinter
root = tk.Tk()

# Hide the main window initially
root.withdraw()

# Show EULA before creating the main window
show_eula()

# set the window title
root.title("Readycade™")

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

cleanup()

root.mainloop()