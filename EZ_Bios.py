import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
from PIL import Image, ImageTk
from tkinter.filedialog import askopenfile
import subprocess
import shutil

root = tk.Tk()

# set the window title
root.title("Readycade™")

# Remove the TK icon
root.iconbitmap(default="icon.ico")

# Logo
logo = Image.open('logo.png')
logo = ImageTk.PhotoImage(logo)
logo_label = tk.Label(image=logo)
logo_label.image = logo
logo_label.grid(column=1, row=0)

# Instructions
Instructions = tk.Label(root, text="Select a Bios file on your computer to install to your Readycade", font="open-sans")
Instructions.grid(columnspan=3, column=0, row=1)

# Status label
status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var, font="open-sans")
status_label.grid(columnspan=3, column=0, row=4)

# Function to update the status label
def update_status(message):
    status_var.set(message)
    root.update_idletasks()

# Function to perform cleanup
def cleanup():
    # Clean up downloaded and extracted files
    shutil.rmtree(os.path.join(os.environ['APPDATA'], 'readycade', 'biospacks'), ignore_errors=True)
    
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
            temp_path = r'F:\Readycade\TEMP\share'

            # Ensure the directories exist
            os.makedirs(appdata_path, exist_ok=True)
            os.makedirs(temp_path, exist_ok=True)

            # Extract using 7-Zip (adjust the path to 7z.exe accordingly)
            extract_command = '7z x "{}" -o"{}"'.format(file.name, appdata_path)

            subprocess.run(extract_command, shell=True)

            # Update status label
            update_status("Extracting Files...")

            # Copy the extracted contents to the destination directory
            shutil.copytree(appdata_path, temp_path, dirs_exist_ok=True)

            # Update status label
            update_status("Copying to Files to your Readycade...")

            # Show messagebox
            messagebox.showinfo("Success", "Extraction and Copying completed. Please reboot your Readycade now.")

            # Update status label
            update_status("Success. Please reboot your Readycade now.")

            # Cleanup function
            cleanup()

        else:
            print("Selected file does not contain 'recalbox' in the name.")

    # Set button text back to "Browse" regardless of whether a file was selected or not
    browse_text.set("Browse")

# Browse Button
browse_text = tk.StringVar()
browse_btn = tk.Button(root, textvariable=browse_text, command=open_file, font="open-sans", bg="#ff6600", fg="white", height=2, width=15)
browse_text.set("Browse")
browse_btn.grid(column=1, row=2)

canvas = tk.Canvas(root, width=720, height=250)
canvas.grid(columnspan=3)

# Remove the TK icon
root.iconbitmap(default="")

root.mainloop()