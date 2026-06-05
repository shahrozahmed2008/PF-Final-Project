import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

# Import your existing portal classes
from student_portal import QuizPortal
from teacher_portal import TeacherPortal

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Portal - Login")
        self.root.geometry("1000x700")
        self.root.config(bg="#f4f6f9")
        
        self.users_file = "users.json"
        self.ensure_users_file()
        
        self.build_login_ui()

    def ensure_users_file(self):
        """Creates a default users.json file if it doesn't exist."""
        if not os.path.exists(self.users_file):
            default_users = {
                "teachers": [{"username": "teacher1", "password": "password123"}],
                "students": [{"username": "student1", "password": "password123"}]
            }
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(default_users, f, indent=4)

    def clear_window(self):
        """Destroys all widgets on the screen to load the next module."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def build_login_ui(self):
        self.clear_window()
        self.root.title("Quiz Portal - Secure Login")

        # Header
        header = tk.Frame(self.root, bg="#2c3e50", height=80)
        header.pack(fill="x")
        
        title_lbl = tk.Label(header, text="Welcome to the Quiz Portal", font=("Arial", 20, "bold"), fg="white", bg="#2c3e50")
        title_lbl.pack(pady=20)

        # Login Form Frame
        form_frame = tk.Frame(self.root, bg="#f4f6f9")
        form_frame.pack(pady=40)

        # Role Selection
        tk.Label(form_frame, text="Select Role:", font=("Arial", 12, "bold"), bg="#f4f6f9", fg="#34495e").grid(row=0, column=0, pady=10, sticky="e", padx=10)
        self.role_var = tk.StringVar()
        self.role_combo = ttk.Combobox(form_frame, textvariable=self.role_var, values=["Student", "Teacher"], state="readonly", font=("Arial", 11), width=18)
        self.role_combo.grid(row=0, column=1, pady=10)
        self.role_combo.current(0) # Default to Student

        # Username
        tk.Label(form_frame, text="Username:", font=("Arial", 12, "bold"), bg="#f4f6f9", fg="#34495e").grid(row=1, column=0, pady=10, sticky="e", padx=10)
        self.user_entry = tk.Entry(form_frame, font=("Arial", 11), width=20)
        self.user_entry.grid(row=1, column=1, pady=10)

        # Password
        tk.Label(form_frame, text="Password:", font=("Arial", 12, "bold"), bg="#f4f6f9", fg="#34495e").grid(row=2, column=0, pady=10, sticky="e", padx=10)
        self.pass_entry = tk.Entry(form_frame, show="*", font=("Arial", 11), width=20)
        self.pass_entry.grid(row=2, column=1, pady=10)

        # Login Button
        login_btn = tk.Button(self.root, text="Login", font=("Arial", 12, "bold"), bg="#3498db", fg="white", width=20, cursor="hand2", command=self.authenticate)
        login_btn.pack(pady=10)

    def authenticate(self):
        role = self.role_var.get()
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Incomplete", "Please enter both username and password.")
            return

        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read users file: {str(e)}")
            return

        # Determine which list to check based on role
        role_key = "teachers" if role == "Teacher" else "students"
        users_list = users_data.get(role_key, [])

        # Verify Credentials
        authenticated = False
        for u in users_list:
            if u["username"] == username and u["password"] == password:
                authenticated = True
                break

        if authenticated:
            messagebox.showinfo("Success", f"Logged in successfully as {role}!")
            self.clear_window()
            
            # Launch the respective portal
            if role == "Teacher":
                TeacherPortal(self.root)
            else:
                QuizPortal(self.root)
        else:
            messagebox.showerror("Access Denied", "Invalid username or password. Please try again.")

if __name__ == "__main__":
    root_window = tk.Tk()
    app = MainApp(root_window)
    root_window.mainloop()