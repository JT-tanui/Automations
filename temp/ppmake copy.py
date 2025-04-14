import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk, font
from PIL import Image, ImageTk
import pdf2image
import tempfile
from pptx import Presentation
from pptx.util import Inches
import img2pdf
import threading
import shutil
from pathlib import Path
import sys

class ModernUI:
    """UI styles and helpers for modern appearance"""
    
    # Color scheme
    PRIMARY = "#1a73e8"  # Blue
    SECONDARY = "#4285f4"  # Light blue
    BACKGROUND = "#f8f9fa"  # Light gray
    TEXT = "#202124"  # Dark gray
    ACCENT = "#fbbc04"  # Yellow
    SUCCESS = "#34a853"  # Green
    ERROR = "#ea4335"  # Red
    
    @staticmethod
    def setup_styles():
        """Configure ttk styles for modern appearance"""
        style = ttk.Style()
        
        # Configure TButton style
        style.configure("TButton", 
                        background=ModernUI.PRIMARY, 
                        foreground="white", 
                        padding=6,
                        font=("Segoe UI", 10))
        
        # Create accent button style
        style.configure("Accent.TButton", 
                        background=ModernUI.ACCENT,
                        foreground="white")
        
        # Configure TLabel style
        style.configure("TLabel",
                        background=ModernUI.BACKGROUND,
                        foreground=ModernUI.TEXT,
                        font=("Segoe UI", 10))
        
        # Configure TFrame style
        style.configure("TFrame",
                        background=ModernUI.BACKGROUND)
        
        # Configure TNotebook style
        style.configure("TNotebook",
                        background=ModernUI.BACKGROUND,
                        tabmargins=[2, 5, 2, 0])
        
        style.configure("TNotebook.Tab",
                        background=ModernUI.BACKGROUND,
                        foreground=ModernUI.TEXT,
                        padding=[12, 4],
                        font=("Segoe UI", 10))
        
        style.map("TNotebook.Tab",
                  background=[("selected", ModernUI.PRIMARY)],
                  foreground=[("selected", "white")])
        
        # Configure Listbox style - handled in direct widget config
        return style

