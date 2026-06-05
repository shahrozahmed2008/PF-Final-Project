import tkinter as tk
from tkinter import messagebox, ttk
import json
import os


class TeacherPortal:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Portal - Teacher Management Dashboard")
        self.root.geometry("1000x700")
        self.root.config(bg="#f4f6f9")

        # Mapping Subject Names to your exact JSON filenames
        self.quiz_files = {
            "English Vocabulary": "english.json",
            "Mathematics": "math.json",
            "Physics": "physics.json",
            "General Knowledge": "general_knowledge.json"
        }

        # Operational variables
        self.current_file = ""
        self.current_key = ""  # Keeps track of the root key inside the JSON (e.g., 'Math')
        self.questions_list = []
        self.selected_index = None

        self.build_ui()

    def build_ui(self):
        # --- Top Banner Header ---
        header = tk.Frame(self.root, bg="#2c3e50", height=60)
        header.pack(fill="x", side="top")

        title_lbl = tk.Label(header, text="Teacher Management Control Panel", font=("Arial", 16, "bold"), fg="white",
                             bg="#2c3e50")
        title_lbl.pack(pady=15, padx=20, side="left")

        # --- Main Layout Body Split Frame ---
        main_frame = tk.Frame(self.root, bg="#f4f6f9")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Left Panel: Controls and Subject Selector Listbox
        left_panel = tk.Frame(main_frame, bg="#f4f6f9", width=320)
        left_panel.pack(side="left", fill="both", padx=(0, 10))
        left_panel.pack_propagate(False)

        # Subject Selector Dropdown Combobox
        tk.Label(left_panel, text="Select Subject File:", font=("Arial", 11, "bold"), bg="#f4f6f9", fg="#34495e").pack(
            anchor="w", pady=(0, 5))
        self.subject_combo = ttk.Combobox(left_panel, values=list(self.quiz_files.keys()), state="readonly",
                                          font=("Arial", 10))
        self.subject_combo.pack(fill="x", pady=(0, 15))
        self.subject_combo.bind("<<ComboboxSelected>>", self.load_subject_json)

        # MCQs Inventory Listbox Display
        tk.Label(left_panel, text="Active Questions Bank:", font=("Arial", 11, "bold"), bg="#f4f6f9",
                 fg="#34495e").pack(anchor="w")

        list_frame = tk.Frame(left_panel)
        list_frame.pack(fill="both", expand=True, pady=5)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self.mcq_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Arial", 10), bg="white",
                                      fg="#2c3e50", selectbackground="#3498db")
        scrollbar.config(command=self.mcq_listbox.yview)

        scrollbar.pack(side="right", fill="y")
        self.mcq_listbox.pack(side="left", fill="both", expand=True)
        self.mcq_listbox.bind("<<ListboxSelect>>", self.on_question_select)

        # Actions Row underneath the listbox
        action_btn_frame = tk.Frame(left_panel, bg="#f4f6f9")
        action_btn_frame.pack(fill="x", pady=(10, 0))

        self.new_btn = tk.Button(action_btn_frame, text="+ Clear Form / New MCQ", font=("Arial", 10, "bold"),
                                 bg="#9b59b6", fg="white", command=self.clear_form, cursor="hand2")
        self.new_btn.pack(fill="x", pady=2)

        self.delete_btn = tk.Button(action_btn_frame, text="🗑 Delete Selected MCQ", font=("Arial", 10, "bold"),
                                    bg="#e74c3c", fg="white", command=self.delete_mcq, cursor="hand2")
        self.delete_btn.pack(fill="x", pady=2)

        # Right Panel: Editing Data Entry Form Box
        self.right_panel = tk.LabelFrame(main_frame, text=" Question Management Form ", font=("Arial", 12, "bold"),
                                         bg="white", fg="#2c3e50", padx=15, pady=15)
        self.right_panel.pack(side="right", fill="both", expand=True)

        # Form Input Layout Fields
        tk.Label(self.right_panel, text="Question Text:", font=("Arial", 10, "bold"), bg="white", fg="#34495e").pack(
            anchor="w", pady=(5, 2))
        self.question_entry = tk.Entry(self.right_panel, font=("Arial", 11), bg="#f8f9fa")
        self.question_entry.pack(fill="x", pady=(0, 10))

        # Options Frame
        options_label_frame = tk.LabelFrame(self.right_panel, text=" Multiple Choice Options ",
                                            font=("Arial", 10, "bold"), bg="white", fg="#2c3e50", padx=10, pady=10)
        options_label_frame.pack(fill="x", pady=5)

        self.option_entries = []
        labels = ["Option A:", "Option B:", "Option C:", "Option D:"]
        for i in range(4):
            tk.Label(options_label_frame, text=labels[i], font=("Arial", 9), bg="white", fg="#7f8c8d").pack(anchor="w")
            ent = tk.Entry(options_label_frame, font=("Arial", 10))
            ent.pack(fill="x", pady=(0, 8))
            self.option_entries.append(ent)

        # Target Correct Option Setter
        tk.Label(self.right_panel, text="Exact Correct Option Match String:", font=("Arial", 10, "bold"), bg="white",
                 fg="#27ae60").pack(anchor="w", pady=(10, 2))
        self.correct_entry = tk.Entry(self.right_panel, font=("Arial", 11, "bold"), bg="#f1f9f5", fg="#27ae60")
        self.correct_entry.pack(fill="x", pady=(0, 20))

        # Global Final Save Button Action execution
        self.save_btn = tk.Button(self.right_panel, text="💾 Save / Commit Changes to File", font=("Arial", 12, "bold"),
                                  bg="#2ecc71", fg="white", height=2, command=self.save_mcq_changes, cursor="hand2")
        self.save_btn.pack(fill="x", side="bottom")

    def load_subject_json(self, event=None):
        """Locates, extracts, and parses the chosen dataset target array structures."""
        subject_name = self.subject_combo.get()
        self.current_file = self.quiz_files[subject_name]

        if not os.path.exists(self.current_file):
            messagebox.showerror("Error",
                                 f"Missing data system structure storage: '{self.current_file}'\nCreate this file on root storage path first.")
            return

        try:
            with open(self.current_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.current_key = list(data.keys())[0]
                self.questions_list = data[self.current_key]

            self.refresh_listbox()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Parse Error", f"Could not read database format properly:\n{str(e)}")

    def refresh_listbox(self):
        """Cleans and re-lists inventory question records inside UI left list window box frame."""
        self.mcq_listbox.delete(0, tk.END)
        for i, q in enumerate(self.questions_list):
            self.mcq_listbox.insert(tk.END, f"Q{i + 1}: {q['question']}")

    def on_question_select(self, event):
        """Triggers form loading when a user updates list target lines."""
        selection = self.mcq_listbox.curselection()
        if not selection:
            return

        self.selected_index = selection[0]
        question_item = self.questions_list[self.selected_index]

        # Populating inputs fields natively
        self.question_entry.delete(0, tk.END)
        self.question_entry.insert(0, question_item["question"])

        for i in range(4):
            self.option_entries[i].delete(0, tk.END)
            if i < len(question_item["options"]):
                self.option_entries[i].insert(0, question_item["options"][i])

        self.correct_entry.delete(0, tk.END)
        self.correct_entry.insert(0, question_item["correct_option"])

    def clear_form(self):
        """Empties selection references and clears entry box variables layout lines cleanly."""
        self.mcq_listbox.selection_clear(0, tk.END)
        self.selected_index = None
        self.question_entry.delete(0, tk.END)
        for ent in self.option_entries:
            ent.delete(0, tk.END)
        self.correct_entry.delete(0, tk.END)

    def save_mcq_changes(self):
        """Edits existing records or appends new values before updating storage allocations."""
        if not self.current_file:
            messagebox.showwarning("Incomplete", "Please select a target subject file first!")
            return

        # Harvest data structures values from input arrays
        question_text = self.question_entry.get().strip()
        options = [ent.get().strip() for ent in self.option_entries]
        correct_ans = self.correct_entry.get().strip()

        # Check constraints validations matrix
        if not question_text or not correct_ans or any(not opt for opt in options):
            messagebox.showwarning("Missing Fields",
                                   "All text fields and options variations configurations must be completed!")
            return

        if correct_ans not in options:
            messagebox.showerror("Error Match Rule",
                                 "The correct answer field MUST match exactly one of the 4 choice options above.")
            return

        new_mcq_structure = {
            "question": question_text,
            "options": options,
            "correct_option": correct_ans
        }

        if self.selected_index is not None:
            # EDIT MODE: Modify item data object structural components
            self.questions_list[self.selected_index] = new_mcq_structure
            action_log_msg = "MCQ updated successfully!"
        else:
            # NEW MODE: Append entry configuration matrix
            self.questions_list.append(new_mcq_structure)
            action_log_msg = "New MCQ added successfully!"

        # Commit structural sequence alterations straight into disk storage layout format
        if self.write_to_json():
            messagebox.showinfo("Success", action_log_msg)
            self.refresh_listbox()
            self.clear_form()

    def delete_mcq(self):
        """Removes a targeted row tracking item directly out of memory lists mappings structures."""
        selection = self.mcq_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Required",
                                   "Please pick an active entry from the Question Bank listbox to delete.")
            return

        target_idx = selection[0]

        confirm = messagebox.askyesno("Confirm Delete Action",
                                      "Are you sure you want to permanently delete this MCQ from records database storage?")
        if confirm:
            del self.questions_list[target_idx]
            if self.write_to_json():
                messagebox.showinfo("Deleted", "Question successfully dropped out of tracking logs matrix.")
                self.refresh_listbox()
                self.clear_form()

    def write_to_json(self):
        """Low-level utility handler mapping updated changes back down into disk memory storage profiles."""
        try:
            output_package = {self.current_key: self.questions_list}
            with open(self.current_file, 'w', encoding='utf-8') as file:
                json.dump(output_package, file, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Storage Rewrite Error",
                                 f"Failed saving modifications back down to persistent parameters database maps.\nDetails: {str(e)}")
            return False


if __name__ == "__main__":
    window = tk.Tk()
    portal = TeacherPortal(window)
    window.mainloop()