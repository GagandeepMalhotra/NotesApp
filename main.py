import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from ctypes import windll
import time
import uuid
import json


class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sticky Notes+")
        self.root.geometry("550x550")
        root.iconbitmap("stickynotes+.ico")

        self.notes_filename = "notes.json"
        self.current_note = {"id": str(uuid.uuid4()), "title": "Sticky Notes+ by Gagandeep Malhotra", "content": ""}
        self.notes_list = []
        self.current_note_id = None

        self.create_widgets()

        # Load notes from file on application startup
        self.load_notes_from_file()

        # Check if there are saved notes
        if self.notes_list:

            self.current_note_id = self.get_most_recently_edited_note_id()
            self.load_current_note()

        # Display "Create new note" if no notes exist
        else:
            self.note_text.insert("1.0", "\nCreate a New Note:\nFile > New Note")
            self.note_text.tag_configure("center", justify='center')
            self.note_text.tag_add("center", "1.0", "end")
            self.note_text.config(state="disabled")
        
        # Binding key events
        self.note_text.bind("<Control-b>", lambda event: self.apply_bold())
        #self.note_text.bind("<Control-i>", lambda event: self.apply_italic())
        self.note_text.bind("<Control-u>", lambda event: self.apply_underline())

    def create_widgets(self):
        self.create_menu_bar()
        self.create_bottom_toolbar()
        self.create_main_window()
        

    def create_menu_bar(self):
        menu_bar = tk.Menu(self.root)

        # File Menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Note", command=self.new_note)
        file_menu.add_command(label="Delete Note", command=self.delete_note)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # View Menu
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Notes List", command=self.show_notes_list)
        menu_bar.add_cascade(label="View", menu=view_menu)

        self.root.config(menu=menu_bar)

    def create_main_window(self):
        self.main_frame = tk.Frame(self.root, bg="#333333")
        self.main_frame.pack(expand=True, fill="both", padx=0, pady=0)

        self.title_label = tk.Label(
            self.main_frame, text=self.current_note["title"], font=("Segoe UI", 12), bg="#333333", fg="white"
        )
        self.title_label.pack(anchor="w", padx=15, pady=(10, 0))

        self.note_text = tk.Text(
            self.main_frame, wrap="word", font=("Segoe UI", 12),
            bg="#333333", fg="white", insertbackground="lightgrey",
            highlightthickness=0, borderwidth=0, undo=True, autoseparators=True, maxundo=-1
        )
        self.note_text.pack(side="left", expand=True, fill="both", padx=15, pady=0)
        self.note_text.insert("1.0", self.current_note["content"])
        self.note_text.bind("<KeyRelease>", self.auto_save)
        self.on_focus_out()

    def create_bottom_toolbar(self):
        self.bottom_frame = tk.Frame(self.root, bg="#333333", pady=0)
        self.bottom_frame.pack(side="bottom", fill="x")
        
        separator = tk.Frame(root, bg="#222", height=1, bd=0)
        separator.pack(side="bottom", fill="x")

        self.char_count_label = tk.Label(
            self.bottom_frame, text="Chars: 0", bg="#333333", fg="white", padx=10
        )
        self.char_count_label.pack(side="left")
        
        # Load the search.png image
        search_image = tk.PhotoImage(file="search.png")

        # Create a label to display the image
        search_label = tk.Label(self.bottom_frame, image=search_image, bg="#333333", height=15)
        search_label.image = search_image  # To prevent image from being garbage collected
        search_label.pack(side="left", padx=(5, 2.5))  # Adjust padx as needed
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.bottom_frame, textvariable=self.search_var, bg="#222", fg="white", insertbackground="lightgrey", bd=0, borderwidth=2.49, relief=tk.FLAT, width=8)
        self.search_entry.pack(side="left", padx=(0,5), pady=0, fill="x", ipadx=5)
        self.search_entry.bind("<KeyRelease>", self.search_text)  # Bind the search function to the search bar input change
        self.search_entry.bind("<FocusIn>", lambda event: self.on_entry_click())
        self.search_entry.bind("<FocusOut>", lambda event: self.on_focus_out())

        """
        undo_image = tk.PhotoImage(file="undo.png")
        undo_button = tk.Button(self.bottom_frame, image=undo_image, command=self.undo, bd=0, bg="#222", activebackground="#111")
        undo_button.image = undo_image
        undo_button.pack(side="left", padx=(5, 0), ipadx=4, ipady=4)

        redo_image = tk.PhotoImage(file="redo.png")
        redo_button = tk.Button(self.bottom_frame, image=redo_image, command=self.redo, bd=0, bg="#222", activebackground="#111")
        redo_button.image = redo_image
        redo_button.pack(side="left", padx=(2.5, 2.5), ipadx=4, ipady=4)
        """
        underline_button = tk.Button(self.bottom_frame, text="U", command=self.apply_underline, bd=0, bg="#222", fg="white", activebackground="#111", activeforeground="white", font=('Segoe UI', 9, 'underline'))
        underline_button.pack(side="right", padx=(0,10), ipadx=7)  # No padx needed for the last button

        italic_button = tk.Button(self.bottom_frame, text="I", command=self.apply_italic, bd=0, bg="#222", fg="white", activebackground="#111", activeforeground="white", font=('Segoe UI', 9, 'italic'))
        italic_button.pack(side="right", padx=(2.5, 2.5), ipadx=10)

        bold_button = tk.Button(self.bottom_frame, text="B", command=self.apply_bold, bd=0, bg="#222", fg="white", activebackground="#111", activeforeground="white", font=('Segoe UI', 9, 'bold'))
        bold_button.pack(side="right", padx=(5, 0), ipadx=8)  # Set ipadx to make the button wider
        
        self.transparency_slider = tk.Scale(
            self.bottom_frame, from_=0.1, to=1.0, resolution=0.1, orient="horizontal", bg="#191919", activebackground="#111", length=50,
            command=self.update_transparency, showvalue=0, highlightthickness=0, troughcolor="#222", bd=0, sliderrelief="flat", sliderlength=15
        )
        self.transparency_slider.set(1.0)  # Set default transparency to 1.0 (fully opaque)
        self.transparency_slider.pack(side="right", padx=(0,10))
        
        # Load the opacity.png image
        opacity_image = tk.PhotoImage(file="opacity.png")

        # Create a label to display the image
        opacity_label = tk.Label(self.bottom_frame, image=opacity_image, bg="#333333", height=15)
        opacity_label.image = opacity_image  # To prevent image from being garbage collected
        opacity_label.pack(side="right", padx=(12.5, 2.5))  # Adjust padx as needed
        
        self.zoom_slider = tk.Scale(
            self.bottom_frame, from_=50, to=150, orient="horizontal", bg="#191919", fg="#111", activebackground="#111", length=50,
            command=self.update_zoom, showvalue=0, highlightthickness=0, troughcolor="#222", bd=0, sliderrelief="flat", sliderlength=15
        )
        self.zoom_slider.set(100)  # Set default zoom to 100%
        self.zoom_slider.pack(side="right", padx=(0, 0))
        
        # Load the zoom.png image
        zoom_image = tk.PhotoImage(file="zoom.png")

        # Create a label to display the image
        zoom_label = tk.Label(self.bottom_frame, image=zoom_image, bg="#333333", height=15)
        zoom_label.image = zoom_image  # To prevent image from being garbage collected
        zoom_label.pack(side="right", padx=(10, 2.5)) 
        
        self.margin_slider = tk.Scale(
            self.bottom_frame, from_=0, to=200, orient="horizontal", bg="#191919", fg="#111", activebackground="#111", length=50,
            command=self.update_margin, showvalue=0, highlightthickness=0, troughcolor="#222", bd=0, sliderrelief="flat", sliderlength=15
        )
        self.margin_slider.set(0)  # Set default zoom to 100%
        self.margin_slider.pack(side="right", padx=(0, 0))
        
        # Load the zoom.png image
        margin_image = tk.PhotoImage(file="margin.png")

        # Create a label to display the image
        margin_label = tk.Label(self.bottom_frame, image=margin_image, bg="#333333", height=15)
        margin_label.image = margin_image  # To prevent image from being garbage collected
        margin_label.pack(side="right", padx=(10, 2.5)) 
        
    def new_note(self):
        self.note_text.config(state="normal")
        new_note_title = simpledialog.askstring("New Note", "New Note Title:")
        if new_note_title:
            new_note_id = str(uuid.uuid4())  # Generate a unique ID for the new note
            self.notes_list.append({"id": new_note_id, "title": new_note_title, "content": ""})
            self.current_note_id = new_note_id
            self.load_current_note()

    def delete_note(self):
        confirm_delete = messagebox.askyesno("Delete Note", "Confirm Delete?")
        if confirm_delete:
            note_id_to_delete = self.current_note_id
            self.notes_list = [note for note in self.notes_list if note["id"] != note_id_to_delete]

            if not self.notes_list:
                # If there are no more notes, set the current note to an empty note
                self.current_note = {"id": "", "title": "", "content": ""}
                self.current_note_id = None
            else:
                # Set the current note to the one with the most recent modification time
                self.current_note_id = self.get_most_recently_edited_note_id()
                self.load_current_note()

            self.load_current_note()
            self.save_notes_to_file()
            
    def update_margin(self, value):
        margin_value = float(value)
        padding_x = int(margin_value)  # Adjust the padding based on the margin_slider value
        self.note_text.config(padx=(padding_x), pady=0)
            
    def search_text(self, event=None):
        search_text = self.search_var.get().lower()
        self.note_text.tag_remove("search", "1.0", "end")
        self.note_text.tag_delete("search")

        if search_text:
            start = "1.0"
            found_index = self.note_text.search(search_text, start, stopindex="end", nocase=True)

            while found_index:
                end = f"{found_index}+{len(search_text)}c"
                self.note_text.tag_add("search", found_index, end)
                start = end
                found_index = self.note_text.search(search_text, start, stopindex="end", nocase=True)

            self.note_text.tag_configure("search", background="yellow")
            
            if start:
                self.note_text.see(start)
            
    def undo(self):
        try:
            self.note_text.edit_undo()
            self.update_char_count()
        except tk.TclError:
            pass

    def redo(self):
        try:
            self.note_text.edit_redo()
            self.update_char_count()
        except tk.TclError:
            pass
        
    def on_entry_click(self):
        if self.search_entry.get() == "Find...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.configure(foreground="white", font=('Segoe UI', 9))

    def on_focus_out(self):
        if self.search_entry.get() == "":
            self.search_entry.insert(0, "Find...")
            self.search_entry.configure(foreground="grey", font=('Segoe UI', 9, 'italic'))
        
    def show_notes_list(self):
        notes_list_window = tk.Toplevel(self.root)
        notes_list_window.title("Notes List")
        notes_list_window.iconbitmap("stickynotes+.ico")
        notes_list_window.minsize(225, 150)
        notes_list_window.configure(bg='#333')

        # Disable resizing
        notes_list_window.resizable(False, False)

        notes_listbox = tk.Listbox(notes_list_window, highlightbackground="grey", highlightcolor="grey", highlightthickness=1)
        notes_listbox.configure(bg='#333', fg='white')
        for note in self.notes_list:
            title_with_content = note['title']
            if note['content']:
                title_with_content += f" - {note['content'][:10]}..."
            notes_listbox.insert("end", title_with_content)

        notes_listbox.pack(expand=True, fill="both", padx=10, pady=(10,0),ipadx=10, ipady=10)

        def open_selected_note():
            selected_index = notes_listbox.curselection()
            if selected_index:
                self.current_note_id = self.notes_list[selected_index[0]]["id"]
                self.load_current_note()
                notes_list_window.destroy()

        open_button = tk.Button(notes_list_window, text="Open Note", command=open_selected_note)
        open_button.configure(bg='#333', fg='white', activebackground='#222', activeforeground='white')
        open_button.pack(pady=10, fill="x", padx=10)

    def get_most_recently_edited_note_id(self):
        sorted_notes = sorted(self.notes_list, key=lambda x: x.get('last_modified', 0), reverse=True)
        return sorted_notes[0]['id'] if sorted_notes else None

    def auto_save(self, event):
        self.current_note["content"] = self.note_text.get("1.0", "end-1c")
        self.update_char_count()
        self.current_note['last_modified'] = time.time()
        self.save_notes_to_file()

    def update_char_count(self):
        char_count = len(self.note_text.get("1.0", "end-1c"))
        self.char_count_label.config(text=f"Chars: {char_count}", font=('Segoe UI', 9))
        
    def update_transparency(self, value):
        transparency = float(value)
        self.root.attributes("-alpha", transparency)

    def apply_format(self, tag_name, font_config=None, underline=False):
        if self.note_text.tag_ranges(tk.SEL):
            current_tags = self.note_text.tag_names(tk.SEL_FIRST)
            if tag_name in current_tags:
                self.note_text.tag_remove(tag_name, tk.SEL_FIRST, tk.SEL_LAST)
            else:
                self.note_text.tag_add(tag_name, tk.SEL_FIRST, tk.SEL_LAST)
                if font_config:
                    self.note_text.tag_configure(tag_name, **font_config)
                elif underline:
                    self.note_text.tag_configure(tag_name, underline=True)

    def apply_bold(self):
        self.apply_format("bold", font_config={"font": ("Segoe UI", 12, "bold")})

    def apply_italic(self):
        self.apply_format("italic", font_config={"font": ("Segoe UI", 12, "italic")})
    
    def apply_underline(self):
        self.apply_format("underline", underline=True)
        
    def update_zoom(self, value):
        zoom_level = int(value)
        font_size = int(12 * zoom_level / 100)  # Adjust the base font size (12) based on zoom level
        self.note_text.configure(font=("Segoe UI", font_size))
        
    def load_notes_from_file(self):
        try:
            with open(self.notes_filename, "r") as file:
                data = file.read()
                self.notes_list = json.loads(data)
        except FileNotFoundError:
            pass

    def save_notes_to_file(self):
        with open(self.notes_filename, "w") as file:
            json.dump(self.notes_list, file)

    def load_current_note(self):
        if not self.notes_list:
            self.title_label.config(text="Sticky Notes+ by Gagandeep Malhotra")
            self.note_text.delete("1.0", "end")
            self.note_text.insert("1.0", "\nCreate a New Note:\nFile > New Note")
            self.note_text.tag_configure("center", justify='center')
            self.note_text.tag_add("center", "1.0", "end")
            self.note_text.config(state="disabled")
        else:
            self.current_note = next((note for note in self.notes_list if note["id"] == self.current_note_id), None)
            if self.current_note:
                self.title_label.config(text=self.current_note["title"])
                self.note_text.delete("1.0", "end")
                self.note_text.insert("1.0", self.current_note["content"])
                self.update_char_count()

if __name__ == "__main__":
    windll.shcore.SetProcessDpiAwareness(1)
    root = tk.Tk()
    root.minsize(550, 200)
    app = NotesApp(root)
    root.mainloop()
