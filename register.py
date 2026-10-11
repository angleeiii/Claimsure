import tkinter as tk
from tkinter import messagebox
from database import connect_database


def round_points(x1, y1, x2, y2, r):
    return [
        x1 + r, y1,  x2 - r, y1,  x2, y1,  x2, y1 + r,
        x2, y2 - r,  x2, y2,  x2 - r, y2,  x1 + r, y2,
        x1, y2,  x1, y2 - r,  x1, y1 + r,  x1, y1
    ]


def round_rect(canvas, x1, y1, x2, y2, r, **kw):
    return canvas.create_polygon(round_points(x1, y1, x2, y2, r), smooth=True, **kw)


def add_placeholder(entry, text):
    def on_focus_in(e):
        if entry.get() == text:
            entry.delete(0, "end")
            entry.config(fg="#37474F")

    def on_focus_out(e):
        if not entry.get().strip():
            entry.insert(0, text)
            entry.config(fg="#B0BEC5")

    entry.insert(0, text)
    entry.config(fg="#B0BEC5")
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)


FIELD_H = 42


def make_field(parent, label_text, icon, placeholder, secret=False):
    tk.Label(
        parent,
        text=label_text,
        font=("Segoe UI", 10),
        bg="white",
        fg="#37474F",
        anchor="w"
    ).pack(fill="x", pady=(0, 2))

    holder = tk.Frame(parent, bg="white", height=FIELD_H)
    holder.pack(fill="x", pady=(0, 12))
    holder.pack_propagate(False)

    cv = tk.Canvas(holder, bg="white", highlightthickness=0, height=FIELD_H)
    cv.pack(fill="both", expand=True)

    border = round_rect(cv, 1, 1, 200, FIELD_H - 1, 12,
                        fill="#F5F9FC", outline="#CFD8DC", width=1)
    icon_id = cv.create_text(22, FIELD_H // 2, text=icon,
                             font=("Segoe UI Emoji", 11), fill="#CFD8DC")

    entry = tk.Entry(
        holder,
        font=("Segoe UI", 11),
        relief="flat",
        bd=0,
        bg="#F5F9FC",
        show="•" if secret else "",
        insertbackground="#1976D2",
        highlightthickness=0
    )
    entry.place(x=40, y=(FIELD_H - 30) // 2, width=140, height=30)

    def on_resize(event):
        w = max(event.width, 60)
        cv.coords(border, *round_points(1, 1, w - 1, FIELD_H - 1, 12))
        cv.coords(icon_id, 22, FIELD_H // 2)
        entry.place_configure(width=w - 52)

    cv.bind("<Configure>", on_resize)

    entry.bind("<FocusIn>",  lambda e: cv.itemconfig(border, outline="#1976D2"))
    entry.bind("<FocusOut>", lambda e: cv.itemconfig(border, outline="#CFD8DC"))

    add_placeholder(entry, placeholder)
    return entry


BTN_H = 46


def make_round_button(parent, text, command, fill="#1E88E5", hover="#1565C0"):
    holder = tk.Frame(parent, bg="white", height=BTN_H)
    holder.pack(fill="x", pady=(8, 0))
    holder.pack_propagate(False)

    cv = tk.Canvas(holder, bg="white", highlightthickness=0, height=BTN_H)
    cv.pack(fill="both", expand=True)

    rect = round_rect(cv, 1, 1, 200, BTN_H - 1, 14, fill=fill, outline="")
    label = cv.create_text(100, BTN_H // 2, text=text,
                           fill="white", font=("Segoe UI", 12, "bold"))

    def on_resize(event):
        w = max(event.width, 60)
        cv.coords(rect, *round_points(1, 1, w - 1, BTN_H - 1, 14))
        cv.coords(label, w // 2, BTN_H // 2)

    cv.bind("<Configure>", on_resize)

    cv.bind("<Enter>", lambda e: cv.itemconfig(rect, fill=hover))
    cv.bind("<Leave>", lambda e: cv.itemconfig(rect, fill=fill))
    for item in (rect, label):
        cv.tag_bind(item, "<Button-1>", lambda e: command())
    cv.config(cursor="hand2")

    return cv


def center_window(win):
    win.update_idletasks()
    w = win.winfo_width()
    h = win.winfo_height()
    x = (win.winfo_screenwidth() - w) // 2
    y = (win.winfo_screenheight() - h) // 2
    win.geometry(f"+{x}+{y}")


def register_user():
    full_name = full_name_entry.get().strip()
    username = username_entry.get().strip()
    password = password_entry.get()
    confirm_password = confirm_password_entry.get()
    contact_number = contact_entry.get().strip()

    if full_name == "e.g. eom seonghyeon":
        full_name = ""
    if username == "e.g. seaneom":
        username = ""
    if contact_number == "e.g. 0900 000 0000":
        contact_number = ""

    if not full_name or not username or not password or not confirm_password:
        messagebox.showwarning("Missing Information",
                               "Please fill in all required fields.")
        return

    if password != confirm_password:
        messagebox.showerror("Password Error", "Passwords do not match.")
        return

    if len(username) < 4:
        messagebox.showwarning("Invalid Username",
                               "Username must be at least 4 characters.")
        return

    if len(password) < 6:
        messagebox.showwarning("Invalid Password",
                               "Password must be at least 6 characters.")
        return

    connection = connect_database()
    if connection is None:
        return

    cursor = connection.cursor()

    cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        messagebox.showerror("Registration Failed", "Username already exists.")
        cursor.close()
        connection.close()
        return

    cursor.execute(
        "INSERT INTO users (full_name, username, password, role, contact_number)"
        " VALUES (%s, %s, %s, 'USER', %s)",
        (full_name, username, password, contact_number)
    )
    connection.commit()
    cursor.close()
    connection.close()

    messagebox.showinfo("Registration Successful",
                        "Your account has been created successfully!")
    open_login()


def open_login():
    window.destroy()
    import login


window = tk.Tk()
window.title("Claimsure • Register")
window.geometry("420x640")


window.resizable(True, True)
window.minsize(360, 560)

window.configure(bg="white")

card = tk.Frame(window, bg="white")
card.pack(fill="both", expand=True, padx=30, pady=10)

tk.Label(card, text="🧱🔍", font=("Segoe UI Emoji", 32),
         bg="white", fg="#1976D2").pack(pady=(10, 0))

tk.Label(card, text="Create an Account",
         font=("Segoe UI", 20, "bold"),
         bg="white", fg="#0D47A1").pack(pady=(4, 16))

full_name_entry = make_field(card, "Full Name", "👤", "e.g. eom seonghyeon")
username_entry = make_field(card, "Username", "@", "e.g. seaneom")
password_entry = make_field(card, "Password", "🔒", "Minimum 8 characters", secret=True)
confirm_password_entry = make_field(card, "Confirm Password", "🔒", "Repeat your password", secret=True)
contact_entry = make_field(card, "Contact Number (Optional)", "📞", "e.g. 0900 000 0000")

make_round_button(card, "REGISTER", register_user)

footer = tk.Frame(card, bg="white")
footer.pack(pady=(14, 0))

tk.Label(footer, text="Already have an account?",
         font=("Segoe UI", 9), bg="white", fg="#78909C").pack(side="left")

login_link = tk.Label(footer, text=" Login", font=("Segoe UI", 9, "underline"),
                      bg="white", fg="#1E88E5", cursor="hand2")
login_link.pack(side="left")
login_link.bind("<Button-1>", lambda e: open_login())

center_window(window)

window.mainloop()