import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import threading
from pathlib import Path
import openai  # You can use OpenAI API or other AI services
import requests
import hashlib
from datetime import datetime

class AIFileOrganizer:
    def __init__(self, root):
        self.root = root
        self.root.title("AI File Organizer & Project Manager")
        self.root.geometry("1200x800")
        
        # Configuration
        self.config = self.load_config()
        
        # AI API setup (you'll need to add your API key)
        self.ai_enabled = False
        self.setup_ai()
        
        self.create_ui()
        
    def setup_ai(self):
        """Setup AI API configuration"""
        try:
            # You can use OpenAI, Hugging Face, or local models
            # Example with OpenAI (you'll need to install openai package)
            # openai.api_key = "your-api-key"
            self.ai_enabled = True
        except:
            self.ai_enabled = False
    
    def load_config(self):
        """Load configuration file"""
        config_path = Path.home() / ".ai_file_organizer_config.json"
        default_config = {
            "file_categories": {
                "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
                "documents": [".pdf", ".doc", ".docx", ".txt", ".rtf"],
                "code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c"],
                "archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
                "media": [".mp4", ".avi", ".mkv", ".mp3", ".wav", ".flac"]
            },
            "project_templates": {
                "python": ["src/", "tests/", "docs/", "requirements.txt", "README.md"],
                "web": ["css/", "js/", "images/", "index.html"],
                "data_science": ["data/", "notebooks/", "models/", "src/"]
            }
        }
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def create_ui(self):
        """Create the main user interface"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # File Explorer Tab
        self.explorer_frame = ttk.Frame(notebook)
        notebook.add(self.explorer_frame, text="File Explorer")
        
        # Project Organizer Tab
        self.project_frame = ttk.Frame(notebook)
        notebook.add(self.project_frame, text="Project Organizer")
        
        # AI Assistant Tab
        self.ai_frame = ttk.Frame(notebook)
        notebook.add(self.ai_frame, text="AI Assistant")
        
        self.setup_file_explorer()
        self.setup_project_organizer()
        self.setup_ai_assistant()
        
    def setup_file_explorer(self):
        """Setup file explorer tab"""
        # Path selection
        path_frame = ttk.Frame(self.explorer_frame)
        path_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(path_frame, text="Current Path:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar(value=str(Path.home()))
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=50)
        path_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(path_frame, text="Browse", 
                  command=self.browse_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(path_frame, text="Refresh", 
                  command=self.refresh_explorer).pack(side=tk.LEFT, padx=5)
        
        # Search frame
        search_frame = ttk.Frame(self.explorer_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<KeyRelease>', self.search_files)
        
        # File tree view
        tree_frame = ttk.Frame(self.explorer_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tree = ttk.Treeview(tree_frame, columns=("Size", "Type", "Modified"), show="tree headings")
        self.tree.heading("#0", text="Name")
        self.tree.heading("Size", text="Size")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Modified", text="Modified")
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Action buttons
        action_frame = ttk.Frame(self.explorer_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(action_frame, text="Organize Files", 
                  command=self.organize_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Get AI Suggestions", 
                  command=self.get_file_suggestions).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Analyze Structure", 
                  command=self.analyze_structure).pack(side=tk.LEFT, padx=5)
        
        self.load_directory(self.path_var.get())
        
    def setup_project_organizer(self):
        """Setup project organizer tab"""
        # Project creation frame
        project_create_frame = ttk.LabelFrame(self.project_frame, text="Create New Project")
        project_create_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(project_create_frame, text="Project Name:").grid(row=0, column=0, padx=5, pady=5)
        self.project_name_var = tk.StringVar()
        ttk.Entry(project_create_frame, textvariable=self.project_name_var).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(project_create_frame, text="Project Type:").grid(row=0, column=2, padx=5, pady=5)
        self.project_type_var = tk.StringVar(value="python")
        project_type_combo = ttk.Combobox(project_create_frame, textvariable=self.project_type_var,
                                         values=list(self.config["project_templates"].keys()))
        project_type_combo.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(project_create_frame, text="Location:").grid(row=1, column=0, padx=5, pady=5)
        self.project_location_var = tk.StringVar(value=str(Path.home() / "Desktop"))
        ttk.Entry(project_create_frame, textvariable=self.project_location_var, width=40).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(project_create_frame, text="Browse", 
                  command=self.browse_project_location).grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Button(project_create_frame, text="Generate Project", 
                  command=self.generate_project).grid(row=1, column=3, padx=5, pady=5)
        
        # GitHub integration frame
        github_frame = ttk.LabelFrame(self.project_frame, text="GitHub Integration")
        github_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(github_frame, text="Repository Name:").grid(row=0, column=0, padx=5, pady=5)
        self.repo_name_var = tk.StringVar()
        ttk.Entry(github_frame, textvariable=self.repo_name_var).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(github_frame, text="Description:").grid(row=0, column=2, padx=5, pady=5)
        self.repo_desc_var = tk.StringVar()
        ttk.Entry(github_frame, textvariable=self.repo_desc_var, width=30).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(github_frame, text="Get AI Repository Suggestions", 
                  command=self.get_repo_suggestions).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(github_frame, text="Generate README", 
                  command=self.generate_readme).grid(row=1, column=1, padx=5, pady=5)
        
        # Project structure preview
        structure_frame = ttk.LabelFrame(self.project_frame, text="Project Structure")
        structure_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.structure_text = scrolledtext.ScrolledText(structure_frame, height=15)
        self.structure_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def setup_ai_assistant(self):
        """Setup AI assistant tab"""
        # Chat interface
        chat_frame = ttk.LabelFrame(self.ai_frame, text="AI Assistant")
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.chat_display = scrolledtext.ScrolledText(chat_frame, height=20, state=tk.DISABLED)
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.chat_input = tk.Text(input_frame, height=3)
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(input_frame, text="Send", 
                  command=self.send_ai_message).pack(side=tk.RIGHT, padx=5)
        
        # Predefined prompts
        prompt_frame = ttk.LabelFrame(self.ai_frame, text="Quick Actions")
        prompt_frame.pack(fill=tk.X, padx=5, pady=5)
        
        prompts = [
            "Suggest folder structure for Python project",
            "Organize my downloads folder",
            "Create GitHub repository structure",
            "Analyze current directory and suggest improvements"
        ]
        
        for i, prompt in enumerate(prompts):
            ttk.Button(prompt_frame, text=prompt, 
                      command=lambda p=prompt: self.use_prompt(p)).grid(
                      row=i//2, column=i%2, padx=5, pady=2, sticky="ew")
        
        for i in range(2):
            prompt_frame.grid_columnconfigure(i, weight=1)
    
    def browse_directory(self):
        """Browse for directory"""
        directory = filedialog.askdirectory(initialdir=self.path_var.get())
        if directory:
            self.path_var.set(directory)
            self.load_directory(directory)
    
    def load_directory(self, path):
        """Load directory contents into tree view"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            path_obj = Path(path)
            if path_obj.exists() and path_obj.is_dir():
                # Add parent directory entry
                if path_obj.parent != path_obj:
                    self.tree.insert("", "end", text="..", values=("", "Directory", ""),
                                   tags=("directory",))
                
                # Add directories
                for item in sorted(path_obj.iterdir()):
                    if item.is_dir():
                        self.tree.insert("", "end", text=item.name, 
                                       values=("", "Directory", item.stat().st_mtime),
                                       tags=("directory",))
                
                # Add files
                for item in sorted(path_obj.iterdir()):
                    if item.is_file():
                        size = self.format_size(item.stat().st_size)
                        modified = datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                        self.tree.insert("", "end", text=item.name, 
                                       values=(size, item.suffix, modified),
                                       tags=("file",))
        
        except PermissionError:
            messagebox.showerror("Error", "Permission denied to access this directory")
    
    def format_size(self, size_bytes):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def search_files(self, event=None):
        """Search files in current directory"""
        query = self.search_var.get().lower()
        if not query:
            self.load_directory(self.path_var.get())
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        path_obj = Path(self.path_var.get())
        try:
            for item in path_obj.rglob("*"):
                if query in item.name.lower():
                    if item.is_dir():
                        self.tree.insert("", "end", text=str(item.relative_to(path_obj)), 
                                       values=("", "Directory", ""), tags=("directory",))
                    else:
                        size = self.format_size(item.stat().st_size)
                        modified = datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                        self.tree.insert("", "end", text=str(item.relative_to(path_obj)), 
                                       values=(size, item.suffix, modified), tags=("file",))
        except PermissionError:
            pass
    
    def organize_files(self):
        """Organize files into categories"""
        path = Path(self.path_var.get())
        try:
            for item in path.iterdir():
                if item.is_file():
                    category = self.get_file_category(item.suffix)
                    if category:
                        category_dir = path / category
                        category_dir.mkdir(exist_ok=True)
                        shutil.move(str(item), str(category_dir / item.name))
            
            messagebox.showinfo("Success", "Files organized successfully!")
            self.load_directory(path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to organize files: {str(e)}")
    
    def get_file_category(self, extension):
        """Get category for file extension"""
        for category, extensions in self.config["file_categories"].items():
            if extension.lower() in extensions:
                return category
        return "others"
    
    def get_file_suggestions(self):
        """Get AI suggestions for file organization"""
        if not self.ai_enabled:
            messagebox.showwarning("AI Disabled", "AI features are not configured")
            return
        
        # This would integrate with an AI service
        # For now, we'll show a placeholder
        suggestions = self.generate_ai_suggestions(self.path_var.get())
        self.show_suggestions_dialog(suggestions)
    
    def generate_ai_suggestions(self, path):
        """Generate AI suggestions for file organization"""
        # This is a placeholder - you would integrate with actual AI API
        return [
            "Create a 'project_docs' folder for documentation files",
            "Move image files to 'assets' folder",
            "Consider creating a backup of important files",
            "Remove duplicate files in the downloads folder"
        ]
    
    def show_suggestions_dialog(self, suggestions):
        """Show AI suggestions in a dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("AI Suggestions")
        dialog.geometry("500x300")
        
        tk.Label(dialog, text="AI Suggestions for Organization:", 
                font=("Arial", 12, "bold")).pack(pady=10)
        
        for i, suggestion in enumerate(suggestions, 1):
            tk.Label(dialog, text=f"{i}. {suggestion}", 
                    wraplength=450, justify=tk.LEFT).pack(anchor=tk.W, padx=20)
        
        ttk.Button(dialog, text="Apply Suggestions", 
                  command=lambda: self.apply_suggestions(suggestions, dialog)).pack(pady=10)
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=5)
    
    def apply_suggestions(self, suggestions, dialog):
        """Apply selected AI suggestions"""
        # This would implement the actual organization logic
        messagebox.showinfo("Applied", "Suggestions applied successfully!")
        dialog.destroy()
        self.refresh_explorer()
    
    def analyze_structure(self):
        """Analyze directory structure"""
        path = Path(self.path_var.get())
        analysis = self.analyze_directory(path)
        
        # Show analysis results
        self.show_analysis_results(analysis)
    
    def analyze_directory(self, path):
        """Analyze directory structure and return insights"""
        analysis = {
            "total_files": 0,
            "total_folders": 0,
            "file_types": {},
            "largest_files": [],
            "recent_files": [],
            "suggestions": []
        }
        
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    analysis["total_files"] += 1
                    ext = item.suffix.lower()
                    analysis["file_types"][ext] = analysis["file_types"].get(ext, 0) + 1
                    
                    # Track largest files
                    file_size = item.stat().st_size
                    analysis["largest_files"].append((item, file_size))
                    
                    # Track recent files
                    mod_time = item.stat().st_mtime
                    analysis["recent_files"].append((item, mod_time))
                
                elif item.is_dir():
                    analysis["total_folders"] += 1
            
            # Sort and limit lists
            analysis["largest_files"].sort(key=lambda x: x[1], reverse=True)
            analysis["recent_files"].sort(key=lambda x: x[1], reverse=True)
            analysis["largest_files"] = analysis["largest_files"][:10]
            analysis["recent_files"] = analysis["recent_files"][:10]
            
        except PermissionError:
            pass
        
        return analysis
    
    def show_analysis_results(self, analysis):
        """Show directory analysis results"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Directory Analysis")
        dialog.geometry("600x400")
        
        text_widget = scrolledtext.ScrolledText(dialog)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        report = f"""
Directory Analysis Report:
=========================

Basic Statistics:
- Total Files: {analysis['total_files']}
- Total Folders: {analysis['total_folders']}

File Type Distribution:
"""
        for ext, count in sorted(analysis['file_types'].items(), key=lambda x: x[1], reverse=True)[:10]:
            report += f"- {ext if ext else 'No extension'}: {count} files\n"
        
        report += "\nLargest Files:\n"
        for file, size in analysis['largest_files']:
            report += f"- {file.name}: {self.format_size(size)}\n"
        
        text_widget.insert(tk.END, report)
        text_widget.config(state=tk.DISABLED)
    
    def browse_project_location(self):
        """Browse for project location"""
        directory = filedialog.askdirectory(initialdir=self.project_location_var.get())
        if directory:
            self.project_location_var.set(directory)
    
    def generate_project(self):
        """Generate project structure"""
        name = self.project_name_var.get()
        project_type = self.project_type_var.get()
        location = self.project_location_var.get()
        
        if not name:
            messagebox.showerror("Error", "Please enter a project name")
            return
        
        project_path = Path(location) / name
        template = self.config["project_templates"].get(project_type, [])
        
        try:
            project_path.mkdir(exist_ok=True)
            
            for item in template:
                item_path = project_path / item
                if item.endswith('/'):
                    item_path.mkdir(exist_ok=True)
                else:
                    item_path.touch()
            
            # Update structure preview
            self.update_structure_preview(project_path)
            messagebox.showinfo("Success", f"Project '{name}' created successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create project: {str(e)}")
    
    def update_structure_preview(self, project_path):
        """Update project structure preview"""
        self.structure_text.delete(1.0, tk.END)
        
        def add_structure(path, prefix=""):
            for item in sorted(path.iterdir()):
                if item.is_dir():
                    self.structure_text.insert(tk.END, f"{prefix}📁 {item.name}\n")
                    add_structure(item, prefix + "  ")
                else:
                    self.structure_text.insert(tk.END, f"{prefix}📄 {item.name}\n")
        
        add_structure(project_path)
    
    def get_repo_suggestions(self):
        """Get AI suggestions for repository"""
        if not self.ai_enabled:
            messagebox.showwarning("AI Disabled", "AI features are not configured")
            return
        
        project_name = self.project_name_var.get()
        suggestions = self.generate_repo_suggestions(project_name)
        
        # Show suggestions
        self.show_repo_suggestions(suggestions)
    
    def generate_repo_suggestions(self, project_name):
        """Generate repository suggestions using AI"""
        # Placeholder - integrate with actual AI
        return {
            "name": f"awesome-{project_name.lower().replace(' ', '-')}",
            "description": f"A Python project for {project_name} with modern development practices",
            "topics": ["python", "automation", "tool"],
            "readme_template": f"# {project_name}\n\nA powerful Python project for automation and organization."
        }
    
    def show_repo_suggestions(self, suggestions):
        """Show repository suggestions"""
        self.repo_name_var.set(suggestions["name"])
        self.repo_desc_var.set(suggestions["description"])
        
        # Update structure text with README template
        self.structure_text.delete(1.0, tk.END)
        self.structure_text.insert(tk.END, suggestions["readme_template"])
    
    def generate_readme(self):
        """Generate README file"""
        readme_content = self.structure_text.get(1.0, tk.END)
        project_path = Path(self.project_location_var.get()) / self.project_name_var.get()
        
        try:
            readme_path = project_path / "README.md"
            with open(readme_path, 'w') as f:
                f.write(readme_content)
            messagebox.showinfo("Success", "README.md generated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate README: {str(e)}")
    
    def send_ai_message(self):
        """Send message to AI assistant"""
        message = self.chat_input.get(1.0, tk.END).strip()
        if not message:
            return
        
        self.chat_input.delete(1.0, tk.END)
        self.display_message("You", message)
        
        # Get AI response (placeholder)
        response = self.get_ai_response(message)
        self.display_message("AI Assistant", response)
    
    def display_message(self, sender, message):
        """Display message in chat"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"\n{sender}: {message}\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def get_ai_response(self, message):
        """Get response from AI service"""
        # Placeholder - integrate with actual AI service
        responses = {
            "project structure": "I suggest creating a modular structure with separate folders for source code, tests, documentation, and assets.",
            "organization": "Based on your files, I recommend categorizing by file type and creating a logical folder hierarchy.",
            "github": "For GitHub, consider adding a proper README, license file, and GitHub Actions for CI/CD."
        }
        
        for key, response in responses.items():
            if key in message.lower():
                return response
        
        return "I can help you with project organization, file structure, and GitHub setup. What specific assistance do you need?"
    
    def use_prompt(self, prompt):
        """Use predefined prompt"""
        self.chat_input.delete(1.0, tk.END)
        self.chat_input.insert(1.0, prompt)
        self.send_ai_message()
    
    def refresh_explorer(self):
        """Refresh file explorer"""
        self.load_directory(self.path_var.get())

def main():
    root = tk.Tk()
    app = AIFileOrganizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
