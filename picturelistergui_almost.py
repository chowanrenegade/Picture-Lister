import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def process_images(folder_path, save_path, progress_bar, root):
    try:
        files = os.listdir(folder_path)
        # Expanded extension list to be more comprehensive
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff')
        image_files = [f for f in files if f.lower().endswith(image_extensions)]
        
        if not image_files:
            return "No image files found in the selected folder."

        image_file_names = set()
        total_files = len(image_files)
        progress_bar['maximum'] = total_files
        
        for i, file in enumerate(image_files):
            # Extract name without extension
            base_name = os.path.splitext(file)[0]
            # Remove suffixes like (1), [1], -1, or - 1 (limited to 1-2 digits to avoid cropping legitimate parts)
            base_name = re.sub(r'\s*[\(\[]\d{1,2}[\)\]]\s*$|\s*-\d{1,2}$', '', base_name)
            image_file_names.add(base_name)
            
            # Update Progress
            progress_bar['value'] = i + 1
            if i % 5 == 0: # Smooth UI updates
                root.update_idletasks()

        # Write to the chosen save path
        with open(save_path, 'w', encoding='utf-8') as f:
            for name in sorted(image_file_names):
                f.write(name + '\n')

        return f"Success! Created list with {len(image_file_names)} unique items."
    
    except Exception as e:
        return f"An error occurred: {e}"

def run_workflow():
    # 1. Select Source Folder
    folder = filedialog.askdirectory(title="Select Folder Containing Images")
    if not folder:
        return

    # 2. Select Destination and Filename
    save_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        initialfile="image_list.txt",
        title="Save List As"
    )
    if not save_path:
        return

    # 3. Process
    status_label.config(text="Processing...", fg="blue")
    progress['value'] = 0
    
    result = process_images(folder, save_path, progress, root)
    
    status_label.config(text=result, fg="green" if "Success" in result else "red")
    if "Success" in result:
        messagebox.showinfo("Done", result)

# --- GUI Setup ---
root = tk.Tk()
root.title("Picture Lister Pro")
root.geometry("500x350") # Wide and clean

main_frame = tk.Frame(root, padx=30, pady=30)
main_frame.pack(expand=True, fill="both")

tk.Label(main_frame, text="Image List Generator", font=("Segoe UI", 16, "bold")).pack(pady=(0, 20))

instructions = tk.Label(main_frame, 
    text="Click the button below to select your image folder.\nYou will then be asked where to save the text file.",
    justify="center", font=("Segoe UI", 10))
instructions.pack(pady=10)

# Progress Bar
progress = ttk.Progressbar(main_frame, orient="horizontal", length=350, mode="determinate")
progress.pack(pady=20)

# Run button
run_button = tk.Button(main_frame, text="Select Folder & Start", 
                       command=run_workflow, bg="#0078D7", fg="white", 
                       font=("Segoe UI", 11, "bold"), padx=20, pady=10)
run_button.pack(pady=10)

# Status label
status_label = tk.Label(main_frame, text="Waiting for input...", font=("Segoe UI", 9, "italic"))
status_label.pack(pady=10)

root.mainloop()