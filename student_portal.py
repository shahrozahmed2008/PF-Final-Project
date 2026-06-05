import tkinter as tk
from tkinter import messagebox
import json
import os


class QuizPortal:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Portal Dashboard")
        self.root.geometry("1000x700")
        self.root.config(bg="#f4f6f9")

        # Mapping Display Names to JSON File Names
        self.quiz_files = {
            "English Vocabulary": "english.json",
            "Mathematics": "math.json",
            "Physics": "physics.json",
            "General Knowledge": "general_knowledge.json"
        }

        # Global Operational Variables
        self.questions = []
        self.current_q_index = 0
        self.score = 0

        # Store user selections to remember answers when clicking "Previous"
        self.user_answers = {}

        # Fix for pre-selection radio bug
        self.selected_option = tk.StringVar(value="none")

        # Load Main Screen Layout
        self.display_main_dashboard()

    def clear_screen(self):
        """Helper to safely dismantle all active screen configurations."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def display_main_dashboard(self):
        self.clear_screen()

        title = tk.Label(self.root, text="Quiz Portal Dashboard", font=("Arial", 24, "bold"), bg="#f4f6f9",
                         fg="#2c3e50")
        title.pack(pady=40)

        subtitle = tk.Label(self.root, text="Select a Subject to Import Questions:", font=("Arial", 12), bg="#f4f6f9",
                            fg="#7f8c8d")
        subtitle.pack(pady=5)

        btn_frame = tk.Frame(self.root, bg="#f4f6f9")
        btn_frame.pack(pady=20)

        for display_name, file_name in self.quiz_files.items():
            btn = tk.Button(
                btn_frame,
                text=display_name,
                font=("Arial", 12, "bold"),
                width=22,
                height=2,
                bg="#3498db",
                fg="white",
                cursor="hand2",
                activebackground="#2980b9",
                activeforeground="white",
                command=lambda fname=file_name, name=display_name: self.import_and_start(fname, name)
            )
            btn.pack(pady=8)

    def import_and_start(self, json_file, subject_title):
        if not os.path.exists(json_file):
            messagebox.showerror("Error", f"Could not find the data file: '{json_file}'")
            return

        try:
            with open(json_file, 'r', encoding='utf-8') as file:
                raw_data = json.load(file)
                first_key = list(raw_data.keys())[0]
                self.questions = raw_data[first_key]

            self.current_subject = subject_title
            self.current_q_index = 0
            self.score = 0
            self.user_answers = {}  # Reset answers history dictionary

            self.build_quiz_interface()
            self.load_question_data()

        except Exception as e:
            messagebox.showerror("Import Error", f"Failed parsing quiz records properly.\nDetails: {str(e)}")

    def build_quiz_interface(self):
        self.clear_screen()

        header = tk.Frame(self.root, bg="#2c3e50", height=40)
        header.pack(fill="x")

        self.subj_lbl = tk.Label(header, text=f"Subject: {self.current_subject}", font=("Arial", 11, "bold"),
                                 fg="white", bg="#2c3e50")
        self.subj_lbl.pack(side="left", padx=15, pady=8)

        self.progress_lbl = tk.Label(header, text="", font=("Arial", 11), fg="white", bg="#2c3e50")
        self.progress_lbl.pack(side="right", padx=15, pady=8)

        self.question_lbl = tk.Label(self.root, text="", font=("Arial", 13, "bold"), bg="#f4f6f9", fg="#2c3e50",
                                     wraplength=500, justify="center")
        self.question_lbl.pack(pady=35)

        self.options_frame = tk.Frame(self.root, bg="#f4f6f9")
        self.options_frame.pack(pady=10)

        self.radio_buttons = []
        for i in range(4):
            rb = tk.Radiobutton(
                self.options_frame,
                text="",
                variable=self.selected_option,
                value="",
                font=("Arial", 11),
                bg="#f4f6f9",
                anchor="w",
                width=35,
                activebackground="#f4f6f9"
            )
            rb.pack(pady=6, anchor="w")
            self.radio_buttons.append(rb)

        # Navigation Actions Frame
        control_frame = tk.Frame(self.root, bg="#f4f6f9")
        control_frame.pack(pady=30)

        # CHANGED: Added Return / Previous Question button
        self.prev_btn = tk.Button(
            control_frame,
            text="↩ Return (Previous)",
            font=("Arial", 11, "bold"),
            bg="#7f8c8d",
            fg="white",
            width=16,
            command=self.previous_question,
            cursor="hand2"
        )
        self.prev_btn.pack(side="left", padx=10)

        self.submit_btn = tk.Button(
            control_frame,
            text="Next / Submit ↪",
            font=("Arial", 11, "bold"),
            bg="#2ecc71",
            fg="white",
            width=16,
            command=self.verify_and_next,
            cursor="hand2"
        )
        self.submit_btn.pack(side="left", padx=10)

    def load_question_data(self):
        # Disable the Return button if we are on the very first question
        if self.current_q_index == 0:
            self.prev_btn.config(state="disabled", bg="#bdc3c7")
        else:
            self.prev_btn.config(state="normal", bg="#7f8c8d")

        # If user has already answered this question before, restore their choice
        if self.current_q_index in self.user_answers:
            self.selected_option.set(self.user_answers[self.current_q_index])
        else:
            self.selected_option.set("none")  # Clear checkmarks natively

        current_data = self.questions[self.current_q_index]

        self.progress_lbl.config(text=f"Progress: {self.current_q_index + 1}/{len(self.questions)}")
        self.question_lbl.config(text=current_data["question"])

        for i, option in enumerate(current_data["options"]):
            self.radio_buttons[i].config(text=option, value=option)

    def verify_and_next(self):
        user_pick = self.selected_option.get()

        if user_pick == "none" or not user_pick:
            messagebox.showwarning("Incomplete", "Please pick an option before moving forward.")
            return

        # Log/Save the selected answer for history tracking memory
        self.user_answers[self.current_q_index] = user_pick

        # Progress forward
        self.current_q_index += 1
        if self.current_q_index < len(self.questions):
            self.load_question_data()
        else:
            self.calculate_and_render_scorecard()

    def previous_question(self):
        """Action handler to safely step backwards into previous question indexes."""
        if self.current_q_index > 0:
            # Save whatever state the user currently clicked before tracking back (optional)
            current_pick = self.selected_option.get()
            if current_pick != "none":
                self.user_answers[self.current_q_index] = current_pick

            self.current_q_index -= 1
            self.load_question_data()

    def calculate_and_render_scorecard(self):
        """Calculates final scores only at the end of the full evaluation submission loop."""
        self.clear_screen()
        self.score = 0

        # Calculate scores dynamically using saved user inputs history map
        for index, q_item in enumerate(self.questions):
            saved_pick = self.user_answers.get(index)
            if saved_pick == q_item["correct_option"]:
                self.score += 1

        final_lbl = tk.Label(self.root, text="Quiz Evaluation", font=("Arial", 22, "bold"), bg="#f4f6f9", fg="#2c3e50")
        final_lbl.pack(pady=45)

        score_val = tk.Label(self.root, text=f"Score: {self.score} / {len(self.questions)}", font=("Arial", 18),
                             bg="#f4f6f9", fg="#e67e22")
        score_val.pack(pady=10)

        percentage = (self.score / len(self.questions)) * 100
        perc_lbl = tk.Label(self.root, text=f"Percentage Performance: {percentage:.1f}%", font=("Arial", 11),
                            bg="#f4f6f9", fg="#7f8c8d")
        perc_lbl.pack(pady=5)

        return_btn = tk.Button(
            self.root,
            text="Back to Main Menu",
            font=("Arial", 11, "bold"),
            bg="#34495e",
            fg="white",
            command=self.display_main_dashboard,
            cursor="hand2"
        )
        return_btn.pack(pady=40)


if __name__ == "__main__":
    root_window = tk.Tk()
    portal_instance = QuizPortal(root_window)
    root_window.mainloop()