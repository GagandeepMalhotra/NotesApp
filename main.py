import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import time
import uuid
import json

class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Local Notes App")
        self.root.geometry("800x600")

        self.notes_filename = "notes.json"
        self.current_note = {"id": str(uuid.uuid4()), "title": "Sticky Notes+ by Gagandeep Malhotra", "content": ""}
        self.notes_list = []
        self.current_note_id = None

        self.create_widgets()

        # Load notes from file on application startup
        self.load_notes_from_file()

        # Check if there are saved notes
        if self.notes_list:
            # Set the ID to the most recently edited note
            self.current_note_id = self.get_most_recently_edited_note_id()
            # Load the most recently edited note
            self.load_current_note()

        # Display "Create new note" if no notes exist
        else:
            self.note_text.insert("1.0", "\nCreate a New Note:\nFile > New Note")
            self.note_text.tag_configure("center", justify='center')
            self.note_text.tag_add("center", "1.0", "end")
            self.note_text.config(state="disabled")

    def create_widgets(self):
        self.create_menu_bar()
        self.create_main_window()
        self.create_bottom_toolbar()

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
        self.main_frame.pack(expand=True, fill="both")

        self.title_label = tk.Label(
            self.main_frame, text=self.current_note["title"], font=("Arial", 16), bg="#333333", fg="white"
        )
        self.title_label.pack(anchor="w", padx=10, pady=5)

        self.note_text = tk.Text(self.main_frame, wrap="word", font=("Arial", 12), bg="#333333", fg="white")
        self.note_text.pack(expand=True, fill="both", padx=10, pady=5)

        self.note_text.insert("1.0", self.current_note["content"])
        self.note_text.bind("<KeyRelease>", self.auto_save)

    def create_bottom_toolbar(self):
        self.bottom_frame = tk.Frame(self.root, bg="#333333")
        self.bottom_frame.pack(side="bottom", fill="x")

        self.char_count_label = tk.Label(
            self.bottom_frame, text="Chars: 0", bg="#333333", fg="white", padx=10
        )
        self.char_count_label.pack(side="left")

        bold_button = tk.Button(self.bottom_frame, text="B", command=self.apply_bold)
        bold_button.pack(side="right", padx=5)

        italic_button = tk.Button(self.bottom_frame, text="I", command=self.apply_italic)
        italic_button.pack(side="right", padx=5)

        underline_button = tk.Button(self.bottom_frame, text="U", command=self.apply_underline)
        underline_button.pack(side="right", padx=5)

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
        self.char_count_label.config(text=f"Chars: {char_count}")

    def apply_format(self, tag_name, font_config=None, underline=False):
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
        self.apply_format("bold", font_config={"font": ("Arial", 12, "bold")})

    def apply_italic(self):
        self.apply_format("italic", font_config={"font": ("Arial", 12, "italic")})

    def apply_underline(self):
        self.apply_format("underline", underline=True)


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
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()
