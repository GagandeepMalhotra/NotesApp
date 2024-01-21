import tkinter as tk
from tkinter import messagebox

class NotesApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Notes App")

        # Text widget for note input
        self.note_text = tk.Text(self.master, height=10, width=50)
        self.note_text.pack(pady=10)

        # Button to save the note
        save_button = tk.Button(self.master, text="Save Note", command=self.save_note)
        save_button.pack()

        # Listbox to display saved notes
        self.notes_listbox = tk.Listbox(self.master, height=10, width=50)
        self.notes_listbox.pack(pady=10)

        # Button to delete selected note
        delete_button = tk.Button(self.master, text="Delete Note", command=self.delete_note)
        delete_button.pack()

        # Load existing notes from file
        self.load_notes()

    def save_note(self):
        # Get the note from the text widget
        note = self.note_text.get("1.0", tk.END).strip()

        if note:
            # Append the note to the listbox
            self.notes_listbox.insert(tk.END, note)

            # Save all notes to a local file
            with open("notes.txt", "a") as file:
                file.write(note + "\n")

            # Clear the text widget after saving
            self.note_text.delete("1.0", tk.END)
        else:
            messagebox.showwarning("Warning", "Please enter a note.")

    def delete_note(self):
        # Get the selected note from the listbox
        selected_note_index = self.notes_listbox.curselection()

        if selected_note_index:
            # Delete the selected note from the listbox
            self.notes_listbox.delete(selected_note_index)

            # Update the local file with the remaining notes
            with open("notes.txt", "w") as file:
                for i in range(self.notes_listbox.size()):
                    file.write(self.notes_listbox.get(i) + "\n")

    def load_notes(self):
        try:
            # Read existing notes from the local file and populate the listbox
            with open("notes.txt", "r") as file:
                notes = file.read().splitlines()
                for note in notes:
                    self.notes_listbox.insert(tk.END, note)
        except FileNotFoundError:
            # Create the file if it doesn't exist
            with open("notes.txt", "w"):
                pass

if __name__ == "__main__":
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()
