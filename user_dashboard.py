import customtkinter as ctk
from tkinter import messagebox, filedialog
from tkinter import ttk
from database import connect_database
from datetime import datetime
from PIL import Image, ImageTk
import os
import shutil

def _normalize_match_text(value):
    return " ".join(str(value or "").lower().strip().split())
    
def _text_match_score(a, b):
    a = _normalize_match_text(a)
    b = _normalize_match_text(b)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    if a in b or b in a:
        return 0.8
    aw = set(a.replace(",", " ").split())
    bw = set(b.replace(",", " ").split())
    return len(aw & bw) / max(len(aw), len(bw)) if aw and bw else 0.0

def _calculate_match_score(lost, found):
    score = _text_match_score(lost["item_name"], found["item_name"]) * 35
    score += _text_match_score(lost["category"], found["category"]) * 20
    if lost["color"] and found["color"]:
        score += _text_match_score(lost["color"], found["color"]) * 15
    score += _text_match_score(lost["location"], found["location"]) * 15
    if lost["date"] and found["date"]:
        try:
            days = abs((lost["date"] - found["date"]).days)
            score += 10 if days == 0 else 7 if days == 1 else 4 if days <= 3 else 0
        except Exception:
            pass
    score += _text_match_score(lost["description"], found["description"]) * 5
    return round(score, 2)

def generate_possible_matches(cursor):
    cursor.execute(
        "SELECT lost_item_id, user_id, item_name, category, description, color, location_lost, date_lost "
        "FROM lost_items WHERE status IN ('ACTIVE','MATCHED')"
    )
    lost_rows = cursor.fetchall()
    cursor.execute(
        "SELECT found_item_id, item_name, category, description, color, location_found, date_found "
        "FROM found_items WHERE status IN ('ACTIVE','MATCHED')"
    )
    found_rows = cursor.fetchall()
    for lost in lost_rows:
        ld = {
            "id": lost[0],
            "user_id": lost[1],
            "item_name": lost[2],
            "category": lost[3],
            "description": lost[4],
            "color": lost[5],
            "location": lost[6],
            "date": lost[7],
        }
        for found in found_rows:
            fd = {
                "id": found[0],
                "item_name": found[1],
                "category": found[2],
                "description": found[3],
                "color": found[4],
                "location": found[5],
                "date": found[6],
            }
            score = _calculate_match_score(ld, fd)
            if score < 40:
                continue
            cursor.execute(
                "SELECT match_id FROM matches WHERE lost_item_id=%s AND found_item_id=%s LIMIT 1",
                (ld["id"], fd["id"]),
            )
            existing = cursor.fetchone()
            if existing:
                cursor.execute(
                    "UPDATE matches SET match_score=%s WHERE match_id=%s AND match_status='POSSIBLE'",
                    (score, existing[0]),
                )
            else:
                cursor.execute(
                    "INSERT INTO matches (lost_item_id, found_item_id, match_score, match_status) "
                    "VALUES (%s, %s, %s, 'POSSIBLE')",
                    (ld["id"], fd["id"], score),
                )
                cursor.execute(
                    "INSERT INTO notifications (user_id, title, message, notification_type) "
                    "VALUES (%s, %s, %s, %s)",
                    (
                        ld["user_id"],
                        "Possible Match Found",
                        f"A possible match was found for your lost item: {ld['item_name']}.",
                        "MATCH",
                    ),
                )

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

PRIMARY = "#0B1F3A"
PRIMARY_LIGHT = "#2563EB"
PRIMARY_HOVER = "#1D4ED8"
PRIMARY_SOFT = "#EAF1FF"
PRIMARY_SOFT_BORDER = "#D6E4FF"

SKY = "#0891B2"
SKY_HOVER = "#0E7490"

INDIGO = "#4F46E5"
INDIGO_HOVER = "#4338CA"

