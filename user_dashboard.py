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

 def section_card(parent, **kwargs):
        defaults = {
            "fg_color": CARD,
            "corner_radius": 16,
            "border_width": 1,
            "border_color": BORDER,
        }
        defaults.update(kwargs)
        return ctk.CTkFrame(parent, **defaults)

    def show_home():
        clear_content()
        header_label.configure(text="Amusement Park Lost & Found System")
        set_active("home")

        card = section_card(content)
        card.grid(row=0, column=0, sticky="ew", pady=(0, 25))

        ctk.CTkLabel(
            card,
            text="👋  Welcome to Claimsure",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=PRIMARY,
        ).pack(anchor="w", padx=28, pady=(24, 4))
        ctk.CTkLabel(
            card,
            text="Use the sidebar to report, search, or manage your claims.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=TEXT_SUB,
        ).pack(anchor="w", padx=28, pady=(0, 24))

        ctk.CTkLabel(
            content,
            text="Quick Actions",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=TEXT_MAIN,
        ).grid(row=1, column=0, sticky="w", pady=(10, 12))

        actions = ctk.CTkFrame(content, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew")
        actions.grid_columnconfigure((0, 1), weight=1)

        def make_action_btn(parent, text, subtitle, icon, command, color, hover, row, col):
            btn = ctk.CTkButton(
                parent,
                height=72,
                corner_radius=16,
                fg_color=color,
                hover_color=hover,
                text=f"{icon}   {text}\n{subtitle}",
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                text_color="white",
                command=command,
            )
            btn.grid(row=row, column=col, sticky="ew", padx=8, pady=8)

        make_action_btn(
            actions, "Report Lost Item", "Log something you lost", "🔍",
            show_report_lost, PRIMARY_LIGHT, PRIMARY_HOVER, 0, 0,
        )
        make_action_btn(
            actions, "Report Found Item", "Hand in what you found", "📦",
            show_report_found, SKY, SKY_HOVER, 0, 1,
        )
        make_action_btn(
            actions, "Search Items", "Browse all active reports", "🔎",
            show_search_items, INDIGO, INDIGO_HOVER, 1, 0,
        )
        make_action_btn(
            actions, "My Claims", "Matches & claim status", "📋",
            show_claims, NAVY_ACCENT, NAVY_ACCENT_HOVER, 1, 1,
        )

        tip = ctk.CTkFrame(
            content, fg_color=PRIMARY_SOFT, corner_radius=12,
            border_width=1, border_color=PRIMARY_SOFT_BORDER,
        )
        tip.grid(row=3, column=0, sticky="ew", pady=(30, 0))
        ctk.CTkLabel(
            tip,
            text="💡  Tip: Always include clear descriptions and the location where the item was lost or found.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=PRIMARY_HOVER,
            wraplength=700,
            justify="left",
        ).pack(anchor="w", padx=20, pady=16)

    def build_report_form(kind):
        is_lost = kind == "lost"
        verb = "Lost" if is_lost else "Found"
        accent = PRIMARY_LIGHT if is_lost else SKY
        accent_hover = PRIMARY_HOVER if is_lost else SKY_HOVER

        card = section_card(content)
        card.grid(row=0, column=0, sticky="nsew")
        content.grid_rowconfigure(0, weight=1)
        card.grid_columnconfigure((0, 1), weight=1, uniform="form")

        selected_photo = [None]

        def field_label(text, row, col):
            ctk.CTkLabel(
                card, text=text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=TEXT_MAIN, anchor="w",
            ).grid(
                row=row, column=col, sticky="w",
                padx=(32, 12) if col == 0 else (12, 32), pady=(0, 3),
            )

        ctk.CTkLabel(
            card, text=f"REPORT {verb.upper()} ITEM",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=PRIMARY,
        ).grid(row=0, column=0, columnspan=2, padx=32, pady=(24, 2), sticky="w")

        ctk.CTkLabel(
            card, text=f"Enter the details of the item you {kind}.",
            font=ctk.CTkFont(family="Segoe UI", size=13), text_color=TEXT_SUB,
        ).grid(row=1, column=0, columnspan=2, padx=32, pady=(0, 16), sticky="w")

        field_label("Item Name", 2, 0)
        item_name_entry = ctk.CTkEntry(
            card, height=38, corner_radius=10, font=ctk.CTkFont(size=13),
            placeholder_text="e.g. Blue backpack",
        )
        item_name_entry.grid(row=3, column=0, sticky="ew", padx=(32, 12), pady=(0, 14))

        field_label("Category", 2, 1)
        category_var = ctk.StringVar()
        category_dropdown = ctk.CTkOptionMenu(
            card, variable=category_var,
            values=["Wallet", "Mobile Phone", "Bag", "ID / Card", "Keys",
                    "Clothing", "Jewelry", "Electronics", "Other"],
            height=38, corner_radius=10, font=ctk.CTkFont(size=13),
            fg_color=accent, button_color=accent_hover, button_hover_color=PRIMARY,
        )
        category_dropdown.grid(row=3, column=1, sticky="ew", padx=(12, 32), pady=(0, 14))
        category_dropdown.set("Select category")

        field_label("Color", 4, 0)
        color_entry = ctk.CTkEntry(
            card, height=38, corner_radius=10, font=ctk.CTkFont(size=13),
            placeholder_text="e.g. Navy blue",
        )
        color_entry.grid(row=5, column=0, sticky="ew", padx=(32, 12), pady=(0, 14))

        field_label(f"Location {verb}", 4, 1)
        location_var = ctk.StringVar()
        location_dropdown = ctk.CTkOptionMenu(
            card, variable=location_var,
            values=["Entrance", "Ferris Wheel", "Roller Coaster", "Food Court",
                    "Arcade", "Gift Shop", "Restroom", "Parking Area", "Other"],
            height=38, corner_radius=10, font=ctk.CTkFont(size=13),
            fg_color=accent, button_color=accent_hover, button_hover_color=PRIMARY,
        )
        location_dropdown.grid(row=5, column=1, sticky="ew", padx=(12, 32), pady=(0, 14))
        location_dropdown.set("Select location")

        field_label(f"Date {verb} (YYYY-MM-DD)", 6, 0)
        date_entry = ctk.CTkEntry(card, height=38, corner_radius=10, font=ctk.CTkFont(size=13))
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.grid(row=7, column=0, sticky="ew", padx=(32, 12), pady=(0, 14))

        field_label(f"Photo of {verb} Item", 6, 1)
        photo_frame = ctk.CTkFrame(
            card, fg_color=BG, corner_radius=10, border_width=1, border_color=BORDER,
        )
        photo_frame.grid(row=7, column=1, sticky="ew", padx=(12, 32), pady=(0, 14))
        photo_frame.grid_columnconfigure(1, weight=1)

        photo_label = ctk.CTkLabel(
            photo_frame, text="No photo selected",
            font=ctk.CTkFont(size=11), text_color=TEXT_SUB, anchor="w",
        )

        def select_photo():
            file_path = filedialog.askopenfilename(
                title=f"Select {verb} Item Photo",
                filetypes=[
                    ("Image Files", "*.jpg *.jpeg *.png"),
                    ("JPG Files", "*.jpg"),
                    ("PNG Files", "*.png"),
                ],
            )
            if file_path:
                selected_photo[0] = file_path
                file_name = os.path.basename(file_path)
                photo_label.configure(
                    text=f"Selected: {file_name}",
                    text_color=SKY_HOVER if not is_lost else PRIMARY_HOVER,
                )

        ctk.CTkButton(
            photo_frame, text="📷  UPLOAD", height=32, width=110, corner_radius=8,
            fg_color=accent, hover_color=accent_hover,
            font=ctk.CTkFont(size=12, weight="bold"), command=select_photo,
        ).grid(row=0, column=0, sticky="w", padx=6, pady=6)
        photo_label.grid(row=0, column=1, sticky="ew", padx=(6, 10))

        ctk.CTkLabel(
            card, text="Description",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MAIN, anchor="w",
        ).grid(row=8, column=0, columnspan=2, sticky="w", padx=32, pady=(0, 3))
        description_text = ctk.CTkTextbox(card, height=80, corner_radius=10, font=ctk.CTkFont(size=13))
        description_text.grid(row=9, column=0, columnspan=2, sticky="ew", padx=32, pady=(0, 16))

        def submit_report():
            item_name = item_name_entry.get().strip()
            category = category_var.get()
            color = color_entry.get().strip()
            location_val = location_var.get()
            date_val = date_entry.get().strip()
            description = description_text.get("1.0", "end").strip()

            if not item_name:
                messagebox.showwarning("Missing Information", "Please enter the item name.")
                return
            if category in ("", "Select category"):
                messagebox.showwarning("Missing Information", "Please select a category.")
                return
            if location_val in ("", "Select location"):
                messagebox.showwarning(
                    "Missing Information",
                    f"Please select the location where the item was {kind}.",
                )
                return
            if not date_val:
                messagebox.showwarning(
                    "Missing Information",
                    f"Please enter the date the item was {kind}.",
                )
                return
            try:
                datetime.strptime(date_val, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Invalid Date", "Please use the format YYYY-MM-DD.")
                return
            if selected_photo[0] is None:
                messagebox.showwarning(
                    "Photo Required", f"Please upload a photo of the {kind} item.",
                )
                return

            connection = connect_database()
            if connection is None:
                return

            cursor = connection.cursor()
            try:
                upload_folder = os.path.join("uploads", f"{kind}_items")
                os.makedirs(upload_folder, exist_ok=True)

                original_file = selected_photo[0]
                extension = os.path.splitext(original_file)[1]
                file_name = f"{kind}_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{extension}"
                destination = os.path.join(upload_folder, file_name)
                shutil.copy(original_file, destination)
                photo_path = destination.replace("\\", "/")

                if is_lost:
                    query = """
                        INSERT INTO lost_items
                        (user_id, item_name, category, description, color, location_lost, date_lost, photo_path)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                else:
                    query = """
                        INSERT INTO found_items
                        (user_id, item_name, category, description, color, location_found, date_found, photo_path)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                values = (user_id, item_name, category, description, color, location_val, date_val, photo_path)
                cursor.execute(query, values)
                generate_possible_matches(cursor)
                connection.commit()

                messagebox.showinfo(
                    "Report Submitted",
                    f"Your {kind} item report has been submitted successfully!",
                )
                cursor.close()
                connection.close()
                show_home()

            except Exception as error:
                connection.rollback()
                messagebox.showerror("Error", f"Failed to submit report.\n\n{error}")
                cursor.close()
                connection.close()

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=10, column=0, columnspan=2, sticky="ew", padx=32, pady=(0, 26))
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame, text="SUBMIT REPORT", height=46, corner_radius=12,
            fg_color=accent, hover_color=accent_hover,
            font=ctk.CTkFont(size=14, weight="bold"), command=submit_report,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkButton(
            btn_frame, text="CANCEL", height=46, corner_radius=12,
            fg_color=NEUTRAL, hover_color=NEUTRAL_HOVER,
            font=ctk.CTkFont(size=14, weight="bold"), command=show_home,
        ).grid(row=0, column=1, sticky="ew", padx=(8, 0))

    def show_report_lost():
        clear_content()
        header_label.configure(text="Report Lost Item")
        set_active("report_lost")
        build_report_form("lost")

    def show_report_found():
        clear_content()
        header_label.configure(text="Report Found Item")
        set_active("report_found")
        build_report_form("found")

    def show_search_items():
        clear_content()
        header_label.configure(text="Search / View Items")
        set_active("search")

        ctk.CTkLabel(
            content,
            text="Search reported lost and found items.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=TEXT_SUB,
        ).grid(row=0, column=0, sticky="w", pady=(0, 15))

        search_frame = section_card(content, corner_radius=14)
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(
            search_frame, text="Search:", font=ctk.CTkFont(family="Segoe UI", size=13),
        ).grid(row=0, column=0, padx=(20, 8), pady=16)

        search_entry = ctk.CTkEntry(
            search_frame, width=350, height=38, corner_radius=10,
            font=ctk.CTkFont(size=13),
            placeholder_text="Item name, description, color, location...",
        )
        search_entry.grid(row=0, column=1, padx=8, pady=16)
        search_entry.bind("<Return>", lambda e: load_items())

        type_var = ctk.StringVar(value="ALL")
        segment = ctk.CTkFrame(search_frame, fg_color=BG, corner_radius=10)
        segment.grid(row=0, column=2, padx=(8, 20), pady=16)
        type_buttons = {}

        def set_type(value):
            type_var.set(value)
            for seg_value, seg_btn in type_buttons.items():
                seg_btn.configure(
                    fg_color=INDIGO if seg_value == value else "transparent",
                    text_color="white" if seg_value == value else TEXT_SUB,
                )
            load_items()

        for i, seg_value in enumerate(["ALL", "LOST", "FOUND"]):
            seg_btn = ctk.CTkButton(
                segment, text=seg_value, width=70, height=32, corner_radius=8,
                fg_color=INDIGO if seg_value == "ALL" else "transparent",
                text_color="white" if seg_value == "ALL" else TEXT_SUB,
                hover_color=INDIGO_HOVER,
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda v=seg_value: set_type(v),
            )
            seg_btn.grid(row=0, column=i, padx=3, pady=3)
            type_buttons[seg_value] = seg_btn

        results_frame = ctk.CTkScrollableFrame(
            content, fg_color="white", corner_radius=16,
            border_width=1, border_color=BORDER,
        )
        results_frame.grid(row=2, column=0, sticky="nsew")
        content.grid_rowconfigure(2, weight=1)

        items_frame = results_frame
        image_references = []
