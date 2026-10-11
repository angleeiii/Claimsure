import tkinter as tk
from tkinter import messagebox
from database import connect_database

from user_dashboard import open_user_dashboard
from admin_dashboard import open_admin_dashboard



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


def make_round_button(parent, text, command, fill="#1E88E5", hover="#1565C0", fg="white"):
    holder = tk.Frame(parent, bg="white", height=BTN_H)
    holder.pack(fill="x", pady=(8, 0))
    holder.pack_propagate(False)

    cv = tk.Canvas(holder, bg="white", highlightthickness=0, height=BTN_H)
    cv.pack(fill="both", expand=True)

    rect = round_rect(cv, 1, 1, 200, BTN_H - 1, 14, fill=fill, outline="")
    label = cv.create_text(100, BTN_H // 2, text=text,
                           fill=fg, font=("Segoe UI", 12, "bold"))

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


def login():
    username = username_entry.get().strip()
    password = password_entry.get()

    if username == "Enter your username":
        username = ""
    if password == "Enter your password":
        password = ""

    if not username or not password:
        messagebox.showwarning(
            "Missing Information",
            "Please enter your username and password."
        )
        return

    connection = connect_database()
    if connection is None:
        return

    cursor = connection.cursor()
    query = """
        SELECT user_id, full_name, role
        FROM users
        WHERE username = %s AND password = %s
    """
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if user:
        user_id, full_name, role = user
        messagebox.showinfo("Login Successful", f"Welcome, {full_name}!")
        window.destroy()

        if role == "ADMIN":
            open_admin_dashboard(user_id, full_name)
        else:
            open_user_dashboard(user_id, full_name)
    else:
        messagebox.showerror(
            "Login Failed",
            "Invalid username or password."
        )


def open_register():
    window.destroy()
    import register


def forgot_password():
    messagebox.showinfo(
        "Forgot Password",
        "Please contact the Lost & Found office or an administrator\nto reset your password."
    )



window = tk.Tk()
window.title("Claimsure • Login")
window.geometry("420x560")

window.resizable(True, True)
window.minsize(360, 500)

window.configure(bg="white")

card = tk.Frame(window, bg="white")
card.pack(fill="both", expand=True, padx=30, pady=10)

tk.Label(card, text="🎡", font=("Segoe UI Emoji", 32),
         bg="white", fg="#1976D2").pack(pady=(10, 0))

tk.Label(card, text="CLAIMSURE",
         font=("Segoe UI", 20, "bold"),
         bg="white", fg="#0D47A1").pack(pady=(4, 0))

tk.Label(card, text="Amusement Park Lost & Found System",
         font=("Segoe UI", 10),
         bg="white", fg="#546E7A").pack(pady=(0, 16))

username_entry = make_field(card, "Username", "👤", "Enter your username")
password_entry = make_field(card, "Password", "🔒", "Enter your password", secret=True)

forgot = tk.Label(card, text="Forgot Password?",
                  font=("Segoe UI", 9, "underline"),
                  bg="white", fg="#1976D2", cursor="hand2")
forgot.pack(anchor="e", pady=(0, 4))
forgot.bind("<Button-1>", lambda e: forgot_password())

make_round_button(card, "LOGIN", login)
make_round_button(card, "REGISTER", open_register,
                  fill="#E3F2FD", hover="#BBDEFB", fg="#1565C0")

tk.Label(card,
         text="Lost something? Found something?\nClaimsure helps you get it back.",
         font=("Segoe UI", 8),
         bg="white",
         fg="#90A4AE",
         justify="center").pack(pady=(14, 0))

window.bind("<Return>", lambda event: login())

center_window(window)

window.mainloop()