NAVY_ACCENT = "#1E3A8A"
NAVY_ACCENT_HOVER = "#17296B"

SIDEBAR_HOVER = "#16304F"
SIDEBAR_DIVIDER = "#1D3A5C"
SIDEBAR_TEXT_DIM = "#7FA8D9"
SIDEBAR_TEXT_MUTED = "#9DBEE6"

NEUTRAL = "#64748B"
NEUTRAL_HOVER = "#475569"
DANGER = "#DC2626"
DANGER_HOVER = "#B91C1C"

BG = "#F1F5F9"
CARD = "white"
BORDER = "#E2E8F0"
TEXT_MAIN = "#0F172A"
TEXT_SUB = "#64748B"


def open_user_dashboard(user_id, full_name):
    window = ctk.CTk()
    window.title("Claimsure • User Dashboard")
    window.geometry("1200x750")
    window.minsize(1050, 680)

    window.grid_columnconfigure(1, weight=1)
    window.grid_rowconfigure(0, weight=1)

    tree_style = ttk.Style(window)
    tree_style.theme_use("clam")
    tree_style.configure(
        "Treeview",
        background="white",
        fieldbackground="white",
        foreground=TEXT_MAIN,
        rowheight=30,
        borderwidth=0,
        font=("Segoe UI", 11),
    )
    tree_style.configure(
        "Treeview.Heading",
        background=PRIMARY_SOFT,
        foreground=PRIMARY,
        font=("Segoe UI", 11, "bold"),
        borderwidth=0,
        relief="flat",
    )
    tree_style.map("Treeview.Heading", background=[("active", PRIMARY_SOFT_BORDER)])
    tree_style.map(
        "Treeview",
        background=[("selected", PRIMARY_LIGHT)],
        foreground=[("selected", "white")],
    )

    sidebar = ctk.CTkFrame(window, width=240, corner_radius=0, fg_color=PRIMARY)
    sidebar.grid(row=0, column=0, sticky="nsew")
    sidebar.grid_propagate(False)

    LOGO_SIZE = 300
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "wheel.jpg")

    def _emoji_logo():
        ctk.CTkLabel(
            sidebar, text="🎡",
            font=ctk.CTkFont(family="Segoe UI Emoji", size=76),
            fg_color="transparent"
        ).grid(row=0, column=0, pady=(24, 2), padx=20)

    if os.path.exists(logo_path):
        try:
            logo_image = Image.open(logo_path)
            logo_image.thumbnail((LOGO_SIZE, LOGO_SIZE), Image.Resampling.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_image)

            logo_label = ctk.CTkLabel(
                sidebar, image=logo_photo, text="", fg_color="transparent"
            )
            logo_label.image = logo_photo
            logo_label.grid(row=0, column=0, pady=(24, 2), padx=20)
        except Exception:
            _emoji_logo()
    else:
        _emoji_logo()

    ctk.CTkLabel(
        sidebar,
        text="CLAIMSURE",
        font=ctk.CTkFont(family="Segoe UI", size=19, weight="bold"),
        text_color="white"
    ).grid(row=1, column=0, padx=20)

    ctk.CTkLabel(
        sidebar,
        text="Administrator Panel",
        font=ctk.CTkFont(family="Segoe UI", size=11),
        text_color=SIDEBAR_TEXT_DIM
    ).grid(row=2, column=0, pady=(2, 14), padx=20)

    user_chip = ctk.CTkFrame(sidebar, fg_color=SIDEBAR_HOVER, corner_radius=10)
    user_chip.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 16))
    ctk.CTkLabel(
        user_chip, text="SIGNED IN AS",
        font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
        text_color=SIDEBAR_TEXT_DIM
    ).pack(anchor="w", padx=12, pady=(8, 0))
    ctk.CTkLabel(
        user_chip, text=full_name,
        font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        text_color="white", wraplength=180, justify="left"
    ).pack(anchor="w", padx=12, pady=(0, 8))

    ctk.CTkFrame(sidebar, height=1, fg_color=SIDEBAR_DIVIDER).grid(
        row=4, column=0, sticky="ew", padx=20, pady=(0, 16)
    )

    nav_btn_kwargs = {
        "height": 48,
        "corner_radius": 12,
        "fg_color": "transparent",
        "hover_color": SIDEBAR_HOVER,
        "text_color": "white",
        "anchor": "w",
        "font": ctk.CTkFont(family="Segoe UI", size=14)
    }

    nav_buttons = {}

    def set_active(key):
        for nav_key, nav_btn in nav_buttons.items():
            nav_btn.configure(fg_color=PRIMARY_LIGHT if nav_key == key else "transparent")

    nav_buttons["home"] = ctk.CTkButton(sidebar, text="🏠  Home", command=lambda: show_home(), **nav_btn_kwargs)
    nav_buttons["home"].grid(row=5, column=0, sticky="ew", padx=14, pady=5)

    nav_buttons["report_lost"] = ctk.CTkButton(sidebar, text="🔍  Report Lost Item", command=lambda: show_report_lost(), **nav_btn_kwargs)
    nav_buttons["report_lost"].grid(row=6, column=0, sticky="ew", padx=14, pady=5)

    nav_buttons["report_found"] = ctk.CTkButton(sidebar, text="📦  Report Found Item", command=lambda: show_report_found(), **nav_btn_kwargs)
    nav_buttons["report_found"].grid(row=7, column=0, sticky="ew", padx=14, pady=5)

    nav_buttons["search"] = ctk.CTkButton(sidebar, text="🔎  Search Items", command=lambda: show_search_items(), **nav_btn_kwargs)
    nav_buttons["search"].grid(row=8, column=0, sticky="ew", padx=14, pady=5)

    nav_buttons["claims"] = ctk.CTkButton(sidebar, text="📋  My Claims", command=lambda: show_claims(), **nav_btn_kwargs)
    nav_buttons["claims"].grid(row=9, column=0, sticky="ew", padx=14, pady=5)

    nav_buttons["notifications"] = ctk.CTkButton(sidebar, text="🔔  Notifications", command=lambda: show_notifications(), **nav_btn_kwargs)
    nav_buttons["notifications"].grid(row=10, column=0, sticky="ew", padx=14, pady=5)

    sidebar.grid_rowconfigure(11, weight=1)

    ctk.CTkButton(
        sidebar, text="🚪  Logout", height=48, corner_radius=12,
        fg_color=DANGER, hover_color=DANGER_HOVER, text_color="white",
        font=ctk.CTkFont(family="Segoe UI", size=14),
        command=lambda: logout()
    ).grid(row=12, column=0, sticky="ew", padx=14, pady=(5, 20))

    main = ctk.CTkFrame(window, fg_color=BG, corner_radius=0)
    main.grid(row=0, column=1, sticky="nsew")
    main.grid_columnconfigure(0, weight=1)
    main.grid_rowconfigure(1, weight=1)

    header = ctk.CTkFrame(main, height=70, fg_color="white", corner_radius=0, border_width=0)
    header.grid(row=0, column=0, sticky="ew")
    header.grid_propagate(False)
    ctk.CTkFrame(main, height=1, fg_color=BORDER).grid(row=0, column=0, sticky="sew")

    header_label = ctk.CTkLabel(
        header,
        text="Amusement Park Lost & Found System",
        font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
        text_color=PRIMARY,
    )
    header_label.pack(side="left", padx=30, pady=20)

    content = ctk.CTkFrame(main, fg_color="transparent")
    content.grid(row=1, column=0, sticky="nsew", padx=40, pady=30)
    content.grid_columnconfigure(0, weight=1)

    def clear_content():
        for widget in content.winfo_children():
            widget.destroy()
        for row in range(6):
            content.grid_rowconfigure(row, weight=0)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=0)
