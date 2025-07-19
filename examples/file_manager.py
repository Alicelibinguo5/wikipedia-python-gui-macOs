import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from send2trash import send2trash
import subprocess
import platform
from pathlib import Path
from datetime import datetime

class FileManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced File Manager")
        self.root.geometry("1000x700")
        
        self.files = []
        self.current_directory = Path.home() / "Downloads"
        
        self.setup_ui()
        self.load_downloads()
    
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="📂 Enhanced File Manager", 
                              font=('Helvetica', 16, 'bold'), bg='#f0f0f0')
        title_label.pack(pady=(0, 10))
        
        # Current directory display
        self.dir_label = tk.Label(main_frame, text=f"Current Directory: {self.current_directory}", 
                                 font=('Helvetica', 10), bg='#f0f0f0')
        self.dir_label.pack(pady=(0, 10))
        
        # Content frame (file list + preview)
        content_frame = tk.Frame(main_frame, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # File list frame
        list_frame = tk.LabelFrame(content_frame, text="Files", bg='#f0f0f0', padx=10, pady=10)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # File listbox with scrollbar
        list_container = tk.Frame(list_frame, bg='#f0f0f0')
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.listbox = tk.Listbox(list_container, selectmode=tk.EXTENDED, 
                                 font=('Consolas', 10), height=20)
        scrollbar = tk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection and double-click events
        self.listbox.bind('<<ListboxSelect>>', self.on_file_select)
        self.listbox.bind('<Double-1>', self.on_double_click)
        
        # Preview frame
        preview_frame = tk.LabelFrame(content_frame, text="Preview", bg='#f0f0f0', 
                                     padx=10, pady=10, width=300)
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        preview_frame.pack_propagate(False)  # Maintain fixed width
        
        # Preview canvas
        self.preview_canvas = tk.Canvas(preview_frame, width=270, height=180, bg='white')
        self.preview_canvas.pack(pady=(0, 10))
        
        # File info text
        self.info_text = tk.Text(preview_frame, height=10, width=35, wrap=tk.WORD, 
                                font=('Consolas', 9))
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons frame
        btn_frame = tk.Frame(main_frame, bg='#f0f0f0')
        btn_frame.pack(pady=(10, 0))
        
        # Buttons
        buttons = [
            ("🔄 Refresh", self.load_downloads),
            ("🏠 Home", self.go_home),
            ("⬆️ Parent", self.go_parent),
            ("📂 Move", self.move_files),
            ("🗑 Trash", self.delete_files),
            ("🔍 Open", self.open_files)
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(btn_frame, text=text, command=command, width=15, 
                           font=('Helvetica', 9), relief=tk.RAISED, bd=2)
            btn.grid(row=0, column=i, padx=5, pady=5)
    
    def load_downloads(self):
        if not self.current_directory.exists():
            messagebox.showerror("Error", f"Directory not found: {self.current_directory}")
            return
        
        self.files = []
        self.listbox.delete(0, tk.END)
        
        # Load files and folders from directory
        try:
            items = []
            # First add folders
            for item_path in self.current_directory.iterdir():
                if item_path.is_dir() and not item_path.name.startswith('.'):
                    items.append((item_path, True))  # True for directory
            
            # Then add files
            for item_path in self.current_directory.iterdir():
                if item_path.is_file() and not item_path.name.startswith('.'):
                    items.append((item_path, False))  # False for file
            
            # Sort items: folders first, then files
            items.sort(key=lambda x: (not x[1], x[0].name.lower()))
            
            for item_path, is_dir in items:
                if is_dir:
                    # Add folder to list
                    self.files.append(item_path)
                    display_text = f"📁 {item_path.name:<38} <DIR>"
                    self.listbox.insert(tk.END, display_text)
                else:
                    # Add file to list
                    self.files.append(item_path)
                    
                    # Format file info
                    size = self.format_file_size(item_path.stat().st_size)
                    modified = datetime.fromtimestamp(item_path.stat().st_mtime).strftime('%m/%d %H:%M')
                    
                    # Insert into listbox
                    display_text = f"📄 {item_path.name:<38} {size:>8} {modified}"
                    self.listbox.insert(tk.END, display_text)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load files: {str(e)}")
        
        # Update directory label
        self.dir_label.config(text=f"Current Directory: {self.current_directory} ({len(self.files)} files)")
        
        # Show folder preview by default
        self.show_folder_preview()
    
    def format_file_size(self, size):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"
    
    def on_file_select(self, event):
        """Handle file selection in listbox"""
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.files):
                file_path = self.files[index]
                if file_path.is_dir():
                    self.show_folder_preview(file_path)
                else:
                    self.show_preview(file_path)
        else:
            # If nothing is selected, show the current folder preview
            self.show_folder_preview()
    
    def show_preview(self, file_path):
        """Show file preview in the preview panel"""
        self.clear_preview()
        
        # Show file info
        try:
            stat = file_path.stat()
            info = f"Name: {file_path.name}\\n"
            info += f"Size: {self.format_file_size(stat.st_size)}\\n"
            info += f"Modified: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\\n"
            info += f"Type: {file_path.suffix.upper() or 'File'}\\n"
            info += f"Path: {file_path}"
            
            self.info_text.insert(tk.END, info)
            
            # Try to show image preview for image files
            if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                try:
                    from PIL import Image, ImageTk
                    image = Image.open(file_path)
                    # Resize image to fit preview area
                    image.thumbnail((250, 160), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    
                    # Store reference to prevent garbage collection
                    self._preview_image = photo  # <-- change this line

                    # Clear canvas and add image
                    self.preview_canvas.delete("all")
                    self.preview_canvas.create_image(135, 90, image=photo)
                except Exception as e:
                    self.preview_canvas.delete("all")
                    self.preview_canvas.create_text(135, 90, text=f"Cannot preview\\n{str(e)}", 
                                                   justify=tk.CENTER, font=('Helvetica', 10))
            else:
                # Show file icon or type info
                self.preview_canvas.delete("all")
                self.preview_canvas.create_text(135, 90, text=f"📄\\n{file_path.suffix.upper() or 'FILE'}", 
                                               justify=tk.CENTER, font=('Helvetica', 16))
        except Exception as e:
            self.info_text.insert(tk.END, f"Error loading file info: {str(e)}")
    
    def clear_preview(self):
        """Clear the preview panel"""
        self.preview_canvas.delete("all")
        self.info_text.delete(1.0, tk.END)
    
    def get_selected_files(self):
        """Get selected files from listbox"""
        selected_files = []
        for index in self.listbox.curselection():
            if index < len(self.files):
                selected_files.append(self.files[index])
        return selected_files
    
    def add_files(self):
        paths = filedialog.askopenfilenames()
        for path in paths:
            if Path(path) not in self.files:
                self.files.append(Path(path))
                self.listbox.insert(tk.END, Path(path).name)
    
    def move_files(self):
        selected_files = self.get_selected_files()
        if not selected_files:
            messagebox.showwarning("No Selection", "Please select files to move.")
            return
            
        dest_folder = filedialog.askdirectory(title="Select Destination Folder")
        if not dest_folder:
            return
            
        for file in selected_files:
            try:
                shutil.move(str(file), dest_folder)
            except Exception as e:
                messagebox.showerror("Move Error", str(e))
        
        self.load_downloads()
    
    def delete_files(self):
        selected_files = self.get_selected_files()
        if not selected_files:
            messagebox.showwarning("No Selection", "Please select files to delete.")
            return
            
        if messagebox.askyesno("Confirm Delete", f"Move {len(selected_files)} file(s) to trash?"):
            for file in selected_files:
                try:
                    send2trash(str(file))
                except Exception as e:
                    messagebox.showerror("Delete Error", str(e))
            
            self.load_downloads()
    
    def open_files(self):
        selected_files = self.get_selected_files()
        if not selected_files:
            messagebox.showwarning("No Selection", "Please select files to open.")
            return
            
        for file in selected_files:
            try:
                if platform.system() == "Darwin":
                    subprocess.call(("open", str(file)))
                elif platform.system() == "Windows":
                    os.startfile(str(file))
                else:
                    subprocess.call(("xdg-open", str(file)))
            except Exception as e:
                messagebox.showerror("Open Error", str(e))
    
    def rename_files(self):
        selected_files = self.get_selected_files()
        if not selected_files:
            messagebox.showwarning("No Selection", "Please select files to rename.")
            return
            
        prefix = simpledialog.askstring("Bulk Rename", "Enter prefix (leave empty for none):")
        if prefix is None:
            return
            
        suffix = simpledialog.askstring("Bulk Rename", "Enter suffix (leave empty for none):")
        if suffix is None:
            return
            
        for file in selected_files:
            try:
                name = file.name
                base, ext = os.path.splitext(name)
                new_name = f"{prefix or ''}{base}{suffix or ''}{ext}"
                new_path = file.parent / new_name
                file.rename(new_path)
            except Exception as e:
                messagebox.showerror("Rename Error", str(e))
        
        self.load_downloads()

    def on_double_click(self, event):
        """Handle double-click to navigate into folders"""
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.files):
                file_path = self.files[index]
                if file_path.is_dir():
                    self.current_directory = file_path
                    self.load_downloads()
                else:
                    self.open_files()
    
    def go_home(self):
        """Navigate to Downloads folder"""
        self.current_directory = Path.home() / "Downloads"
        self.load_downloads()
    
    def go_parent(self):
        """Navigate to parent directory"""
        if self.current_directory.parent != self.current_directory:
            self.current_directory = self.current_directory.parent
            self.load_downloads()
    
    def show_folder_preview(self, folder_path=None):
        """Show folder contents preview"""
        if folder_path is None:
            folder_path = self.current_directory
            
        self.clear_preview()
        
        try:
            # Count items in folder
            files = []
            dirs = []
            
            for item in folder_path.iterdir():
                if item.name.startswith('.'):
                    continue
                if item.is_dir():
                    dirs.append(item.name)
                else:
                    files.append(item.name)
            
            # Show folder info
            info = f"Folder: {folder_path.name}\n"
            info += f"Path: {folder_path}\n"
            info += f"Folders: {len(dirs)}\n"
            info += f"Files: {len(files)}\n\n"
            
            if dirs:
                info += "Recent Folders:\n"
                for d in sorted(dirs)[:10]:
                    info += f"  📁 {d}\n"
            
            if files:
                info += "\nRecent Files:\n"
                for f in sorted(files)[:10]:
                    info += f"  📄 {f}\n"
            
            self.info_text.insert(tk.END, info)
            
            # Show folder icon
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(135, 90, text=f"📁\n{len(files)} files\n{len(dirs)} folders", 
                                           justify=tk.CENTER, font=('Helvetica', 14))
            
        except Exception as e:
            self.info_text.insert(tk.END, f"Error reading folder: {str(e)}")
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(135, 90, text=f"📁\nFolder", 
                                           justify=tk.CENTER, font=('Helvetica', 14))

if __name__ == "__main__":
    root = tk.Tk()
    app = FileManagerApp(root)
    root.mainloop()