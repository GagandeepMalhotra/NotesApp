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
        self.root.geometry("500x500")
        root.iconbitmap("stickynotes+.ico")

        self.notes_filename = "notes.json"
        self.current_note = {"id": str(uuid.uuid4()), "title": "Sticky Notes+ by Gagandeep Malhotra", "content": ""}
        self.notes_list = []
        self.current_note_id = None

        self.create_widgets()
        self.create_zoom_slider()

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

    def create_bottom_toolbar(self):
        self.bottom_frame = tk.Frame(self.root, bg="#333333", pady=1)
        self.bottom_frame.pack(side="bottom", fill="x")
        
        separator = tk.Frame(root, bg="#222", height=1, bd=0)
        separator.pack(side="bottom", fill="x")

        self.char_count_label = tk.Label(
            self.bottom_frame, text="Chars: 0", bg="#333333", fg="white", padx=10
        )
        self.char_count_label.pack(side="left")

        underline_button = tk.Button(self.bottom_frame, text="U", command=self.apply_underline, bd=0, bg="#222", fg="white", activebackground="#111", activeforeground="white", font=('Segoe UI', 9, 'underline'))
        underline_button.pack(side="right", padx=(0,10), ipadx=7)  # No padx needed for the last button

        italic_button = tk.Button(self.bottom_frame, text="I", command=self.apply_italic, bd=0, bg="#222", fg="white", activebackground="#111", activeforeground="white", font=('Segoe UI', 9, 'italic'))
        italic_button.pack(side="right", padx=(2.5, 2.5), ipadx=10)

        bold_button = tk.Button(self.bottom_frame, text="B", command=self.apply_bold, bd=0, bg="#222", fg="white", activebackground="#111", activeforeground="white", font=('Segoe UI', 9, 'bold'))
        bold_button.pack(side="right", padx=(5, 0), ipadx=8)  # Set ipadx to make the button wider

        self.transparency_slider = tk.Scale(
            self.bottom_frame, from_=0.1, to=1.0, resolution=0.1, orient="horizontal", bg="#222", activebackground="#333",
            command=self.update_transparency, showvalue=0, highlightthickness=0, troughcolor="#222", bd=0
        )
        self.transparency_slider.set(1.0)  # Set default transparency to 1.0 (fully opaque)
        self.transparency_slider.pack(side="right", padx=(0,10))
        
        # Load the opacity.png image
        opacity_image = tk.PhotoImage(file="opacity.png")

        # Create a label to display the image
        opacity_label = tk.Label(self.bottom_frame, image=opacity_image, bg="#333333", height=15)
        opacity_label.image = opacity_image  # To prevent image from being garbage collected
        opacity_label.pack(side="right", padx=(12.5, 2.5))  # Adjust padx as needed
        
    def new_note(self):
        self.note_text.config(state="normal")
        new_note_title = simpledialog.askstring("New Note", "Enter a title for the new note:")
        if new_note_title:
            new_note_id = str(uuid.uuid4())  # Generate a unique ID for the new note
            self.notes_list.append({"id": new_note_id, "title": new_note_title, "content": ""})
            self.current_note_id = new_note_id
            self.load_current_note()

    def delete_note(self):
        confirm_delete = messagebox.askyesno("Delete Note", "Are you sure you want to delete this note?")
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

    def show_notes_list(self):
        notes_list_window = tk.Toplevel(self.root)
        notes_list_window.title("Notes List")

        notes_listbox = tk.Listbox(notes_list_window)
        for note in self.notes_list:
            notes_listbox.insert("end", note["title"])

        notes_listbox.pack(expand=True, fill="both")

        def open_selected_note():
            selected_index = notes_listbox.curselection()
            if selected_index:
                self.current_note_id = self.notes_list[selected_index[0]]["id"]
                self.load_current_note()
                notes_list_window.destroy()

        open_button = tk.Button(notes_list_window, text="Open Note", command=open_selected_note)
        open_button.pack(pady=10)

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

    def create_zoom_slider(self):
        self.zoom_slider = tk.Scale(
            self.bottom_frame, from_=50, to=150, orient="horizontal", bg="#222", fg="#111", activebackground="#333",
            command=self.update_zoom, showvalue=0, highlightthickness=0, troughcolor="#222", bd=0
        )
        self.zoom_slider.set(100)  # Set default zoom to 100%
        self.zoom_slider.pack(side="right", padx=(0, 0))
        
        # Load the zoom.png image
        zoom_image = tk.PhotoImage(file="zoom.png")

        # Create a label to display the image
        zoom_label = tk.Label(self.bottom_frame, image=zoom_image, bg="#333333", height=15)
        zoom_label.image = zoom_image  # To prevent image from being garbage collected
        zoom_label.pack(side="right", padx=(10, 2.5)) 

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
    app = NotesApp(root)
    root.mainloop()
