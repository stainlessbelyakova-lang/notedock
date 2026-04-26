import customtkinter as ctk
from app.storage import load_notes, save_notes, create_note, update_time
from app.config import APP_NAME, WINDOW_SIZE


class NoteDockApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry(WINDOW_SIZE)
        self.minsize(850, 550)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.notes = load_notes()
        self.current_note_id = None
        self.search_text = ctk.StringVar()

        self.build_ui()

        if not self.notes:
            self.add_note()
        else:
            self.refresh_notes_list()
            self.open_note(self.notes[0]["id"])

    def build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(3, weight=1)

        self.logo = ctk.CTkLabel(
            self.sidebar,
            text="NoteDock",
            font=("Arial", 24, "bold")
        )
        self.logo.grid(row=0, column=0, padx=15, pady=(20, 10), sticky="w")

        self.search_entry = ctk.CTkEntry(
            self.sidebar,
            placeholder_text="Search notes...",
            textvariable=self.search_text
        )
        self.search_entry.grid(row=1, column=0, padx=15, pady=8, sticky="ew")
        self.search_text.trace_add("write", lambda *_: self.refresh_notes_list())

        self.new_button = ctk.CTkButton(
            self.sidebar,
            text="+ New Note",
            command=self.add_note
        )
        self.new_button.grid(row=2, column=0, padx=15, pady=8, sticky="ew")

        self.notes_frame = ctk.CTkScrollableFrame(self.sidebar)
        self.notes_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        self.editor = ctk.CTkFrame(self, corner_radius=0)
        self.editor.grid(row=0, column=1, sticky="nsew")
        self.editor.grid_columnconfigure(0, weight=1)
        self.editor.grid_rowconfigure(2, weight=1)

        self.title_entry = ctk.CTkEntry(
            self.editor,
            placeholder_text="Note title",
            font=("Arial", 22, "bold")
        )
        self.title_entry.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.title_entry.bind("<KeyRelease>", self.auto_save)

        self.info_label = ctk.CTkLabel(
            self.editor,
            text="",
            text_color="gray"
        )
        self.info_label.grid(row=1, column=0, padx=22, pady=(0, 5), sticky="w")

        self.textbox = ctk.CTkTextbox(
            self.editor,
            font=("Arial", 16),
            wrap="word"
        )
        self.textbox.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.textbox.bind("<KeyRelease>", self.auto_save)

        self.bottom_bar = ctk.CTkFrame(self.editor, fg_color="transparent")
        self.bottom_bar.grid(row=3, column=0, padx=20, pady=(5, 20), sticky="ew")

        self.pin_button = ctk.CTkButton(
            self.bottom_bar,
            text="Pin",
            width=100,
            command=self.toggle_pin
        )
        self.pin_button.pack(side="left")

        self.delete_button = ctk.CTkButton(
            self.bottom_bar,
            text="Delete",
            width=100,
            fg_color="#8a1f1f",
            hover_color="#6f1717",
            command=self.delete_note
        )
        self.delete_button.pack(side="right")

    def get_current_note(self):
        for note in self.notes:
            if note["id"] == self.current_note_id:
                return note
        return None

    def add_note(self):
        note = create_note()
        self.notes.insert(0, note)
        self.current_note_id = note["id"]
        save_notes(self.notes)
        self.refresh_notes_list()
        self.open_note(note["id"])

    def open_note(self, note_id):
        self.current_note_id = note_id
        note = self.get_current_note()

        if not note:
            return

        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, note["title"])

        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", note["content"])

        self.info_label.configure(
            text=f"Created: {note['created_at']}  •  Updated: {note['updated_at']}"
        )

        self.pin_button.configure(text="Unpin" if note["pinned"] else "Pin")
        self.refresh_notes_list()

    def auto_save(self, event=None):
        note = self.get_current_note()

        if not note:
            return

        title = self.title_entry.get().strip()
        content = self.textbox.get("1.0", "end").strip()

        note["title"] = title if title else "Untitled"
        note["content"] = content
        update_time(note)

        save_notes(self.notes)

        self.info_label.configure(
            text=f"Created: {note['created_at']}  •  Updated: {note['updated_at']}"
        )

        self.refresh_notes_list()

    def delete_note(self):
        if not self.current_note_id:
            return

        self.notes = [
            note for note in self.notes
            if note["id"] != self.current_note_id
        ]

        save_notes(self.notes)

        if self.notes:
            self.open_note(self.notes[0]["id"])
        else:
            self.add_note()

    def toggle_pin(self):
        note = self.get_current_note()

        if not note:
            return

        note["pinned"] = not note["pinned"]
        update_time(note)

        self.notes.sort(key=lambda n: (not n["pinned"], n["updated_at"]), reverse=False)

        save_notes(self.notes)
        self.open_note(note["id"])

    def refresh_notes_list(self):
        for widget in self.notes_frame.winfo_children():
            widget.destroy()

        query = self.search_text.get().lower().strip()

        filtered_notes = []
        for note in self.notes:
            text = f"{note['title']} {note['content']}".lower()
            if query in text:
                filtered_notes.append(note)

        filtered_notes.sort(
            key=lambda n: (not n["pinned"], n["updated_at"]),
            reverse=False
        )

        for note in filtered_notes:
            title = note["title"]
            if note["pinned"]:
                title = "📌 " + title

            button = ctk.CTkButton(
                self.notes_frame,
                text=title,
                anchor="w",
                fg_color="#2b2b2b" if note["id"] != self.current_note_id else "#1f6aa5",
                command=lambda note_id=note["id"]: self.open_note(note_id)
            )
            button.pack(fill="x", padx=5, pady=4)