import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from ctypes import windll
import time
import uuid
import json
import re

class NotesApp:
    #Initialize the NotesApp class, set up the main window and essential variables
    def __init__(self, root):
        self.root = root
        self.root.title("Sticky Notes+")
        self.root.geometry("325x325")
        root.iconbitmap("stickynotes+.ico")

        self.notes_filename = "notes.json"
        self.current_note = {"id": str(uuid.uuid4()), "title": "Sticky Notes+ by Gagandeep Malhotra", "content": ""}
        self.notes_list = []
        self.current_note_id = None
        self.match_indices = []
        self.current_match_index = -1

        self.create_widgets()

        self.load_notes_from_file()

        if self.notes_list:

            self.current_note_id = self.get_most_recently_edited_note_id()
            self.load_current_note()

        else:
            self.note_text.insert("1.0", "\nCreate a New Note:\nFile > New Note")
            self.note_text.tag_configure("center", justify='center')
            self.note_text.tag_add("center", "1.0", "end")
            self.note_text.config(state="disabled")
        
        """
        # Binding key events
        self.note_text.bind("<Control-b>", lambda event: self.apply_bold())
        #self.note_text.bind("<Control-i>", lambda event: self.apply_italic())
        self.note_text.bind("<Control-u>", lambda event: self.apply_underline())
        """
        
    def create_widgets(self):
        self.create_menu_bar()
        self.create_bottom_toolbar_2()
        self.create_bottom_toolbar()
        self.create_main_window()
        
    #Create the menu bar with options like "New Note," "Delete Note," and "Exit"
    def create_menu_bar(self):
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Note", command=self.new_note)
        file_menu.add_command(label="Delete Note", command=self.delete_note)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menu_bar.add_cascade(label="File", menu=file_menu)

        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Notes List", command=self.show_notes_list)
        menu_bar.add_cascade(label="View", menu=view_menu)

        self.root.config(menu=menu_bar)

    #Create the main window layout with title, text area, and other elements
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

    #Create the bottom toolbar with buttons for search, navigation, and formatting options
    def create_bottom_toolbar(self):
        self.bottom_frame = tk.Frame(self.root, bg="#333333", pady=0)
        self.bottom_frame.pack(side="bottom", fill="x")
        
        separator = tk.Frame(root, bg="#222", height=1, bd=0)
        separator.pack(side="bottom", fill="x")
        
        search_image = tk.PhotoImage(file="search.png")

        search_label = tk.Label(self.bottom_frame, image=search_image, bg="#333333", height=15)
        search_label.image = search_image
        search_label.pack(side="left", padx=(10, 2.5))
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.bottom_frame, textvariable=self.search_var, bg="#222", fg="white", insertbackground="lightgrey", bd=0, borderwidth=2.49, relief=tk.FLAT, width=4)
        self.search_entry.pack(side="left", padx=(0), pady=0, fill="x", ipadx=5)
        self.search_entry.bind("<KeyRelease>", self.search_text)
        self.search_entry.bind("<FocusIn>", lambda event: self.on_entry_click())
        self.search_entry.bind("<FocusOut>", lambda event: self.on_focus_out())

        self.prev_button = tk.Button(self.bottom_frame, text="▲", command=self.prev_match, bd=0, bg="#222", fg="#F9F6EE", activebackground="#111", activeforeground="white", font=('Segoe UI', 9), state="disabled")
        self.prev_button.pack(side="left", padx=(0, 0), ipadx=0)
        
        self.next_button = tk.Button(self.bottom_frame, text="▼", command=self.next_match, bd=0, bg="#222", fg="#F9F6EE", activebackground="#111", activeforeground="white", font=('Segoe UI', 9), state="disabled")
        self.next_button.pack(side="left", padx=(0, 0), ipadx=0)
        
        self.matches_label = tk.Label(
            self.bottom_frame, text="", bg="#333333", fg="white", padx=5
        )
        self.matches_label.pack(side="left", padx=(0, 0))
        
        underline_button = tk.Button(self.bottom_frame, text="U", command=self.apply_underline, bd=0, bg="#222", fg="white", activebackground="#111", activeforeground="white", font=('Segoe UI', 9, 'underline'))
        underline_button.pack(side="right", padx=(0, 10), ipadx=5)

        """
        italic_button = tk.Button(self.bottom_frame, text="I", command=self.apply_italic, bd=0, bg="#222", fg="white", activebackground="#111", activeforeground="white", font=('Segoe UI', 9, 'italic'))
        italic_button.pack(side="right", padx=(2.5, 2.5), ipadx=7)

        bold_button = tk.Button(self.bottom_frame, text="B", command=self.apply_bold, bd=0, bg="#222", fg="white", activebackground="#111", activeforeground="white", font=('Segoe UI', 9, 'bold'))
        bold_button.pack(side="right", padx=(0, 0), ipadx=5)
        """
        
        redo_image = tk.PhotoImage(file="redo.png")
        redo_button = tk.Button(self.bottom_frame, image=redo_image, command=self.redo, bd=0, bg="#222", activebackground="#111")
        redo_button.image = redo_image
        redo_button.pack(side="right", padx=(2.5, 5), ipadx=4, ipady=4)
        
        undo_image = tk.PhotoImage(file="undo.png")
        undo_button = tk.Button(self.bottom_frame, image=undo_image, command=self.undo, bd=0, bg="#222", activebackground="#111")
        undo_button.image = undo_image
        undo_button.pack(side="right", padx=(0, 0), ipadx=4, ipady=4)
                
    #Create an additional bottom toolbar with sliders for transparency, zoom, and margin adjustments
    def create_bottom_toolbar_2(self):
        
        self.bottom_frame2 = tk.Frame(self.root, bg="#333333", pady=0)
        self.bottom_frame2.pack(side="bottom", fill="x")
        
        self.char_count_label = tk.Label(
            self.bottom_frame2, text="0 Words   0 Chars", bg="#333333", fg="white", padx=10
        )
        self.char_count_label.pack(side="left")
        
        self.transparency_slider = tk.Scale(
            self.bottom_frame2, from_=0.1, to=1.0, resolution=0.1, orient="horizontal", bg="#191919", activebackground="#111", length=33,
            command=self.update_transparency, showvalue=0, highlightthickness=0, troughcolor="#222", bd=0, sliderrelief="flat", sliderlength=11
        )
        self.transparency_slider.set(1.0)
        self.transparency_slider.pack(side="right", padx=(0, 10))
        
        opacity_image = tk.PhotoImage(file="opacity.png")

        opacity_label = tk.Label(self.bottom_frame2, image=opacity_image, bg="#333333", height=15)
        opacity_label.image = opacity_image
        opacity_label.pack(side="right", padx=(5, 2.5))
        
        self.zoom_slider = tk.Scale(
            self.bottom_frame2, from_=50, to=150, orient="horizontal", bg="#191919", fg="#111", activebackground="#111", length=33,
            command=self.update_zoom, showvalue=0, highlightthickness=0, troughcolor="#222", bd=0, sliderrelief="flat", sliderlength=11
        )
        self.zoom_slider.set(100)
        self.zoom_slider.pack(side="right", padx=(0, 0))
        
        zoom_image = tk.PhotoImage(file="zoom.png")

        zoom_label = tk.Label(self.bottom_frame2, image=zoom_image, bg="#333333", height=15)
        zoom_label.image = zoom_image
        zoom_label.pack(side="right", padx=(5, 2.5)) 
        
        self.margin_slider = tk.Scale(
            self.bottom_frame2, from_=0, to=125, orient="horizontal", bg="#191919", fg="#111", activebackground="#111", length=33,
            command=self.update_margin, showvalue=0, highlightthickness=0, troughcolor="#222", bd=0, sliderrelief="flat", sliderlength=11
        )
        self.margin_slider.set(0)
        self.margin_slider.pack(side="right", padx=(0, 0))
        
        margin_image = tk.PhotoImage(file="margin.png")

        margin_label = tk.Label(self.bottom_frame2, image=margin_image, bg="#333333", height=15)
        margin_label.image = margin_image
        margin_label.pack(side="right", padx=(0, 2.5)) 
    
    #Open a window for creating a new note with a title entry and OK button
    def new_note(self):
        new_note_window = tk.Toplevel(self.root)
        new_note_window.title("New Note")
        new_note_window.iconbitmap("stickynotes+.ico")
        new_note_window.minsize(150, 100)
        new_note_window.resizable(False,False)
        new_note_window.configure(bg='#333')

        title_label = tk.Label(new_note_window, text="Enter Note Title:")
        title_label.configure(bg='#333', fg='white')
        title_label.pack(pady=(10,5))

        title_entry = tk.Entry(new_note_window)
        title_entry.configure(bg='#222', fg='white', insertbackground='white', highlightbackground="grey",)
        title_entry.pack()

        ok_button = tk.Button(new_note_window, text="OK", command=lambda: self.process_new_note(title_entry.get(), new_note_window))
        ok_button.configure(bg='#333', fg='white', activebackground='#222', activeforeground='white')
        ok_button.pack(fill="x", padx=12.5, pady=(10,0))

    #Process the creation of a new note by updating notes_list and loading the new note
    def process_new_note(self, new_note_title, new_note_window):
        if new_note_title:
            new_note_id = str(uuid.uuid4())
            self.notes_list.append({"id": new_note_id, "title": new_note_title, "content": ""})
            self.current_note_id = new_note_id
            self.load_current_note()
            self.note_text.config(state="normal")
            self.note_text.delete("1.0", "end")

        new_note_window.destroy()

    #Delete the currently selected note, updating notes_list and loading the most recent note
    def delete_note(self):
        confirm_delete = messagebox.askyesno("Delete Note", "Confirm Delete?")
        if confirm_delete:
            note_id_to_delete = self.current_note_id
            self.notes_list = [note for note in self.notes_list if note["id"] != note_id_to_delete]

            if not self.notes_list:
                self.current_note = {"id": "", "title": "", "content": ""}
                self.current_note_id = None
            else:
                
                self.current_note_id = self.get_most_recently_edited_note_id()
                self.load_current_note()

            self.load_current_note()
            self.save_notes_to_file()
    
    #Update the left margin of the text area based on the provided value            
    def update_margin(self, value):
        margin_value = float(value)
        padding_x = int(margin_value)
        self.note_text.config(padx=(padding_x), pady=0)

    #Search for the entered text in the note and highlight occurrences
    def search_text(self, event=None):
        search_text = self.search_var.get().lower()
        self.note_text.tag_remove("search", "1.0", "end")
        self.note_text.tag_delete("search")

        if search_text:
            start = "1.0"
            self.match_indices = []

            found_index = self.note_text.search(search_text, start, stopindex="end", nocase=True)
            matches_count = 0

            while found_index:
                end = f"{found_index}+{len(search_text)}c"
                self.note_text.tag_add("search", found_index, end)
                self.match_indices.append(found_index)
                start = end
                found_index = self.note_text.search(search_text, start, stopindex="end", nocase=True)

                matches_count += 1

            self.note_text.tag_configure("search", background="yellow", foreground="black")

            if self.match_indices:
                self.current_match_index = 0
                self.show_current_match()
            
            self.update_matches_label()
        
        else:
            self.match_indices = []
            self.current_match_index = -1
            self.matches_label.config(text="")
        
        self.update_prev_next_buttons_state()

    # Update the state of previous and next buttons based on search results
    def update_prev_next_buttons_state(self):
        if self.match_indices:
            self.prev_button.config(state="normal")
            self.next_button.config(state="normal")
        else:
            self.prev_button.config(state="disabled")
            self.next_button.config(state="disabled")
    
    #Show the currently selected search match in the note
    def show_current_match(self):
        if 0 <= self.current_match_index < len(self.match_indices):
            start = self.match_indices[self.current_match_index]
            end = f"{start}+{len(self.search_var.get())}c"
            self.note_text.see(start)
            self.note_text.tag_add("search", start, end)

    #Navigate to the next search match in the note
    def next_match(self):
        if self.match_indices:
            self.current_match_index = (self.current_match_index + 1) % len(self.match_indices)
            self.show_current_match()
            self.update_matches_label()

    #Navigate to the previous search match in the note
    def prev_match(self):
        if self.match_indices:
            self.current_match_index = (self.current_match_index - 1) % len(self.match_indices)
            self.show_current_match()
            self.update_matches_label()
    
    #Update the label displaying current match information
    def update_matches_label(self):
        if self.match_indices:
            total_matches = len(self.match_indices)
            self.matches_label.config(text=f"{self.current_match_index + 1} of {total_matches}")
        elif self.search_entry:
            self.match_indices = []
            self.current_match_index = -1
            self.matches_label.config(text="No Matches")
        else:
            self.match_indices = []
            self.current_match_index = -1
            self.matches_label.config(text="")
    
    #Undo the last text edit in the note            
    def undo(self):
        try:
            self.note_text.edit_undo()
            self.update_char_count()
        except tk.TclError:
            pass
        
    #Redo the previously undone text edit in the note
    def redo(self):
        try:
            self.note_text.edit_redo()
            self.update_char_count()
        except tk.TclError:
            pass
    
    #Handle the click event on the search entry to clear the placeholder text
    def on_entry_click(self):
        if self.search_entry.get() == "Find...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.configure(foreground="white", font=('Segoe UI', 9))

    #Handle the focus-out event on the search entry to show placeholder text if empty
    def on_focus_out(self):
        if self.search_entry.get() == "":
            self.search_entry.insert(0, "Find...")
            self.search_entry.configure(foreground="grey", font=('Segoe UI', 9, 'italic'))
            self.matches_label.config(text="")
    
    #Open a window displaying the list of notes with an option to open a selected note
    def show_notes_list(self):
        notes_list_window = tk.Toplevel(self.root)
        notes_list_window.title("Notes List")
        notes_list_window.iconbitmap("stickynotes+.ico")
        notes_list_window.minsize(225, 150)
        notes_list_window.configure(bg='#333')

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

    #Get the ID of the most recently edited note from the notes_list
    def get_most_recently_edited_note_id(self):
        sorted_notes = sorted(self.notes_list, key=lambda x: x.get('last_modified', 0), reverse=True)
        return sorted_notes[0]['id'] if sorted_notes else None

    #Autosave the current note content and update last_modified timestamp
    def auto_save(self, event):
        self.current_note["content"] = self.note_text.get("1.0", "end-1c")
        self.update_char_count()
        self.current_note['last_modified'] = time.time()
        self.save_notes_to_file()

    #Update the character count label based on the current note's content
    def update_char_count(self):
        text_content = self.note_text.get("1.0", "end-1c")
        char_count = len(text_content)
        word_count = len(re.findall(r'\b\w+\b', text_content))
        
        if word_count != 1 and char_count != 1:
            count_text = f"{word_count} Words   {char_count} Chars"
        elif word_count == 1 and char_count != 1:
            count_text = f"{word_count} Word    {char_count} Chars"
        else:
            count_text = f"{word_count} Word    {char_count} Char"
        
        self.char_count_label.config(text=count_text, font=('Segoe UI', 9))
    
    #Update the transparency of the main window based on the provided value  
    def update_transparency(self, value):
        transparency = float(value)
        self.root.attributes("-alpha", transparency)
        
    """
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
    """
    
    #Apply the underline formatting to the selected text in the note
    def apply_underline(self):
        sel_start = self.note_text.index(tk.SEL_FIRST)
        sel_end = self.note_text.index(tk.SEL_LAST)

        if sel_start and sel_end:
            self.note_text.tag_add("underline", sel_start, sel_end)
            self.note_text.tag_configure("underline", underline=True)
    
    #Update the zoom level of the text area based on the slider value    
    def update_zoom(self, value):
        zoom_level = int(value)
        font_size = int(12 * zoom_level / 100) 
        self.note_text.configure(font=("Segoe UI", font_size))
    
    #Load notes from a JSON file into the notes_list
    def load_notes_from_file(self):
        try:
            with open(self.notes_filename, "r") as file:
                data = file.read()
                self.notes_list = json.loads(data)
        except FileNotFoundError:
            pass
        
    #Save the notes_list to a JSON file      
    def save_notes_to_file(self):
        with open(self.notes_filename, "w") as file:
            json.dump(self.notes_list, file)

    #Load the content of the currently selected note into the main window
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
    root.minsize(315, 150)
    app = NotesApp(root)
    root.mainloop()
