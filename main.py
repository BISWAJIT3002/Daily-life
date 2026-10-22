
import customtkinter as ctk
import json
import os
import hashlib
import secrets
from datetime import date, datetime, timedelta
from tkinter import messagebox

APP_NAME = "Home Maintenance Reminder System"
DATA_FILE = "data.json"

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError):
            data = {}
    else:
        data = {}

    defaults = {
        "users": {},
        "tasks": [],
        "bills": [],
        "appliances": [],
        "expenses": [],
        "providers": [],
        "history": [],
        "profile": {},
        "settings": {"appearance": "System"}
    }

    for key, value in defaults.items():
        if key not in data:
            data[key] = value

    return data


def save_data(data):
    temp_file = DATA_FILE + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    os.replace(temp_file, DATA_FILE)


def make_password_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 120000
    ).hex()
    return salt, hashed


class HomeMaintenanceApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("1150x720")
        self.minsize(900, 600)

        self.data = load_data()
        self.current_user = None
        self.content = None

        self.show_login()

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_screen()

        card = ctk.CTkFrame(self, width=420, height=480)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        ctk.CTkLabel(
            card, text="🏠 HomeCare",
            font=ctk.CTkFont(size=30, weight="bold")
        ).pack(pady=(35, 8))

        ctk.CTkLabel(
            card, text="Home Maintenance Reminder System"
        ).pack(pady=(0, 25))

        self.email_entry = ctk.CTkEntry(
            card, placeholder_text="Email address", width=310, height=40
        )
        self.email_entry.pack(pady=8)

        self.password_entry = ctk.CTkEntry(
            card, placeholder_text="Password",
            show="*", width=310, height=40
        )
        self.password_entry.pack(pady=8)

        self.show_password = ctk.BooleanVar(value=False)

        ctk.CTkCheckBox(
            card, text="Show password",
            variable=self.show_password,
            command=self.toggle_password
        ).pack(pady=6)

        ctk.CTkButton(
            card, text="Login", width=310, height=40,
            command=self.login
        ).pack(pady=12)

        ctk.CTkButton(
            card, text="Create Account", width=310,
            fg_color="transparent", border_width=1,
            command=self.show_register
        ).pack(pady=5)

        ctk.CTkButton(
            card, text="Forgot Password?", width=310,
            fg_color="transparent", border_width=1,
            command=self.show_forgot
        ).pack(pady=5)

    def toggle_password(self):
        self.password_entry.configure(
            show="" if self.show_password.get() else "*"
        )

    def show_register(self):
        self.clear_screen()

        card = ctk.CTkFrame(self, width=430, height=530)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        ctk.CTkLabel(
            card, text="Create Account",
            font=ctk.CTkFont(size=27, weight="bold")
        ).pack(pady=25)

        self.reg_name = ctk.CTkEntry(
            card, placeholder_text="Full name", width=320
        )
        self.reg_name.pack(pady=8)

        self.reg_email = ctk.CTkEntry(
            card, placeholder_text="Email address", width=320
        )
        self.reg_email.pack(pady=8)

        self.reg_password = ctk.CTkEntry(
            card, placeholder_text="Password (6+ characters)",
            show="*", width=320
        )
        self.reg_password.pack(pady=8)

        self.reg_confirm = ctk.CTkEntry(
            card, placeholder_text="Confirm password",
            show="*", width=320
        )
        self.reg_confirm.pack(pady=8)

        ctk.CTkButton(
            card, text="Register", width=320,
            command=self.register
        ).pack(pady=15)

        ctk.CTkButton(
            card, text="Back to Login", width=320,
            fg_color="transparent", border_width=1,
            command=self.show_login
        ).pack(pady=5)

    def register(self):
        name = self.reg_name.get().strip()
        email = self.reg_email.get().strip().lower()
        password = self.reg_password.get()
        confirm = self.reg_confirm.get()

        if not name or not email or not password:
            messagebox.showerror("Error", "Fill in all fields.")
            return

        if "@" not in email or "." not in email:
            messagebox.showerror("Error", "Enter a valid email address.")
            return

        if email in self.data["users"]:
            messagebox.showerror("Error", "Account already exists.")
            return

        if len(password) < 6:
            messagebox.showerror("Error", "Password must have at least 6 characters.")
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        salt, hashed = make_password_hash(password)

        self.data["users"][email] = {
            "name": name,
            "salt": salt,
            "password_hash": hashed
        }

        self.data["profile"] = {
            "name": name,
            "email": email,
            "phone": "",
            "address": ""
        }

        save_data(self.data)

        messagebox.showinfo("Success", "Account created successfully.")
        self.show_login()

    def login(self):
        email = self.email_entry.get().strip().lower()
        password = self.password_entry.get()

        user = self.data["users"].get(email)

        if not user:
            messagebox.showerror("Error", "Account not found. Register first.")
            return

        _, hashed = make_password_hash(password, user["salt"])

        if not secrets.compare_digest(hashed, user["password_hash"]):
            messagebox.showerror("Error", "Incorrect password.")
            return

        self.current_user = email
        save_data(self.data)
        self.show_dashboard()

    def show_forgot(self):
        self.clear_screen()

        card = ctk.CTkFrame(self, width=420, height=400)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        ctk.CTkLabel(
            card, text="Reset Password",
            font=ctk.CTkFont(size=26, weight="bold")
        ).pack(pady=25)

        self.forgot_email = ctk.CTkEntry(
            card, placeholder_text="Registered email", width=310
        )
        self.forgot_email.pack(pady=10)

        self.forgot_new = ctk.CTkEntry(
            card, placeholder_text="New password",
            show="*", width=310
        )
        self.forgot_new.pack(pady=10)

        ctk.CTkButton(
            card, text="Reset Password", width=310,
            command=self.reset_password
        ).pack(pady=12)

        ctk.CTkButton(
            card, text="Back to Login",
            fg_color="transparent", border_width=1,
            command=self.show_login
        ).pack(pady=5)

    def reset_password(self):
        email = self.forgot_email.get().strip().lower()
        password = self.forgot_new.get()

        if email not in self.data["users"]:
            messagebox.showerror("Error", "Account not found.")
            return

        if len(password) < 6:
            messagebox.showerror("Error", "Password must have at least 6 characters.")
            return

        salt, hashed = make_password_hash(password)
        self.data["users"][email]["salt"] = salt
        self.data["users"][email]["password_hash"] = hashed

        save_data(self.data)
        messagebox.showinfo("Success", "Password updated.")
        self.show_login()

    def show_dashboard(self):
        self.clear_screen()

        shell = ctk.CTkFrame(self, corner_radius=0)
        shell.pack(fill="both", expand=True)

        sidebar = ctk.CTkFrame(shell, width=235, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        user = self.data["users"][self.current_user]

        ctk.CTkLabel(
            sidebar, text="🏠 HomeCare",
            font=ctk.CTkFont(size=25, weight="bold")
        ).pack(pady=(22, 5))

        ctk.CTkLabel(
            sidebar, text=user["name"], text_color="gray"
        ).pack(pady=(0, 15))

        main = ctk.CTkFrame(shell, corner_radius=0)
        main.pack(side="left", fill="both", expand=True)

        top = ctk.CTkFrame(main, height=60, corner_radius=0)
        top.pack(fill="x")
        top.pack_propagate(False)

        ctk.CTkLabel(
            top, text="Home Maintenance Dashboard",
            font=ctk.CTkFont(size=21, weight="bold")
        ).pack(side="left", padx=20)

        self.content = ctk.CTkScrollableFrame(main)
        self.content.pack(fill="both", expand=True, padx=15, pady=15)

        menu = [
            ("Dashboard", self.page_dashboard),
            ("My Maintenance", self.page_tasks),
            ("Reminders & Notifications", self.page_reminders),
            ("Bills & Payments", self.page_bills),
            ("My Appliances", self.page_appliances),
            ("Warranty Tracker", self.page_warranty),
            ("Expense Management", self.page_expenses),
            ("Maintenance History", self.page_history),
            ("Service Providers", self.page_providers),
            ("AI Maintenance Assistant", self.page_ai),
            ("Reports & Export", self.page_reports),
            ("My Profile", self.page_profile),
            ("Settings", self.page_settings),
        ]

        for label, command in menu:
            ctk.CTkButton(
                sidebar, text=label, anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray80", "gray25"),
                command=command
            ).pack(fill="x", padx=9, pady=3)

        ctk.CTkButton(
            sidebar, text="Logout", fg_color="#b83232",
            command=self.logout
        ).pack(side="bottom", fill="x", padx=10, pady=15)

        self.page_dashboard()

    def page_title(self, title, subtitle=""):
        for widget in self.content.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.content, text=title,
            font=ctk.CTkFont(size=27, weight="bold")
        ).pack(anchor="w", pady=(8, 3))

        if subtitle:
            ctk.CTkLabel(
                self.content, text=subtitle, text_color="gray"
            ).pack(anchor="w", pady=(0, 15))

    def page_dashboard(self):
        self.page_title("Dashboard", "Overview of your home maintenance")

        pending = sum(
            1 for task in self.data["tasks"]
            if task.get("status") != "Completed"
        )

        due = sum(
            1 for task in self.data["tasks"]
            if task.get("status") != "Completed"
            and task.get("due_date", "9999") <= date.today().isoformat()
        )

        cards = ctk.CTkFrame(self.content, fg_color="transparent")
        cards.pack(fill="x")

        for label, value in [
            ("Total Tasks", len(self.data["tasks"])),
            ("Pending Tasks", pending),
            ("Due / Overdue", due),
            ("Appliances", len(self.data["appliances"]))
        ]:
            card = ctk.CTkFrame(cards)
            card.pack(side="left", expand=True, fill="x", padx=5, pady=5)
            ctk.CTkLabel(card, text=label, text_color="gray").pack(pady=(15, 5))
            ctk.CTkLabel(
                card, text=str(value),
                font=ctk.CTkFont(size=28, weight="bold")
            ).pack(pady=(0, 15))

        ctk.CTkLabel(
            self.content, text="Upcoming Maintenance",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w", pady=(25, 10))

        tasks = sorted(
            [t for t in self.data["tasks"] if t.get("status") != "Completed"],
            key=lambda t: t.get("due_date", "9999")
        )

        if not tasks:
            ctk.CTkLabel(
                self.content, text="No pending tasks. Add your first task!",
                text_color="gray"
            ).pack(anchor="w")
        else:
            for task in tasks[:8]:
                ctk.CTkLabel(
                    self.content,
                    text=f'{task["title"]}  |  Due: {task["due_date"]}  |  {task["status"]}',
                    anchor="w"
                ).pack(fill="x", pady=5)

        ctk.CTkButton(
            self.content, text="+ Add Maintenance Task",
            command=self.page_tasks
        ).pack(anchor="w", pady=18)

    def page_tasks(self):
        self.page_title("My Maintenance", "Add, complete, and delete maintenance tasks")

        form = ctk.CTkFrame(self.content)
        form.pack(fill="x", pady=8)

        self.task_title = ctk.CTkEntry(
            form, placeholder_text="Task title", width=230
        )
        self.task_title.grid(row=0, column=0, padx=7, pady=8)

        self.task_category = ctk.CTkComboBox(
            form, values=["Cleaning", "Repair", "Inspection", "Plumbing", "Electrical", "Other"],
            width=150
        )
        self.task_category.set("Cleaning")
        self.task_category.grid(row=0, column=1, padx=7, pady=8)

        self.task_due = ctk.CTkEntry(
            form, placeholder_text="YYYY-MM-DD", width=150
        )
        self.task_due.insert(0, (date.today() + timedelta(days=7)).isoformat())
        self.task_due.grid(row=0, column=2, padx=7, pady=8)

        ctk.CTkButton(
            form, text="Add Task", command=self.add_task
        ).grid(row=0, column=3, padx=7, pady=8)

        for task in list(self.data["tasks"]):
            box = ctk.CTkFrame(self.content)
            box.pack(fill="x", pady=4)

            ctk.CTkLabel(
                box,
                text=f'{task["title"]} | {task["category"]} | Due: {task["due_date"]} | {task["status"]}',
                anchor="w", wraplength=500
            ).pack(side="left", fill="x", expand=True, padx=10, pady=10)

            ctk.CTkButton(
                box, text="Complete", width=85,
                command=lambda t=task: self.complete_task(t)
            ).pack(side="right", padx=4, pady=5)

            ctk.CTkButton(
                box, text="Delete", width=70,
                fg_color="#b83232",
                command=lambda t=task: self.delete_record("tasks", t, self.page_tasks)
            ).pack(side="right", padx=4, pady=5)

    def add_task(self):
        title = self.task_title.get().strip()
        due = self.task_due.get().strip()

        if not title:
            messagebox.showerror("Error", "Enter a task title.")
            return

        try:
            datetime.strptime(due, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Enter date as YYYY-MM-DD.")
            return

        self.data["tasks"].append({
            "id": secrets.token_hex(5),
            "title": title,
            "category": self.task_category.get(),
            "due_date": due,
            "status": "Pending"
        })

        save_data(self.data)
        self.page_tasks()

    def complete_task(self, task):
        task["status"] = "Completed"

        self.data["history"].append({
            "date": date.today().isoformat(),
            "title": task["title"],
            "type": "Maintenance completed"
        })

        save_data(self.data)
        self.page_tasks()

    def delete_record(self, key, item, refresh):
        if messagebox.askyesno("Confirm", "Delete this record?"):
            self.data[key].remove(item)
            save_data(self.data)
            refresh()

    def page_reminders(self):
        self.page_title("Reminders & Notifications", "Tasks due today or overdue")

        today = date.today().isoformat()
        tasks = [
            t for t in self.data["tasks"]
            if t.get("status") != "Completed"
            and t.get("due_date", "9999") <= today
        ]

        if not tasks:
            ctk.CTkLabel(
                self.content, text="No tasks due today. You are all caught up!",
                text_color="#16a34a"
            ).pack(anchor="w")
        else:
            for task in tasks:
                ctk.CTkLabel(
                    self.content,
                    text=f'{task["title"]} — Due: {task["due_date"]}',
                    anchor="w"
                ).pack(fill="x", pady=5)

    def generic_page(self, title, subtitle, key, fields, labels):
        self.page_title(title, subtitle)

        form = ctk.CTkFrame(self.content)
        form.pack(fill="x", pady=8)

        entries = {}

        for index, (field, label) in enumerate(zip(fields, labels)):
            entry = ctk.CTkEntry(form, placeholder_text=label, width=190)
            entry.grid(
                row=index // 3, column=index % 3,
                padx=6, pady=7, sticky="ew"
            )
            entries[field] = entry

        def add_record():
            record = {
                field: entries[field].get().strip()
                for field in fields
            }

            if not record[fields[0]]:
                messagebox.showerror("Error", f"Enter {labels[0]}.")
                return

            record["id"] = secrets.token_hex(5)
            self.data[key].append(record)
            save_data(self.data)
            self.generic_page(title, subtitle, key, fields, labels)

        ctk.CTkButton(
            form, text="Add Record", command=add_record
        ).grid(row=(len(fields) - 1) // 3 + 1, column=0, padx=6, pady=8)

        for record in list(self.data[key]):
            line = " | ".join(
                f"{label}: {record.get(field, '-')}"
                for field, label in zip(fields, labels)
            )

            box = ctk.CTkFrame(self.content)
            box.pack(fill="x", pady=4)

            ctk.CTkLabel(
                box, text=line, anchor="w", wraplength=650
            ).pack(side="left", fill="x", expand=True, padx=10, pady=10)

            ctk.CTkButton(
                box, text="Delete", width=75, fg_color="#b83232",
                command=lambda r=record: self.delete_record(
                    key, r,
                    lambda: self.generic_page(title, subtitle, key, fields, labels)
                )
            ).pack(side="right", padx=8, pady=5)

    def page_bills(self):
        self.generic_page(
            "Bills & Payments", "Track household bills",
            "bills",
            ["bill", "amount", "due_date", "status"],
            ["Bill name", "Amount", "Due date", "Paid/Pending"]
        )

    def page_appliances(self):
        self.generic_page(
            "My Appliances", "Save appliance details",
            "appliances",
            ["name", "brand", "purchase_date", "warranty_end"],
            ["Appliance", "Brand", "Purchase date", "Warranty end date"]
        )

    def page_warranty(self):
        self.page_title("Warranty Tracker", "View warranty dates for your appliances")

        if not self.data["appliances"]:
            ctk.CTkLabel(self.content, text="Add appliances in My Appliances first.").pack(anchor="w")
            return

        for item in self.data["appliances"]:
            ctk.CTkLabel(
                self.content,
                text=f'{item.get("name", "-")} | {item.get("brand", "-")} | Warranty ends: {item.get("warranty_end", "-")}',
                anchor="w"
            ).pack(fill="x", pady=6)

    def page_expenses(self):
        self.generic_page(
            "Expense Management", "Track maintenance expenses",
            "expenses",
            ["description", "amount", "category"],
            ["Description", "Amount", "Category"]
        )

    def page_history(self):
        self.page_title("Maintenance History", "Completed maintenance records")

        if not self.data["history"]:
            ctk.CTkLabel(self.content, text="No completed tasks yet.").pack(anchor="w")

        for item in reversed(self.data["history"]):
            ctk.CTkLabel(
                self.content,
                text=f'{item["date"]} | {item["title"]} | {item["type"]}',
                anchor="w"
            ).pack(fill="x", pady=5)

    def page_providers(self):
        self.generic_page(
            "Service Providers", "Store technician contact details",
            "providers",
            ["name", "service", "phone"],
            ["Provider name", "Service type", "Phone number"]
        )

    def page_ai(self):
        self.page_title(
            "AI Maintenance Assistant",
            "Basic offline tips; no external AI service is connected"
        )

        self.ai_input = ctk.CTkEntry(
            self.content, placeholder_text="e.g. AC, plumbing, electrical, refrigerator",
            width=450
        )
        self.ai_input.pack(anchor="w", pady=10)

        self.ai_output = ctk.CTkTextbox(self.content, width=650, height=200)
        self.ai_output.pack(fill="x", pady=10)

        ctk.CTkButton(
            self.content, text="Get Suggestions",
            command=self.ai_suggest
        ).pack(anchor="w")

    def ai_suggest(self):
        query = self.ai_input.get().lower()

        if "ac" in query or "air conditioner" in query:
            tips = [
                "Clean the AC filter regularly.",
                "Keep the outdoor unit clear.",
                "Call a technician if cooling is weak."
            ]
        elif "plumb" in query or "leak" in query or "tap" in query:
            tips = [
                "Turn off the water supply if the leak is serious.",
                "Check visible joints carefully.",
                "Call a qualified plumber if the leak continues."
            ]
        elif "electric" in query or "wire" in query:
            tips = [
                "Do not touch exposed wires.",
                "Switch off power if safe to do so.",
                "Call a qualified electrician."
            ]
        elif "fridge" in query or "refrigerator" in query:
            tips = [
                "Keep ventilation space around the refrigerator.",
                "Check the door seals.",
                "Contact a technician if it stops cooling."
            ]
        else:
            tips = [
                "Inspect for leaks monthly.",
                "Follow manufacturer maintenance schedules.",
                "Check smoke alarms regularly.",
                "Use qualified professionals for electrical or gas problems."
            ]

        self.ai_output.delete("1.0", "end")
        self.ai_output.insert("1.0", "\n".join("• " + tip for tip in tips))

    def page_reports(self):
        self.page_title("Reports & Export", "View a simple summary of saved records")

        for label, key in [
            ("Maintenance tasks", "tasks"),
            ("Bills", "bills"),
            ("Appliances", "appliances"),
            ("Expenses", "expenses"),
            ("Service providers", "providers")
        ]:
            ctk.CTkLabel(
                self.content,
                text=f"{label}: {len(self.data[key])} record(s)",
                anchor="w"
            ).pack(fill="x", pady=5)

    def page_profile(self):
        self.page_title("My Profile", "Update your personal details")

        profile = self.data["profile"]
        if not profile:
            profile = {
                "name": self.data["users"][self.current_user]["name"],
                "email": self.current_user,
                "phone": "",
                "address": ""
            }
            self.data["profile"] = profile

        entries = {}

        for key, label in [
            ("name", "Full name"),
            ("phone", "Phone"),
            ("address", "Address")
        ]:
            ctk.CTkLabel(self.content, text=label).pack(anchor="w", pady=(8, 2))
            entry = ctk.CTkEntry(self.content, width=450)
            entry.insert(0, profile.get(key, ""))
            entry.pack(anchor="w", pady=2)
            entries[key] = entry

        ctk.CTkLabel(
            self.content, text=f"Email: {self.current_user}"
        ).pack(anchor="w", pady=10)

        def save_profile():
            for key, entry in entries.items():
                profile[key] = entry.get().strip()

            self.data["users"][self.current_user]["name"] = (
                profile["name"] or self.data["users"][self.current_user]["name"]
            )

            save_data(self.data)
            messagebox.showinfo("Saved", "Profile updated.")
            self.show_dashboard()

        ctk.CTkButton(
            self.content, text="Save Profile", command=save_profile
        ).pack(anchor="w", pady=15)

    def page_settings(self):
        self.page_title("Settings", "Choose the app appearance")

        mode = ctk.CTkComboBox(
            self.content, values=["System", "Light", "Dark"], width=220
        )
        mode.set(self.data["settings"].get("appearance", "System"))
        mode.pack(anchor="w", pady=10)

        def apply_settings():
            selected = mode.get()
            ctk.set_appearance_mode(selected)
            self.data["settings"]["appearance"] = selected
            save_data(self.data)
            messagebox.showinfo("Settings", "Settings saved.")

        ctk.CTkButton(
            self.content, text="Apply Settings",
            command=apply_settings
        ).pack(anchor="w", pady=8)

        ctk.CTkLabel(
            self.content,
            text="Storage: local data.json file. Keep a backup of this file.",
            text_color="gray"
        ).pack(anchor="w", pady=12)

    def logout(self):
        save_data(self.data)
        self.current_user = None
        self.show_login()


if __name__ == "__main__":
    app = HomeMaintenanceApp()
    app.mainloop()