class PDFToPPTConverter:
    def __init__(self, root=None):
        self.pdf_files = []
        self.image_files = []
        self.temp_dir = tempfile.mkdtemp()
        
        # Find poppler path - more robust handling
        self.poppler_path = self._find_poppler_path()
        
        # Set up UI
        if root:
            self.root = root
        else:
            self.root = tk.Tk()
            self.root.title("Document Converter Pro")
            self.root.geometry("800x600")
            self.root.minsize(700, 500)
            
            # Set app icon if available
            try:
                icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.ico")
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
            except:
                pass
            
            # Configure background
            self.root.configure(bg=ModernUI.BACKGROUND)
            
            # Apply modern styling
            self.style = ModernUI.setup_styles()
            
            self.setup_ui()
    
    def _find_poppler_path(self):
        """Find the poppler path across multiple potential locations"""
        # List of potential Poppler locations
        poppler_paths = [
            r"C:\tools\poppler-24.08.0\Library\bin",
            r"C:\Program Files\poppler\bin",
            r"C:\Program Files (x86)\poppler\bin",
            r"C:\poppler\bin"
        ]
        
        # Check if path exists in environment
        if 'POPPLER_PATH' in os.environ:
            poppler_paths.insert(0, os.environ['POPPLER_PATH'])
        
        # Find the first valid path
        for path in poppler_paths:
            if os.path.exists(path):
                return path
        
        # Return default even if it doesn't exist
        return poppler_paths[0]
    
    def setup_ui(self):
        """Set up the main UI components"""
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create header with logo and title
        self.setup_header()
        
        # Create a notebook with tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create tabs
        self.ppt_tab = ttk.Frame(self.notebook)
        self.pdf_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.ppt_tab, text="PDF to PowerPoint")
        self.notebook.add(self.pdf_tab, text="Images to PDF")
        self.notebook.add(self.settings_tab, text="Settings")
        
        # Add status bar
        self.setup_status_bar()
        
        # Set up each tab
        self.setup_ppt_tab()
        self.setup_pdf_tab()
        self.setup_settings_tab()
    
    def setup_header(self):
        """Set up the application header"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Try to load logo
        try:
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
            if os.path.exists(logo_path):
                logo_image = Image.open(logo_path).resize((40, 40), Image.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_image)
                logo_label = ttk.Label(header_frame, image=logo_photo)
                logo_label.image = logo_photo  # Keep reference
                logo_label.pack(side=tk.LEFT, padx=(0, 10))
        except:
            pass
        
        title_label = ttk.Label(header_frame, text="Document Converter Pro", 
                              font=("Segoe UI", 16, "bold"),
                              foreground=ModernUI.PRIMARY)
        title_label.pack(side=tk.LEFT, padx=5)
        
        version_label = ttk.Label(header_frame, text="v2.0",
                                font=("Segoe UI", 10),
                                foreground=ModernUI.TEXT)
        version_label.pack(side=tk.LEFT, padx=5)
        
        # Help button
        help_button = ttk.Button(header_frame, text="?", width=3,
                              command=self.show_help,
                              style="Accent.TButton")
        help_button.pack(side=tk.RIGHT, padx=5)
    
    def setup_status_bar(self):
        """Create status bar at bottom of window"""
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        status_label = ttk.Label(status_frame, textvariable=self.status_var, anchor=tk.W)
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.progress_var = tk.IntVar()
        self.progress = ttk.Progressbar(status_frame, orient=tk.HORIZONTAL, 
                                     length=150, mode='determinate', 
                                     variable=self.progress_var)
        self.progress.pack(side=tk.RIGHT, padx=5)
    
    def setup_ppt_tab(self):
        """Set up the PowerPoint tab UI with better layout"""
        # Create frames with proper padding and borders
        top_frame = ttk.Frame(self.ppt_tab)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # File list frame with border and better styling
        list_frame = ttk.Frame(self.ppt_tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        button_frame = ttk.Frame(self.ppt_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Top frame buttons with icons (would be ideal)
        select_folder_btn = ttk.Button(top_frame, text="Select Default Folder", 
                                     command=self.select_default_folder)
        select_folder_btn.pack(side=tk.LEFT, padx=5)
        
        select_files_btn = ttk.Button(top_frame, text="Select Files", 
                                    command=self.select_pdf_files)
        select_files_btn.pack(side=tk.LEFT, padx=5)
        
        # Add sort button
        sort_btn = ttk.Button(top_frame, text="Sort Files", 
                           command=lambda: self.sort_files("ppt"))
        sort_btn.pack(side=tk.LEFT, padx=5)
        
        # File List with better styling
        list_label = ttk.Label(list_frame, text="Selected Files (PDFs and Images):")
        list_label.pack(anchor=tk.W, padx=5, pady=(0, 5))
        
        # Create a frame for the listbox to add border
        listbox_container = ttk.Frame(list_frame, borderwidth=1, relief="solid")
        listbox_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a frame for the listbox and scrollbar
        listbox_frame = ttk.Frame(listbox_container)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.pdf_listbox = tk.Listbox(listbox_frame, 
                                     background="white",
                                     font=("Segoe UI", 10),
                                     selectbackground=ModernUI.PRIMARY,
                                     selectforeground="white",
                                     activestyle="none")
        self.pdf_listbox.pack(fill=tk.BOTH, expand=True)
        
        self.pdf_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.pdf_listbox.yview)
        
        # Add right-click menu
        self.create_context_menu(self.pdf_listbox, "ppt")
        
        # Button frame with better organization
        remove_btn = ttk.Button(button_frame, text="Remove Selected", 
                              command=self.remove_selected)
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(button_frame, text="Clear All", 
                             command=self.clear_all)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Add preview button
        preview_btn = ttk.Button(button_frame, text="Preview Selected", 
                               command=lambda: self.preview_file("ppt"))
        preview_btn.pack(side=tk.LEFT, padx=5)
        
        # Make generate button stand out
        generate_btn = ttk.Button(button_frame, text="Generate PowerPoint", 
                                command=self.generate_ppt, 
                                style="Accent.TButton")
        generate_btn.pack(side=tk.RIGHT, padx=5)
    
    def setup_pdf_tab(self):
        """Set up the PDF tab UI with better layout"""
        # Create frames with proper padding and borders
        top_frame = ttk.Frame(self.pdf_tab)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # File list frame with border and better styling
        list_frame = ttk.Frame(self.pdf_tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        button_frame = ttk.Frame(self.pdf_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Top frame buttons with icons (would be ideal)
        select_images_btn = ttk.Button(top_frame, text="Select Images", 
                                     command=self.select_images)
        select_images_btn.pack(side=tk.LEFT, padx=5)
        
        select_folder_btn = ttk.Button(top_frame, text="Select Folder", 
                                     command=self.select_images_folder)
        select_folder_btn.pack(side=tk.LEFT, padx=5)
        
        # Add sort button
        sort_btn = ttk.Button(top_frame, text="Sort Files", 
                           command=lambda: self.sort_files("pdf"))
        sort_btn.pack(side=tk.LEFT, padx=5)
        
        # File List with better styling
        list_label = ttk.Label(list_frame, text="Selected Images:")
        list_label.pack(anchor=tk.W, padx=5, pady=(0, 5))
        
        # Create a frame for the listbox to add border
        listbox_container = ttk.Frame(list_frame, borderwidth=1, relief="solid")
        listbox_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a frame for the listbox and scrollbar
        listbox_frame = ttk.Frame(listbox_container)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.image_listbox = tk.Listbox(listbox_frame, 
                                      background="white",
                                      font=("Segoe UI", 10),
                                      selectbackground=ModernUI.PRIMARY,
                                      selectforeground="white",
                                      activestyle="none")
        self.image_listbox.pack(fill=tk.BOTH, expand=True)
        
        self.image_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.image_listbox.yview)
        
        # Add right-click menu
        self.create_context_menu(self.image_listbox, "pdf")
        
        # Button frame with better organization
        remove_btn = ttk.Button(button_frame, text="Remove Selected", 
                              command=self.remove_selected_image)
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(button_frame, text="Clear All", 
                             command=self.clear_all_images)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Add preview button
        preview_btn = ttk.Button(button_frame, text="Preview Selected", 
                               command=lambda: self.preview_file("pdf"))
        preview_btn.pack(side=tk.LEFT, padx=5)
        
        # PDF options frame
        options_frame = ttk.LabelFrame(button_frame, text="PDF Options")
        options_frame.pack(side=tk.RIGHT, padx=10, pady=5, fill=tk.Y)
        
        # PDF quality option
        self.pdf_quality_var = tk.StringVar(value="high")
        quality_frame = ttk.Frame(options_frame)
        quality_frame.pack(padx=5, pady=2)
        
        ttk.Label(quality_frame, text="Quality:").pack(side=tk.LEFT)
        ttk.Radiobutton(quality_frame, text="High", variable=self.pdf_quality_var, 
                      value="high").pack(side=tk.LEFT)
        ttk.Radiobutton(quality_frame, text="Medium", variable=self.pdf_quality_var, 
                      value="medium").pack(side=tk.LEFT)
        
        # Make generate button stand out
        generate_btn = ttk.Button(button_frame, text="Generate PDF", 
                                command=self.generate_pdf,
                                style="Accent.TButton")
        generate_btn.pack(side=tk.RIGHT, padx=5)
    
    def setup_settings_tab(self):
        """Set up the Settings tab UI"""
        # Create a frame for settings
        settings_frame = ttk.Frame(self.settings_tab)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Poppler path setting
        poppler_frame = ttk.LabelFrame(settings_frame, text="Poppler Path Configuration")
        poppler_frame.pack(fill=tk.X, pady=10)
        
        self.poppler_path_var = tk.StringVar(value=self.poppler_path)
        
        poppler_entry_frame = ttk.Frame(poppler_frame)
        poppler_entry_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(poppler_entry_frame, text="Poppler Path:").pack(side=tk.LEFT, padx=(0, 5))
        poppler_entry = ttk.Entry(poppler_entry_frame, textvariable=self.poppler_path_var, width=50)
        poppler_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        browse_btn = ttk.Button(poppler_entry_frame, text="Browse",
                             command=self.browse_poppler_path)
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        # Validate and test poppler
        poppler_status_frame = ttk.Frame(poppler_frame)
        poppler_status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.poppler_status_var = tk.StringVar(value="Status: Not Tested")
        ttk.Label(poppler_status_frame, textvariable=self.poppler_status_var).pack(side=tk.LEFT)
        
        test_btn = ttk.Button(poppler_status_frame, text="Test Poppler",
                           command=self.test_poppler)
        test_btn.pack(side=tk.LEFT, padx=5)
        
        # Default output folder setting
        output_frame = ttk.LabelFrame(settings_frame, text="Output Folder Settings")
        output_frame.pack(fill=tk.X, pady=10)
        
        self.output_path_var = tk.StringVar(value=os.path.join(os.getcwd(), "output"))
        
        output_entry_frame = ttk.Frame(output_frame)
        output_entry_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(output_entry_frame, text="Default Output:").pack(side=tk.LEFT, padx=(0, 5))
        output_entry = ttk.Entry(output_entry_frame, textvariable=self.output_path_var, width=50)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        output_browse_btn = ttk.Button(output_entry_frame, text="Browse",
                                    command=self.browse_output_path)
        output_browse_btn.pack(side=tk.LEFT, padx=5)
        
        # Save settings
        save_frame = ttk.Frame(settings_frame)
        save_frame.pack(fill=tk.X, pady=20)
        
        save_btn = ttk.Button(save_frame, text="Save Settings",
                           command=self.save_settings,
                           style="Accent.TButton")
        save_btn.pack(side=tk.RIGHT)
    
    def create_context_menu(self, listbox, tab_type):
        """Create a right-click context menu for a listbox"""
        context_menu = tk.Menu(listbox, tearoff=0)
        
        context_menu.add_command(label="Preview", 
                                 command=lambda: self.preview_selected_file(listbox, tab_type))
        context_menu.add_command(label="Remove", 
                                 command=lambda: self.remove_selected_item(listbox, tab_type))
        context_menu.add_separator()
        context_menu.add_command(label="Move Up", 
                                 command=lambda: self.move_item_up(listbox, tab_type))
        context_menu.add_command(label="Move Down", 
                                 command=lambda: self.move_item_down(listbox, tab_type))
        
        # Bind right-click to show the context menu
        listbox.bind("<Button-3>", lambda event: self.show_context_menu(event, context_menu))
        
        # Double-click to preview
        listbox.bind("<Double-1>", lambda event: self.preview_selected_file(listbox, tab_type))
    
    def show_context_menu(self, event, menu):
        """Show the context menu at the cursor position"""
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def preview_selected_file(self, listbox, tab_type):
        """Preview the selected file"""
        selection = listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        if tab_type == "ppt":
            file_path = self.pdf_files[index]
        else:
            file_path = self.image_files[index]
            
        self.preview_file_at_path(file_path)
    
    def preview_file(self, tab_type):
        """Preview the selected file in the current tab"""
        if tab_type == "ppt":
            selection = self.pdf_listbox.curselection()
            if not selection:
                messagebox.showinfo("Info", "Please select a file to preview.")
                return
                
            index = selection[0]
            file_path = self.pdf_files[index]
        else:
            selection = self.image_listbox.curselection()
            if not selection:
                messagebox.showinfo("Info", "Please select an image to preview.")
                return
                
            index = selection[0]
            file_path = self.image_files[index]
            
        self.preview_file_at_path(file_path)
    
    def preview_file_at_path(self, file_path):
        """Open a file with the default system viewer"""
        # Use system's default program to open the file
        try:
            # Get file extension
            ext = os.path.splitext(file_path)[1].lower()
            
            # For PDFs, we might want to show first page only
            if ext == '.pdf':
                self.show_pdf_preview(file_path)
            else:
                # For other files, use system default
                os.startfile(file_path) if sys.platform == 'win32' else \
                    os.system(f"xdg-open '{file_path}'")
            
        except Exception as e:
            messagebox.showerror("Preview Error", f"Could not preview file: {str(e)}")
    
    def show_pdf_preview(self, pdf_path):
        """Show a preview of the first page of a PDF"""
        try:
            # Create a top-level window
            preview_window = tk.Toplevel(self.root)
            preview_window.title(f"Preview: {os.path.basename(pdf_path)}")
            preview_window.geometry("800x600")
            
            # Configure the window to be non-resizable and modal
            preview_window.resizable(False, False)
            preview_window.transient(self.root)
            preview_window.grab_set()
            
            # Try to convert the first page of the PDF to an image
            try:
                images = pdf2image.convert_from_path(
                    pdf_path,
                    poppler_path=self.poppler_path,
                    first_page=1,
                    last_page=1,
                    dpi=150
                )
                if images:
                    # Get the first page
                    img = images[0]
                    
                    # Resize if needed to fit the window
                    img = self.resize_image_for_preview(img, 780, 520)
                    
                    # Convert to PhotoImage
                    img_tk = ImageTk.PhotoImage(img)
                    
                    # Display the image
                    img_label = ttk.Label(preview_window, image=img_tk)
                    img_label.image = img_tk  # Keep a reference
                    img_label.pack(padx=10, pady=10)
                    
                    # Add close button
                    close_btn = ttk.Button(preview_window, text="Close", 
                                        command=preview_window.destroy)
                    close_btn.pack(pady=10)
                else:
                    ttk.Label(preview_window, text="Could not load PDF preview.").pack(padx=20, pady=20)
            except Exception as e:
                ttk.Label(preview_window, text=f"Error loading PDF: {str(e)}").pack(padx=20, pady=20)
                
        except Exception as e:
            messagebox.showerror("Preview Error", f"Could not create preview: {str(e)}")
    
    def resize_image_for_preview(self, img, max_width, max_height):
        """Resize an image to fit within max dimensions while preserving aspect ratio"""
        width, height = img.size
        
        # Calculate aspect ratios
        width_ratio = max_width / width
        height_ratio = max_height / height
        
        # Use the smaller ratio to ensure image fits
        ratio = min(width_ratio, height_ratio)
        
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        return img.resize((new_width, new_height), Image.LANCZOS)
    
    def move_item_up(self, listbox, tab_type):
        """Move the selected item up in the list"""
        selection = listbox.curselection()
        if not selection or selection[0] == 0:
            return
            
        index = selection[0]
        
        if tab_type == "ppt":
            # Swap items in the pdf_files list
            self.pdf_files[index], self.pdf_files[index-1] = self.pdf_files[index-1], self.pdf_files[index]
            
            # Update listbox
            item_text = listbox.get(index)
            listbox.delete(index)
            listbox.insert(index-1, item_text)
            listbox.selection_set(index-1)
        else:
            # Swap items in the image_files list
            self.image_files[index], self.image_files[index-1] = self.image_files[index-1], self.image_files[index]
            
            # Update listbox
            item_text = listbox.get(index)
            listbox.delete(index)
            listbox.insert(index-1, item_text)
            listbox.selection_set(index-1)
    
    def move_item_down(self, listbox, tab_type):
        """Move the selected item down in the list"""
        selection = listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        
        if tab_type == "ppt":
            # Check if item is last in the list
            if index == len(self.pdf_files) - 1:
                return
                
            # Swap items in the pdf_files list
            self.pdf_files[index], self.pdf_files[index+1] = self.pdf_files[index+1], self.pdf_files[index]
            
            # Update listbox
            item_text = listbox.get(index)
            listbox.delete(index)
            listbox.insert(index+1, item_text)
            listbox.selection_set(index+1)
        else:
            # Check if item is last in the list
            if index == len(self.image_files) - 1:
                return
                
            # Swap items in the image_files list
            self.image_files[index], self.image_files[index+1] = self.image_files[index+1], self.image_files[index]
            
            # Update listbox
            item_text = listbox.get(index)
            listbox.delete(index)
            listbox.insert(index+1, item_text)
            listbox.selection_set(index+1)
    
    def remove_selected_item(self, listbox, tab_type):
        """Remove the selected item from the list"""
        if tab_type == "ppt":
            self.remove_selected()
        else:
            self.remove_selected_image()
    
    def select_default_folder(self):
        """Look for files in the 'cert' folder or user's preferred folder"""
        cert_folder = os.path.join(os.getcwd(), "cert")
        
        if os.path.exists(cert_folder) and os.path.isdir(cert_folder):
            self.add_files_from_folder(cert_folder)
        else:
            messagebox.showinfo("Info", "The 'cert' folder does not exist. Please select a folder.")
            folder_path = filedialog.askdirectory(title="Select Folder")
            if folder_path:
                self.add_files_from_folder(folder_path)
    
    def add_files_from_folder(self, folder_path):
        """Add all supported files from the specified folder to the list"""
        self.status_var.set(f"Loading files from {os.path.basename(folder_path)}...")
        self.root.update_idletasks()
        
        # Define allowed extensions
        allowed_extensions = ('.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')
        
        try:
            # Find all files with allowed extensions
            new_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
                        if os.path.splitext(f.lower())[1] in allowed_extensions]
            
            if not new_files:
                messagebox.showinfo("Info", "No supported files found in the selected folder.")
                self.status_var.set("Ready")
                return
            
            # Update progress bar
            self.progress_var.set(0)
            total_files = len(new_files)
            
            # Add unique files
            added_count = 0
            for i, file_path in enumerate(new_files):
                # Update progress
                self.progress_var.set(int((i+1) / total_files * 100))
                self.root.update_idletasks()
                
                if file_path not in self.pdf_files:
                    self.pdf_files.append(file_path)
                    self.pdf_listbox.insert(tk.END, os.path.basename(file_path))
                    added_count += 1
            
            self.status_var.set(f"Added {added_count} new files from {os.path.basename(folder_path)}")
            
        except Exception as e:
            self.status_var.set("Error loading files")
            messagebox.showerror("Error", f"Failed to load files: {str(e)}")
        finally:
            self.progress_var.set(0)
    
    def select_pdf_files(self):
        """Open file dialog to select PDF files and images with better handling"""
        file_paths = filedialog.askopenfilenames(
            title="Select Files",
            filetypes=[
                ("All Supported Files", "*.pdf *.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
                ("PDF Files", "*.pdf"),
                ("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
            ]
        )
        
        if not file_paths:
            return
        
        # Update progress bar
        self.progress_var.set(0)
        total_files = len(file_paths)
        
        # Add unique files with progress update
        added_count = 0
        for i, file_path in enumerate(file_paths):
            # Update progress
            self.progress_var.set(int((i+1) / total_files * 100))
            self.root.update_idletasks()
            
            if file_path not in self.pdf_files:
                self.pdf_files.append(file_path)
                self.pdf_listbox.insert(tk.END, os.path.basename(file_path))
                added_count += 1
        
        self.status_var.set(f"Added {added_count} new files")
        self.progress_var.set(0)
    
    def remove_selected(self):
        """Remove selected PDFs from the list with better feedback"""
        selection = self.pdf_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Please select a file to remove.")
            return
        
        # Remove from bottom to top to maintain indices
        for index in sorted(selection, reverse=True):
            del self.pdf_files[index]
            self.pdf_listbox.delete(index)
            
        self.status_var.set(f"Removed {len(selection)} file(s)")
    
    def clear_all(self):
        """Clear all PDFs from the list with confirmation"""
        if not self.pdf_files:
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all files?"):
            self.pdf_files = []
            self.pdf_listbox.delete(0, tk.END)
            self.status_var.set("All files cleared")
    
    def sort_files(self, tab_type):
        """Sort the files alphabetically"""
        if tab_type == "ppt":
            if not self.pdf_files:
                return
                
            # Sort files and get sorted filenames
            sorted_data = sorted(zip(self.pdf_files, [os.path.basename(f) for f in self.pdf_files]), 
                                key=lambda x: x[1].lower())
            sorted_files, sorted_names = zip(*sorted_data)
            
            # Update the list
            self.pdf_files = list(sorted_files)
            self.pdf_listbox.delete(0, tk.END)
            for name in sorted_names:
                self.pdf_listbox.insert(tk.END, name)
                
            self.status_var.set("Files sorted alphabetically")
        else:
            if not self.image_files:
                return
                
            # Sort files and get sorted filenames
            sorted_data = sorted(zip(self.image_files, [os.path.basename(f) for f in self.image_files]), 
                                key=lambda x: x[1].lower())
            sorted_files, sorted_names = zip(*sorted_data)
            
            # Update the list
            self.image_files = list(sorted_files)
            self.image_listbox.delete(0, tk.END)
            for name in sorted_names:
                self.image_listbox.insert(tk.END, name)
                
            self.status_var.set("Images sorted alphabetically")
    
    def generate_ppt(self):
        """Generate PowerPoint from selected PDFs and images with progress tracking"""
        if not self.pdf_files:
            messagebox.showinfo("Info", "Please add at least one file.")
            return
        
        # Ask for output filename
        default_output = os.path.join(self.output_path_var.get(), "presentation.pptx")
        output_file = filedialog.asksaveasfilename(
            title="Save PowerPoint As",
            defaultextension=".pptx",
            initialfile=os.path.basename(default_output),
            initialdir=os.path.dirname(default_output),
            filetypes=[("PowerPoint Presentation", "*.pptx")]
        )
        
        if not output_file:
            return
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Use threading to prevent UI freeze
        threading.Thread(target=self._generate_ppt_thread, 
                        args=(output_file,), 
                        daemon=True).start()
    
    def _generate_ppt_thread(self, output_file):
        """Worker thread for PowerPoint generation"""
        try:
            # Update UI
            self.root.after(0, self.status_var.set, "Creating PowerPoint...")
            self.root.after(0, self.progress_var.set, 0)
            
            # Create presentation
            prs = Presentation()
            
            # Process each file
            total_files = len(self.pdf_files)
            for i, file_path in enumerate(self.pdf_files):
                # Update progress
                progress = int((i / total_files) * 100)
                self.root.after(0, self.progress_var.set, progress)
                self.root.after(0, self.status_var.set, 
                              f"Processing {os.path.basename(file_path)}...")
                
                file_extension = os.path.splitext(file_path)[1].lower()
                
                # Handle based on file type
                if file_extension == '.pdf':
                    self._add_pdf_to_ppt(prs, file_path)
                elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']:
                    self._add_image_to_ppt(prs, file_path)
                else:
                    print(f"Unsupported file type: {file_extension}")
            
            # Save presentation
            self.root.after(0, self.status_var.set, "Saving PowerPoint presentation...")
            self.root.after(0, self.progress_var.set, 90)
            
            prs.save(output_file)
            
            # Show success and return to ready state
            self.root.after(0, self.status_var.set, "PowerPoint created successfully!")
            self.root.after(0, self.progress_var.set, 100)
            self.root.after(2000, self.status_var.set, "Ready")
            self.root.after(2000, self.progress_var.set, 0)
            
            # Show success message
            self.root.after(0, messagebox.showinfo, "Success", 
                          f"PowerPoint created successfully!\nSaved to: {output_file}")
        
        except Exception as e:
            # Show error
            self.root.after(0, self.status_var.set, "Error creating PowerPoint")
            self.root.after(0, self.progress_var.set, 0)
            self.root.after(0, messagebox.showerror, "Error", 
                          f"An error occurred: {str(e)}")
    
    def _add_pdf_to_ppt(self, prs, pdf_path):
        """Convert a PDF page to an image and add it to the presentation"""
        try:
            # Convert PDF to images with higher quality
            images = pdf2image.convert_from_path(
                pdf_path,
                poppler_path=self.poppler_path,
                dpi=300  # Increased DPI for better quality
            )
            
            for img in images:
                # Save image temporarily with better quality
                img_path = os.path.join(self.temp_dir, f"temp_img_{os.path.basename(pdf_path)}_{id(img)}.png")
                img.save(img_path, "PNG", optimize=True)
                
                # Add slide
                slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
                
                # Get slide dimensions
                slide_width = prs.slide_width
                slide_height = prs.slide_height
                
                # Add image to slide - starting position doesn't matter, will be adjusted
                pic = slide.shapes.add_picture(img_path, 0, 0)
                
                # Apply small margin (2.5%) for better visual appearance
                margin_factor = 0.95  # 95% of available space
                max_width = slide_width * margin_factor
                max_height = slide_height * margin_factor
                
                # Calculate scaling to preserve aspect ratio
                width_scale = max_width / pic.width
                height_scale = max_height / pic.height
                scale = min(width_scale, height_scale)
                
                # Apply scaling
                new_width = int(pic.width * scale)
                new_height = int(pic.height * scale)
                pic.width = new_width
                pic.height = new_height
                
                # Center precisely on slide
                pic.left = int((slide_width - new_width) / 2)
                pic.top = int((slide_height - new_height) / 2)
                
                # Clean up temp file
                os.remove(img_path)
                
        except Exception as e:
            error_msg = f"Error processing {os.path.basename(pdf_path)}: {str(e)}"
            print(error_msg)
            raise
    
    # ... additional methods ...
    
    # ... existing methods (like add_image_to_ppt, select_images, etc.) ...
    
    def _add_image_to_ppt(self, prs, image_path):
        """Add an image directly to the presentation"""
        try:
            # Add slide
            slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
            
            # Get slide dimensions
            slide_width = prs.slide_width
            slide_height = prs.slide_height
            
            # Add image to slide
            pic = slide.shapes.add_picture(image_path, 0, 0)
            
            # Apply small margin for better visual appearance
            margin_factor = 0.95  # 95% of available space
            max_width = slide_width * margin_factor
            max_height = slide_height * margin_factor
            
            # Calculate scaling to preserve aspect ratio
            width_scale = max_width / pic.width
            height_scale = max_height / pic.height
            scale = min(width_scale, height_scale)
            
            # Apply scaling
            new_width = int(pic.width * scale)
            new_height = int(pic.height * scale)
            pic.width = new_width
            pic.height = new_height
            
            # Center precisely on slide
            pic.left = int((slide_width - new_width) / 2)
            pic.top = int((slide_height - new_height) / 2)
            
        except Exception as e:
            error_msg = f"Error processing {os.path.basename(image_path)}: {str(e)}"
            print(error_msg)
            raise
    
    def select_images(self):
        """Open file dialog to select image files with improved handling"""
        file_paths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
            ]
        )
        
        if not file_paths:
            return
        
        # Update progress bar
        self.progress_var.set(0)
        total_files = len(file_paths)
        
        # Add unique files
        added_count = 0
        for i, file_path in enumerate(file_paths):
            # Update progress
            self.progress_var.set(int((i+1) / total_files * 100))
            self.root.update_idletasks()
            
            if file_path not in self.image_files:
                self.image_files.append(file_path)
                self.image_listbox.insert(tk.END, os.path.basename(file_path))
                added_count += 1
        
        self.status_var.set(f"Added {added_count} new images")
        self.progress_var.set(0)
    
    def select_images_folder(self):
        """Select folder containing images with progress indicators"""
        folder_path = filedialog.askdirectory(title="Select Folder Containing Images")
        if not folder_path:
            return
        
        self.status_var.set(f"Loading images from {os.path.basename(folder_path)}...")
        self.root.update_idletasks()
        
        # Define allowed image extensions
        allowed_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')
        
        try:
            # Find all image files
            new_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
                        if os.path.splitext(f.lower())[1] in allowed_extensions]
            
            if not new_files:
                messagebox.showinfo("Info", "No image files found in the selected folder.")
                self.status_var.set("Ready")
                return
            
            # Update progress bar
            self.progress_var.set(0)
            total_files = len(new_files)
            
            # Add unique files
            added_count = 0
            for i, file_path in enumerate(new_files):
                # Update progress
                self.progress_var.set(int((i+1) / total_files * 100))
                self.root.update_idletasks()
                
                if file_path not in self.image_files:
                    self.image_files.append(file_path)
                    self.image_listbox.insert(tk.END, os.path.basename(file_path))
                    added_count += 1
            
            self.status_var.set(f"Added {added_count} new images from {os.path.basename(folder_path)}")
            
        except Exception as e:
            self.status_var.set("Error loading images")
            messagebox.showerror("Error", f"Failed to load images: {str(e)}")
        finally:
            self.progress_var.set(0)
    
    def remove_selected_image(self):
        """Remove selected images from the list with feedback"""
        selection = self.image_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Please select an image to remove.")
            return
        
        # Remove from bottom to top to maintain indices
        for index in sorted(selection, reverse=True):
            del self.image_files[index]
            self.image_listbox.delete(index)
            
        self.status_var.set(f"Removed {len(selection)} image(s)")
    
    def clear_all_images(self):
        """Clear all images from the list with confirmation"""
        if not self.image_files:
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all images?"):
            self.image_files = []
            self.image_listbox.delete(0, tk.END)
            self.status_var.set("All images cleared")
    
    def generate_pdf(self):
        """Generate PDF from selected images with threading and progress tracking"""
        if not self.image_files:
            messagebox.showinfo("Info", "Please add at least one image.")
            return
        
        # Ask for output filename
        default_output = os.path.join(self.output_path_var.get(), "output.pdf")
        output_file = filedialog.asksaveasfilename(
            title="Save PDF As",
            defaultextension=".pdf",
            initialfile=os.path.basename(default_output),
            initialdir=os.path.dirname(default_output),
            filetypes=[("PDF Document", "*.pdf")]
        )
        
        if not output_file:
            return
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Use threading to prevent UI freeze
        threading.Thread(target=self._generate_pdf_thread, 
                        args=(output_file,), 
                        daemon=True).start()
    
    def _generate_pdf_thread(self, output_file):
        """Worker thread for PDF generation"""
        try:
            # Update UI
            self.root.after(0, self.status_var.set, "Creating PDF...")
            self.root.after(0, self.progress_var.set, 0)
            
            # Process images based on quality setting
            quality = self.pdf_quality_var.get()
            dpi = 300 if quality == "high" else 150
            
            # Update progress
            self.root.after(0, self.progress_var.set, 20)
            
            # Convert images to PDF
            with open(output_file, "wb") as f:
                # Set PDF options based on quality
                layout_fun = img2pdf.get_layout_fun(
                    pagesize=img2pdf.parse_pagesize("A4"),
                    fit=img2pdf.FitMode.into
                ) if quality == "high" else None
                
                f.write(img2pdf.convert(
                    [file for file in self.image_files],
                    layout_fun=layout_fun
                ))
            
            # Show success and return to ready state
            self.root.after(0, self.status_var.set, "PDF created successfully!")
            self.root.after(0, self.progress_var.set, 100)
            self.root.after(2000, self.status_var.set, "Ready")
            self.root.after(2000, self.progress_var.set, 0)
            
            # Show success message
            self.root.after(0, messagebox.showinfo, "Success", 
                          f"PDF created successfully!\nSaved to: {output_file}")
        
        except Exception as e:
            # Show error
            self.root.after(0, self.status_var.set, "Error creating PDF")
            self.root.after(0, self.progress_var.set, 0)
            self.root.after(0, messagebox.showerror, "Error", 
                          f"An error occurred: {str(e)}")
    
    def browse_poppler_path(self):
        """Browse for poppler path directory"""
        path = filedialog.askdirectory(title="Select Poppler Directory")
        if path:
            self.poppler_path_var.set(path)
    
    def browse_output_path(self):
        """Browse for default output directory"""
        path = filedialog.askdirectory(title="Select Default Output Directory")
        if path:
            self.output_path_var.set(path)
    
    def test_poppler(self):
        """Test if poppler is properly installed and configured"""
        path = self.poppler_path_var.get()
        
        if not os.path.exists(path):
            self.poppler_status_var.set("Status: Path does not exist")
            return
        
        # Check for poppler executables
        pdftoppm_path = os.path.join(path, "pdftoppm.exe" if sys.platform == "win32" else "pdftoppm")
        pdftocairo_path = os.path.join(path, "pdftocairo.exe" if sys.platform == "win32" else "pdftocairo")
        
        if not os.path.exists(pdftoppm_path) and not os.path.exists(pdftocairo_path):
            self.poppler_status_var.set("Status: Poppler executables not found")
            return
            
        self.poppler_status_var.set("Status: Poppler found and valid")
        self.poppler_path = path  # Update the path
    
    def save_settings(self):
        """Save settings to a configuration file"""
        try:
            # Create settings directory if it doesn't exist
            settings_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
            os.makedirs(settings_dir, exist_ok=True)
            
            # Settings file
            settings_file = os.path.join(settings_dir, "settings.txt")
            
            # Write settings
            with open(settings_file, "w") as f:
                f.write(f"poppler_path={self.poppler_path_var.get()}\n")
                f.write(f"output_path={self.output_path_var.get()}\n")
            
            # Update current settings
            self.poppler_path = self.poppler_path_var.get()
            
            messagebox.showinfo("Settings", "Settings saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def load_settings(self):
        """Load settings from configuration file"""
        try:
            # Settings file
            settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "settings.txt")
            
            if not os.path.exists(settings_file):
                return
            
            # Read settings
            with open(settings_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                        
                    parts = line.split("=", 1)
                    if len(parts) != 2:
                        continue
                        
                    key, value = parts
                    
                    if key == "poppler_path" and os.path.exists(value):
                        self.poppler_path = value
                        self.poppler_path_var.set(value)
                    elif key == "output_path":
                        self.output_path_var.set(value)
        except Exception:
            # Silently fail on settings load error
            pass
    
    def show_help(self):
        """Show help dialog"""
        help_text = """Document Converter Pro Help

PDF to PowerPoint:
- Select PDFs and images to add to the presentation
- Arrange the order using drag & drop or right-click menu
- Preview files by double-clicking or right-clicking
- Generate a PowerPoint where each file becomes a slide

Images to PDF:
- Select images to include in the PDF
- Arrange the order as needed
- Choose quality settings 
- Generate a PDF containing all selected images

Settings:
- Set Poppler path for PDF processing
- Configure default output location
- Test and validate your configuration

For more help, refer to the documentation.
"""
        messagebox.showinfo("Help", help_text)
    
    def run(self):
        """Start the application"""
        # Load settings before showing UI
        self.load_settings()
        
        # Create required directories
        os.makedirs(self.output_path_var.get(), exist_ok=True)
        
        # Start the application
        self.root.mainloop()
        
        # Clean up temp directory on exit
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

if __name__ == "__main__":
    converter = PDFToPPTConverter()
    converter.run()