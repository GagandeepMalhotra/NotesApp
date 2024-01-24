import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Local Notes App")
        self.root.geometry("800x600")

        self.notes_filename = "notes.txt"
        self.current_note = {"title": "Create new note", "content": ""}
        self.notes_list = []
        self.current_note_index = 0

        self.create_widgets()

        # Load notes from file on application startup
        self.load_notes_from_file()

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
        self.note_text.bind("<Key>", self.auto_save)

        # Display "Create new note" if no notes exist
        if not self.notes_list:
            self.note_text.insert("1.0", "Create new note")

    def create_bottom_toolbar(self):
        self.bottom_frame = tk.Frame(self.root, bg="#333333")
        self.bottom_frame.pack(side="bottom", fill="x")

        self.char_count_label = tk.Label(
            self.bottom_frame, text="Chars: 0", bg="#333333", fg="white", padx=10
        )
        self.char_count_label.pack(side="left")

        bold_button = tk.Button(self.bottom_frame, text="Bold", command=self.apply_bold)
        bold_button.pack(side="right", padx=5)

        italic_button = tk.Button(self.bottom_frame, text="Italic", command=self.apply_italic)
        italic_button.pack(side="right", padx=5)

        underline_button = tk.Button(self.bottom_frame, text="Underline", command=self.apply_underline)
        underline_button.pack(side="right", padx=5)

    def new_note(self):
        new_note_title = simpledialog.askstring("New Note", "Enter a title for the new note:")
        if new_note_title:
            self.notes_list.append({"title": new_note_title, "content": ""})
            self.current_note_index = len(self.notes_list) - 1
            self.load_current_note()

    def delete_note(self):
        confirm_delete = messagebox.askyesno("Delete Note", "Are you sure you want to delete this note?")
        if confirm_delete:
            del self.notes_list[self.current_note_index]
            if self.current_note_index >= len(self.notes_list):
                self.current_note_index = len(self.notes_list) - 1
            self.load_current_note()

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
                self.current_note_index = selected_index[0]
                self.load_current_note()
                notes_list_window.destroy()

        open_button = tk.Button(notes_list_window, text="Open Note", command=open_selected_note)
        open_button.pack(pady=10)

    def auto_save(self, event):
        self.current_note["content"] = self.note_text.get("1.0", "end-1c")
        self.update_char_count()
        self.save_notes_to_file()  # Save notes to file on each change

    def update_char_count(self):
        char_count = len(self.note_text.get("1.0", "end-1c"))
        self.char_count_label.config(text=f"Chars: {char_count}")

    def apply_bold(self):
        self.note_text.tag_add("bold", self.note_text.index(tk.SEL_FIRST), self.note_text.index(tk.SEL_LAST))
        self.note_text.tag_configure("bold", font=("Arial", 12, "bold"))

    def apply_italic(self):
        self.note_text.tag_add("italic", self.note_text.index(tk.SEL_FIRST), self.note_text.index(tk.SEL_LAST))
        self.note_text.tag_configure("italic", font=("Arial", 12, "italic"))

    def apply_underline(self):
        self.note_text.tag_add("underline", self.note_text.index(tk.SEL_FIRST), self.note_text.index(tk.SEL_LAST))
        self.note_text.tag_configure("underline", underline=True)

    def load_notes_from_file(self):
        try:
            with open(self.notes_filename, "r") as file:
                data = file.readlines()
                self.notes_list = [eval(note.strip()) for note in data]
        except FileNotFoundError:
            # Handle the case when the file doesn't exist yet
            pass

    def save_notes_to_file(self):
        with open(self.notes_filename, "w") as file:
            for note in self.notes_list:
                file.write(str(note) + "\n")

    def load_current_note(self):
        self.current_note = self.notes_list[self.current_note_index]
        self.title_label.config(text=self.current_note["title"])
        self.note_text.delete("1.0", "end")
        self.note_text.insert("1.0", self.current_note["content"])
        self.update_char_count()

if __name__ == "__main__":
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()
