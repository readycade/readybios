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
* Title: EZ_Rom_Packs
* GPL-3.0 License
* Description: Downloads and Installs Rom Packs to your Readycade eg: n64.zip, snes.7z ect
"""

import tkinter as tk
from tkinter.filedialog import askopenfile
from tkinter import ttk, messagebox, simpledialog
from tkinter import Tk, Label, StringVar, Button
from tkinter.filedialog import askopenfile
from tkinter import messagebox
import os
from PIL import Image, ImageTk
import platform
import subprocess
import shutil
import sys
import time
#from tqdm import tqdm

# Set global password
global_password = "readysetgo"

# Dictionary of valid console names
valid_consoles = {
    "64dd": "Nintendo 64DD",
    "amiga600": "Amiga 600",
    "amiga1200": "Amiga 1200",
    "amstradcpc": "Amstrad CPC",
    "apple2": "Apple II",
    "apple2gs": "Apple IIGS",
    "arduboy": "Arduboy",
    "atari800": "Atari 800",
    "atari2600": "Atari 2600",
    "atari5200": "Atari 5200",
    "atari7800": "Atari 7800",
    "atarist": "Atari ST",
    "atomiswave": "Atomiswave",
    "bbcmicro": "BBC Micro",
    "bk": "BK",
    "c64": "Commodore 64",
    "channelf": "Channel F",
    "colecovision": "ColecoVision",
    "daphne": "Daphne",
    "dos": "DOS",
    "fds": "Famicom Disk System",
    "gamegear": "Game Gear",
    "gba": "Game Boy Advance",
    "gbc": "Game Boy Color",
    "gb": "Game Boy",
    "gw": "GW",
    "gx4000": "GX4000",
    "intellivision": "Intellivision",
    "jaguar": "Atari Jaguar",
    "lowresnx": "LowRes NX",
    "lutro": "Lutro",
    "mastersystem": "Sega Master System",
    "megadrive": "Sega Genesis",
    "model3": "Model 3",
    "msx1": "MSX1",
    "msx2": "MSX2",
    "msxturbor": "MSX Turbo R",
    "multivision": "Multivision",
    "n64": "Nintendo 64",
    "naomigd": "Naomi GD",
    "naomi": "Naomi",
    "neogeocd": "Neo Geo CD",
    "neogeo": "Neo Geo",
    "nes": "Nintendo Entertainment System",
    "ngpc": "Neo Geo Pocket Color",
    "ngp": "Neo Geo Pocket",
    "o2em": "O2EM",
    "oricatmos": "Oric Atmos",
    "pcenginecd": "PC Engine CD",
    "pcengine": "PC Engine",
    "pcfx": "PC-FX",
    "pcv2": "PCV2",
    "pokemini": "Pokemini",
    "ports": "Ports",
    "samcoupe": "Sam Coupe",
    "satellaview": "Satellaview",
    "scv": "Super Cassette Vision",
    "sega32x": "Sega 32X",
    "sg1000": "SG-1000",
    "snes": "Super Nintendo Entertainment System",
    "solarus": "Solarus",
    "spectravideo": "Spectravideo",
    "sufami": "Sufami Turbo",
    "supergrafx": "SuperGrafx",
    "supervision": "Supervision",
    "thomson": "Thomson",
    "tic80": "TIC-80",
    "trs80coco": "TRS-80 CoCo",
    "uzebox": "Uzebox",
    "vectrex": "Vectrex",
    "vic20": "Commodore VIC-20",
    "videopacplus": "Videopac Plus",
    "virtualboy": "Virtual Boy",
    "wasm4": "Wasm4",
    "wswanc": "Wonderswan Color",
    "wswan": "Wonderswan",
    "x1": "X1",
    "x68000": "X68000",
    "zx81": "ZX81",
    "zxspectrum images": "ZX Spectrum Images",
    "zxspectrum videos": "ZX Spectrum Videos"
}

def check_windows():
    if platform.system() != 'Windows':
        messagebox.showerror("Error", "This script is intended to run on Windows only. Exiting.")
        sys.exit(1)

# CHECK NETWORK SHARE
print("Checking if the network share is available...")

try:
    subprocess.run(["ping", "-n", "1", "RECALBOX"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Network share found.")
except subprocess.CalledProcessError:
    print("Error: Could not connect to the network share \\RECALBOX.")
    print("Please make sure you are connected to the network and try again.")
    
    # Show a message box
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showerror("Error", "Network Share not found. Please make sure you are connected to the network and try again.")
    sys.exit()

print()

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
    localTempDir = os.path.expandvars(r"%APPDATA%\readycade\temp")

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
    shutil.rmtree(os.path.join(os.environ['APPDATA'], 'readycade', 'rompacks'), ignore_errors=True)

    # Update status label
    update_status("Deleting Temporary Files... Please Wait...")
    print("Deleting Temporary Files... Please Wait...")

    # Sleep for 2 seconds
    time.sleep(2)

    # Clear status label
    status_var.set("")

# Function to extract and copy ROM files
def process_rom(file):
    # Get the base filename (without extension)
    base_filename = os.path.splitext(os.path.basename(file.name))[0]

    # Check if the base filename matches a valid console name
    if base_filename in valid_consoles:
        # Define paths
        appdata_path = os.path.join(os.environ['APPDATA'], 'readycade', 'rompacks')
        temp_path = r'F:\Readycade\TEMP\share\roms'
        #temp_path = r'\RECALBOX\share\roms'
        # Ensure the directories exist
        os.makedirs(appdata_path, exist_ok=True)
        os.makedirs(temp_path, exist_ok=True)

        print("Extracting Files...")

        # Update status label
        update_status("Extracting Files...")

        # Extract using 7-Zip with the global password
        extract_command = '7z x -p{} "{}" -o"{}"'.format(global_password, file.name, appdata_path)
        subprocess.run(extract_command, shell=True)

        # Clear status label
        status_var.set("")

        # Update status label
        update_status(f"Copying {valid_consoles[base_filename]} to your Readycade...")

        print(f"Copying {valid_consoles[base_filename]} to your Readycade...")

        # Copy the extracted contents to the destination directory
        destination_path = os.path.join(temp_path, base_filename)
        shutil.copytree(appdata_path, destination_path, dirs_exist_ok=True)



        # Update status label
        update_status("Success. Please Update your Gameslist Now.")

        # Show messagebox
        messagebox.showinfo("Success", f"Extraction and Copying completed for {valid_consoles[base_filename]}. Remember to Update your Gamelists.")

        # Cleanup function
        cleanup()
    else:
        # Display an error message for an invalid console name
        messagebox.showerror("Error", "Invalid console name. Please use a valid console name eg: n64, amiga600 etc.")

# Function to handle opening a ROM file
def open_rom_file():
    browse_text.set("loading...")

    # Update the GUI more frequently during the process
    def update_gui():
        root.update_idletasks()
        root.after(100, update_gui)

    update_gui()  # Start updating the GUI

    file = askopenfile(parent=root, mode='rb', title="Choose a ROM Pack (.zip or .7z only)", filetype=[("ZIP files", "*.zip;*.7z")])
    if file:
        process_rom(file)

    # Set button text back to "Browse" regardless of whether a file was selected or not
    browse_text.set("Browse")

# Set up the main window
root = tk.Tk()

# set the window title
root.title("Readycade™")

# Remove the TK icon
root.iconbitmap(default="icon.ico")

# Instructions
Instructions = tk.Label(root, text="Select a ROM Pack on your computer to install to your Readycade", font="open-sans")
Instructions.grid(columnspan=3, column=0, row=1)

# Logo
logo = Image.open('logo.png')
logo = ImageTk.PhotoImage(logo)
logo_label = tk.Label(image=logo)
logo_label.image = logo
logo_label.grid(column=1, row=0)

# Status label
status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var, font="open-sans")
status_label.grid(columnspan=3, column=0, row=4)

# Browse Button
browse_text = tk.StringVar()
browse_btn = tk.Button(root, textvariable=browse_text, command=open_rom_file, font="open-sans", bg="#ff6600", fg="white", height=2, width=15)
browse_text.set("Browse")
browse_btn.grid(column=1, row=2)

root.mainloop()
