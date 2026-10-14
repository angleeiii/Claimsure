import customtkinter as ctk
from tkinter import ttk, messagebox
import mysql.connector
from database import connect_database
from PIL import Image, ImageTk
import os
def open_admin_dashboard(user_id, full_name):
    window = ctk.CTk()
    window.title("Claimsure - Administrator Dashboard")
    window.state("zoomed")
    window.minsize(1100, 650)
    BG_COLOR = "#F1F5F9"
    SIDEBAR_COLOR = "#0B1F3A"
    CARD_COLOR = "#FFFFFF"
    BORDER_COLOR = "#E2E8F0"
    TEXT_COLOR = "#0F172A"
    SECONDARY_TEXT = "#64748B"
    PRIMARY = "#0B1F3A"
    PRIMARY_SOFT = "#EAF1FF"
    BLUE = "#2563EB"
    BLUE_HOVER = "#1D4ED8"
    SKY = "#0891B2"
    SKY_HOVER = "#0E7490"
    INDIGO = "#4F46E5"
    INDIGO_HOVER = "#4338CA"
    GREEN = "#16A34A"
    GREEN_HOVER = "#15803D"
    RED = "#DC2626"
    RED_HOVER = "#B91C1C"
    GRAY = "#64748B"
    GRAY_HOVER = "#475569"
    SIDEBAR_HOVER = "#16304F"
    SIDEBAR_DIVIDER = "#1D3A5C"
    SIDEBAR_TEXT_DIM = "#7FA8D9"
    SIDEBAR_TEXT_MUTED = "#9DBEE6"
    window.configure(fg_color=BG_COLOR)
    window.grid_columnconfigure(0, weight=0)
    window.grid_columnconfigure(1, weight=1)
    window.grid_rowconfigure(0, weight=1)
    style = ttk.Style(window)
    style.theme_use("clam")
    style.configure(
        "Treeview",
        background="white", fieldbackground="white", foreground=TEXT_COLOR,
        rowheight=30, borderwidth=0, font=("Segoe UI", 10)
    )
    style.configure(
        "Treeview.Heading",
        background=PRIMARY_SOFT, foreground=PRIMARY,
        font=("Segoe UI", 10, "bold"), borderwidth=0, relief="flat"
    )
    style.map("Treeview.Heading", background=[("active", "#D6E4FF")])
    style.map(
        "Treeview",
        background=[("selected", BLUE)],
        foreground=[("selected", "white")]
    )
    style.configure(
        "TNotebook",
        background=BG_COLOR, borderwidth=0
    )
    style.configure(
        "TNotebook.Tab",
        background=CARD_COLOR, foreground=SECONDARY_TEXT,
        padding=(18, 10), font=("Segoe UI", 11, "bold"), borderwidth=0
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", BLUE)],
        foreground=[("selected", "white")]
    )
    sidebar = ctk.CTkFrame(
        window,
        width=240,
        corner_radius=0,
        fg_color=SIDEBAR_COLOR
    )
    sidebar.grid(row=0, column=0, sticky="nsew")
    sidebar.grid_propagate(False)
    sidebar.grid_rowconfigure(0, weight=0)
    sidebar.grid_rowconfigure(1, weight=0)
    sidebar.grid_rowconfigure(2, weight=0)
    sidebar.grid_rowconfigure(3, weight=0)
    sidebar.grid_rowconfigure(4, weight=1)
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
    admin_frame = ctk.CTkFrame(
        sidebar,
        fg_color=SIDEBAR_HOVER,
        corner_radius=12
    )
    admin_frame.grid(
        row=3,
        column=0,
        sticky="ew",
        padx=14,
        pady=(0, 15)
    )
    ctk.CTkLabel(
        admin_frame,
        text="ADMINISTRATOR",
        font=ctk.CTkFont(
            family="Segoe UI",
            size=9,
            weight="bold"
        ),
        text_color=SIDEBAR_TEXT_DIM
    ).pack(anchor="w", padx=14, pady=(12, 0))
    ctk.CTkLabel(
        admin_frame,
        text=full_name,
        font=ctk.CTkFont(
            family="Segoe UI",
            size=13,
            weight="bold"
        ),
        text_color="white",
        wraplength=180,
        justify="left"
    ).pack(anchor="w", padx=14, pady=(1, 2))
    ctk.CTkLabel(
        admin_frame,
        text="Lost & Found Staff",
        font=ctk.CTkFont(
            family="Segoe UI",
            size=10
        ),
        text_color=SIDEBAR_TEXT_MUTED
    ).pack(anchor="w", padx=14, pady=(0, 12))
    ctk.CTkFrame(
        sidebar,
        height=1,
        fg_color=SIDEBAR_DIVIDER
    ).grid(row=3, column=0, sticky="sew", padx=14)
    nav_frame = ctk.CTkFrame(
        sidebar,
        fg_color="transparent"
    )
    nav_frame.grid(
        row=4,
        column=0,
        sticky="nsew",
        padx=0,
        pady=(15, 5)
    )
    nav_frame.grid_columnconfigure(0, weight=1)
    nav_btn_kwargs = {
        "height": 46,
        "corner_radius": 10,
        "fg_color": "transparent",
        "hover_color": SIDEBAR_HOVER,
        "text_color": "white",
        "font": ctk.CTkFont(
            family="Segoe UI",
            size=13
        ),
        "anchor": "w"
    }
    nav_buttons = {}
    def set_active(key):
        for nav_key, nav_btn in nav_buttons.items():
            nav_btn.configure(fg_color=BLUE if nav_key == key else "transparent")
    content = ctk.CTkFrame(
        window,
        fg_color=BG_COLOR,
        corner_radius=0
    )
    content.grid(
        row=0,
        column=1,
        sticky="nsew",
        padx=0,
        pady=0
    )
    content.grid_columnconfigure(0, weight=1)
    content.grid_rowconfigure(2, weight=1)
    header = ctk.CTkFrame(
        content,
        fg_color=CARD_COLOR,
        corner_radius=0,
        height=70
    )
    header.grid(
        row=0,
        column=0,
        sticky="ew",
        padx=0,
        pady=0
    )
    header.grid_propagate(False)
    ctk.CTkFrame(
        content, height=1, fg_color=BORDER_COLOR
    ).grid(row=0, column=0, sticky="sew")
    header.grid_columnconfigure(0, weight=1)
    header_label = ctk.CTkLabel(
        header,
        text="Administrator Dashboard",
        font=ctk.CTkFont(
            family="Segoe UI",
            size=20,
            weight="bold"
        ),
        text_color=PRIMARY
    )
    header_label.grid(
        row=0,
        column=0,
        sticky="w",
        padx=30,
        pady=20
    )
    def clear_content():
        for widget in content.winfo_children():
            if widget != header:
                widget.destroy()
        content.grid_rowconfigure(1, weight=0)
        content.grid_rowconfigure(2, weight=1)
    def database_error(error):
        messagebox.showerror(
            "Database Error",
            f"Unable to access the database.\n\n{error}"
        )
    def section_card(parent, **kwargs):
        defaults = {"fg_color": CARD_COLOR, "corner_radius": 16, "border_width": 1, "border_color": BORDER_COLOR}
        defaults.update(kwargs)
        return ctk.CTkFrame(parent, **defaults)
    def show_dashboard():
        clear_content()
        set_active("dashboard")
        header_label.configure(
            text="Administrator Dashboard"
        )
        subtitle = ctk.CTkLabel(
            content,
            text="Overview of Claimsure lost-and-found activities.",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13
            ),
            text_color=SECONDARY_TEXT
        )
        subtitle.grid(
            row=1,
            column=0,
            sticky="nw",
            padx=30,
            pady=(20, 15)
        )
        dashboard_frame = ctk.CTkScrollableFrame(
            content,
            fg_color="transparent"
        )
        dashboard_frame.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=30,
            pady=(0, 25)
        )
        dashboard_frame.grid_columnconfigure(
            (0, 1, 2, 3),
            weight=1
        )
        counts = {
            "users": 0,
            "lost": 0,
            "found": 0,
            "claims": 0
        }
        connection = connect_database()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE role = 'USER'"
                )
                counts["users"] = cursor.fetchone()[0]
                cursor.execute(
                    "SELECT COUNT(*) FROM lost_items"
                )
                counts["lost"] = cursor.fetchone()[0]
                cursor.execute(
                    "SELECT COUNT(*) FROM found_items"
                )
                counts["found"] = cursor.fetchone()[0]
                cursor.execute(
                    "SELECT COUNT(*) FROM claims WHERE claim_status = 'PENDING'"
                )
                counts["claims"] = cursor.fetchone()[0]
            except Exception as error:
                database_error(error)
            finally:
                cursor.close()
                connection.close()
        stats = [
            ("Registered Users", counts["users"], BLUE),
            ("Lost Reports", counts["lost"], SKY),
            ("Found Reports", counts["found"], INDIGO),
            ("Pending Claims", counts["claims"], RED)
        ]
        for index, (title, value, color) in enumerate(stats):
            card = section_card(
                dashboard_frame,
                height=130
            )
            card.grid(
                row=0,
                column=index,
                sticky="ew",
                padx=6,
                pady=6
            )
            card.grid_propagate(False)
            ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=12
                ),
                text_color=SECONDARY_TEXT
            ).pack(
                anchor="w",
                padx=18,
                pady=(18, 3)
            )
            ctk.CTkLabel(
                card,
                text=str(value),
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=30,
                    weight="bold"
                ),
                text_color=color
            ).pack(
                anchor="w",
                padx=18
            )
        actions_card = section_card(
            dashboard_frame
        )
        actions_card.grid(
            row=1,
            column=0,
            columnspan=4,
            sticky="ew",
            padx=6,
            pady=(20, 10)
        )
        ctk.CTkLabel(
            actions_card,
            text="Quick Actions",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=16,
                weight="bold"
            ),
            text_color=TEXT_COLOR
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 3)
        )
        ctk.CTkLabel(
            actions_card,
            text="Access common administrator functions.",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11
            ),
            text_color=SECONDARY_TEXT
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 15)
        )
        action_frame = ctk.CTkFrame(
            actions_card,
            fg_color="transparent"
        )
        action_frame.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )
        ctk.CTkButton(
            action_frame,
            text="MANAGE REPORTS",
            height=42,
            corner_radius=10,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            command=show_reports
        ).pack(
            side="left",
            padx=(0, 10)
        )
        ctk.CTkButton(
            action_frame,
            text="VERIFY CLAIMS",
            height=42,
            corner_radius=10,
            fg_color=INDIGO,
            hover_color=INDIGO_HOVER,
            command=show_claims
        ).pack(
            side="left",
            padx=10
        )
        ctk.CTkButton(
            action_frame,
            text="MANAGE USERS",
            height=42,
            corner_radius=10,
            fg_color=GRAY,
            hover_color=GRAY_HOVER,
            command=show_users
        ).pack(
            side="left",
            padx=10
        )
    def show_reports():
        clear_content()
        set_active("reports")
        header_label.configure(
            text="Manage Item Reports"
        )
        subtitle = ctk.CTkLabel(
            content,
            text="View lost and found item reports submitted by users.",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13
            ),
            text_color=SECONDARY_TEXT
        )
        subtitle.grid(
            row=1,
            column=0,
            sticky="nw",
            padx=30,
            pady=(20, 15)
        )
        reports_frame = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )
        reports_frame.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=30,
            pady=(0, 25)
        )
        reports_frame.grid_columnconfigure(0, weight=1)
        reports_frame.grid_rowconfigure(1, weight=1)
        search_frame = section_card(
            reports_frame,
            corner_radius=14
        )
        search_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 12)
        )
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search item name...",
            height=40,
            corner_radius=10
        )
        search_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(15, 8),
            pady=12
        )
        search_entry.bind("<Return>", lambda e: load_reports())
        notebook = ttk.Notebook(reports_frame)
        notebook.grid(
            row=1,
            column=0,
            sticky="nsew"
        )
        lost_tab = ctk.CTkFrame(
            notebook,
            fg_color=CARD_COLOR
        )
        found_tab = ctk.CTkFrame(
            notebook,
            fg_color=CARD_COLOR
        )
        notebook.add(
            lost_tab,
            text="  Lost Reports  "
        )
        notebook.add(
            found_tab,
            text="  Found Reports  "
        )
        lost_tab.grid_rowconfigure(0, weight=1)
        lost_tab.grid_columnconfigure(0, weight=1)
        found_tab.grid_rowconfigure(0, weight=1)
        found_tab.grid_columnconfigure(0, weight=1)
        lost_columns = (
            "id",
            "item",
            "category",
            "color",
            "location",
            "date",
            "status"
        )
        lost_tree = ttk.Treeview(
            lost_tab,
            columns=lost_columns,
            show="headings"
        )
        headings = {
            "id": "ID",
            "item": "Item",
            "category": "Category",
            "color": "Color",
            "location": "Location Lost",
            "date": "Date Lost",
            "status": "Status"
        }
        widths = {
            "id": 70,
            "item": 180,
            "category": 130,
            "color": 100,
            "location": 160,
            "date": 120,
            "status": 100
        }
        for column in lost_columns:
            lost_tree.heading(
                column,
                text=headings[column]
            )
            lost_tree.column(
                column,
                width=widths[column],
                anchor="center"
            )
        lost_scroll = ttk.Scrollbar(
            lost_tab,
            orient="vertical",
            command=lost_tree.yview
        )
        lost_tree.configure(
            yscrollcommand=lost_scroll.set
        )
        lost_tree.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(15, 0),
            pady=15
        )
        lost_scroll.grid(
            row=0,
            column=1,
            sticky="ns",
            padx=(0, 15),
            pady=15
        )
        found_columns = (
            "id",
            "item",
            "category",
            "color",
            "location",
            "date",
            "status"
        )
        found_tree = ttk.Treeview(
            found_tab,
            columns=found_columns,
            show="headings"
        )
        headings_found = {
            "id": "ID",
            "item": "Item",
            "category": "Category",
            "color": "Color",
            "location": "Location Found",
            "date": "Date Found",
            "status": "Status"
        }
        for column in found_columns:
            found_tree.heading(
                column,
                text=headings_found[column]
            )
            found_tree.column(
                column,
                width=widths[column],
                anchor="center"
            )
        found_scroll = ttk.Scrollbar(
            found_tab,
            orient="vertical",
            command=found_tree.yview
        )
        found_tree.configure(
            yscrollcommand=found_scroll.set
        )
        found_tree.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(15, 0),
            pady=15
        )
        found_scroll.grid(
            row=0,
            column=1,
            sticky="ns",
            padx=(0, 15),
            pady=15
        )
        def load_reports():
            for item in lost_tree.get_children():
                lost_tree.delete(item)
            for item in found_tree.get_children():
                found_tree.delete(item)
            keyword = search_entry.get().strip()
            connection = connect_database()
            if connection is None:
                return
            cursor = connection.cursor()
            try:
                lost_query = """
                    SELECT
                        lost_item_id,
                        item_name,
                        category,
                        color,
                        location_lost,
                        date_lost,
                        status
                    FROM lost_items
                    WHERE item_name LIKE %s
                    ORDER BY date_reported DESC
                """
                cursor.execute(
                    lost_query,
                    (f"%{keyword}%",)
                )
                for row in cursor.fetchall():
                    lost_tree.insert(
                        "",
                        "end",
                        values=row
                    )
                found_query = """
                    SELECT
                        found_item_id,
                        item_name,
                        category,
                        color,
                        location_found,
                        date_found,
                        status
                    FROM found_items
                    WHERE item_name LIKE %s
                    ORDER BY date_reported DESC
                """
                cursor.execute(
                    found_query,
                    (f"%{keyword}%",)
                )
                for row in cursor.fetchall():
                    found_tree.insert(
                        "",
                        "end",
                        values=row
                    )
            except Exception as error:
                database_error(error)
            finally:
                cursor.close()
                connection.close()
        ctk.CTkButton(
            search_frame,
            text="SEARCH",
            width=110,
            height=40,
            corner_radius=10,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            command=load_reports
        ).pack(
            side="left",
            padx=(0, 15),
            pady=12
        )
        action_frame = ctk.CTkFrame(
            reports_frame,
            fg_color="transparent"
        )
        action_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(12, 0)
        )
        def delete_selected_report():
            selected_tab = notebook.index(notebook.select())
            if selected_tab == 0:
                selected = lost_tree.selection()
                report_type = "LOST"
                table = "lost_items"
                id_column = "lost_item_id"
                tree = lost_tree
                report_name = "lost"
            else:
                selected = found_tree.selection()
                report_type = "FOUND"
                table = "found_items"
                id_column = "found_item_id"
                tree = found_tree
                report_name = "found"
            if not selected:
                messagebox.showwarning(
                    "No Report Selected",
                    f"Please select a {report_name} report first.",
                    parent=window
                )
                return
            values = tree.item(selected[0], "values")
            report_id = values[0]
            item_name = values[1]
            confirmed = messagebox.askyesno(
                "Delete Report",
                f"Are you sure you want to delete this {report_type.lower()} report?\n\n"
                f"Item: {item_name}\n"
                f"Report ID: {report_id}\n\n"
                "This will also remove related match and claim records.\n"
                "This action cannot be undone.",
                icon="warning",
                parent=window
            )
            if not confirmed:
                return
            connection = connect_database()
            if connection is None:
                return
            cursor = connection.cursor()
            try:
                cursor.execute(
                    f"DELETE FROM {table} WHERE {id_column} = %s",
                    (report_id,)
                )
                if cursor.rowcount == 0:
                    connection.rollback()
                    messagebox.showwarning(
                        "Report Not Found",
                        "The selected report no longer exists.",
                        parent=window
                    )
                    load_reports()
                    return
                connection.commit()
                messagebox.showinfo(
                    "Report Deleted",
                    f"The {report_type.lower()} report has been deleted successfully.",
                    parent=window
                )
                load_reports()
            except Exception as error:
                connection.rollback()
                database_error(error)
            finally:
                cursor.close()
                connection.close()
        ctk.CTkButton(
            action_frame,
            text="DELETE SELECTED REPORT",
            width=210,
            height=42,
            corner_radius=10,
            fg_color=RED,
            hover_color=RED_HOVER,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11,
                weight="bold"
            ),
            command=delete_selected_report
        ).pack(
            side="left",
            padx=(0, 10),
            pady=(0, 5)
        )
        load_reports()
    def show_claims():
        clear_content()
        set_active("claims")
        header_label.configure(
            text="Verify Claims"
        )
        subtitle = ctk.CTkLabel(
            content,
            text="Review submitted claims and verify item ownership.",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13
            ),
            text_color=SECONDARY_TEXT
        )
        subtitle.grid(
            row=1,
            column=0,
            sticky="nw",
            padx=30,
            pady=(20, 15)
        )
        claims_frame = section_card(
            content
        )
        claims_frame.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=30,
            pady=(0, 25)
        )
        claims_frame.grid_columnconfigure(0, weight=1)
        claims_frame.grid_rowconfigure(0, weight=1)
        columns = (
            "claim_id",
            "user",
            "item",
            "proof",
            "status",
            "submitted"
        )
        tree = ttk.Treeview(
            claims_frame,
            columns=columns,
            show="headings"
        )
        headings = {
            "claim_id": "Claim ID",
            "user": "User",
            "item": "Found Item",
            "proof": "Ownership Details",
            "status": "Status",
            "submitted": "Submitted"
        }
        widths = {
            "claim_id": 90,
            "user": 150,
            "item": 180,
            "proof": 380,
            "status": 110,
            "submitted": 170
        }
        for column in columns:
            tree.heading(
                column,
                text=headings[column]
            )
            tree.column(
                column,
                width=widths[column],
                anchor="center"
            )
        scrollbar = ttk.Scrollbar(
            claims_frame,
            orient="vertical",
            command=tree.yview
        )
        tree.configure(
            yscrollcommand=scrollbar.set
        )
        tree.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(20, 0),
            pady=20
        )
        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
            padx=(0, 20),
            pady=20
        )
        button_frame = ctk.CTkFrame(
            claims_frame,
            fg_color="transparent"
        )
        button_frame.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=20,
            pady=(0, 20)
        )
        selected_claim = [None]
        def select_claim(event=None):
            selected = tree.selection()
            if not selected:
                return
            values = tree.item(
                selected[0]
            )["values"]
            if values:
                selected_claim[0] = values[0]
        tree.bind(
            "<<TreeviewSelect>>",
            select_claim
        )
        def verify_claim(status):
            claim_id = selected_claim[0]
            if claim_id is None:
                messagebox.showwarning(
                    "No Claim Selected",
                    "Please select a claim first."
                )
                return
            admin_message = ""
            if status == "APPROVED":
                message_window = ctk.CTkToplevel(window)
                message_window.title("Approve Claim")
                message_window.geometry("560x360")
                message_window.resizable(False, False)
                message_window.transient(window)
                message_window.grab_set()
                ctk.CTkLabel(
                    message_window,
                    text="Approve Claim",
                    font=ctk.CTkFont(size=20, weight="bold"),
                    text_color=TEXT_COLOR
                ).pack(pady=(25, 5))
                ctk.CTkLabel(
                    message_window,
                    text="Add a message for the user about the approved claim.",
                    font=ctk.CTkFont(size=12),
                    text_color=SECONDARY_TEXT
                ).pack(pady=(0, 12))
                message_text = ctk.CTkTextbox(
                    message_window,
                    width=480,
                    height=130,
                    corner_radius=10,
                    font=ctk.CTkFont(size=13)
                )
                message_text.pack(padx=30)
                message_text.insert(
                    "1.0",
                    "Approved. Please collect your item at the Claimsure Office located near the Amusement Park."
                )
                result = {"confirmed": False, "message": ""}
                def confirm_approval():
                    msg = message_text.get("1.0", "end").strip()
                    if not msg:
                        messagebox.showwarning(
                            "Message Required",
                            "Please enter a message for the user.",
                            parent=message_window
                        )
                        return
                    result["confirmed"] = True
                    result["message"] = msg
                    message_window.destroy()
                def cancel_approval():
                    message_window.destroy()
                ctk.CTkButton(
                    message_window, text="APPROVE CLAIM", width=190, height=42,
                    corner_radius=10, fg_color=GREEN, hover_color=GREEN_HOVER,
                    command=confirm_approval
                ).pack(side="left", padx=(80, 8), pady=20)
                ctk.CTkButton(
                    message_window, text="CANCEL", width=120, height=42,
                    corner_radius=10, fg_color=GRAY, hover_color=GRAY_HOVER,
                    command=cancel_approval
                ).pack(side="left", padx=8, pady=20)
                window.wait_window(message_window)
                if not result["confirmed"]:
                    return
                admin_message = result["message"]
            else:
                confirmed = messagebox.askyesno(
                    "Reject Claim",
                    "Are you sure you want to reject this claim?"
                )
                if not confirmed:
                    return
                admin_message = "Claim rejected by administrator."
            connection = connect_database()
            if connection is None:
                return
            cursor = connection.cursor()
            try:
                cursor.execute(
                    """
                    SELECT found_item_id, user_id
                    FROM claims
                    WHERE claim_id = %s
                    AND claim_status = 'PENDING'
                    """,
                    (claim_id,)
                )
                claim = cursor.fetchone()
                if not claim:
                    messagebox.showwarning(
                        "Claim Unavailable",
                        "This claim is no longer pending."
                    )
                    return
                found_item_id, claim_user_id = claim
                cursor.execute(
                    """
                    UPDATE claims
                    SET claim_status = %s
                    WHERE claim_id = %s
                    """,
                    (status, claim_id)
                )
                cursor.execute(
                    """
                    INSERT INTO verifications
                    (
                        claim_id,
                        verified_by,
                        verification_status,
                        remarks
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        claim_id,
                        user_id,
                        status,
                        admin_message
                    )
                )
                notification_title = "Claim Approved" if status == "APPROVED" else "Claim Rejected"
                notification_message = admin_message
                cursor.execute(
                    """
                    INSERT INTO notifications
                    (user_id, title, message, notification_type)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (claim_user_id, notification_title, notification_message, "CLAIM")
                )
                if status == "APPROVED":
                    cursor.execute(
                        """
                        UPDATE found_items
                        SET status = 'CLAIMED'
                        WHERE found_item_id = %s
                        """,
                        (found_item_id,)
                    )
                    cursor.execute(
                        """
                        UPDATE lost_items
                        SET status = 'CLAIMED'
                        WHERE lost_item_id = (
                            SELECT lost_item_id FROM (
                                SELECT m.lost_item_id
                                FROM matches m
                                INNER JOIN lost_items l
                                    ON l.lost_item_id = m.lost_item_id
                                WHERE m.found_item_id = %s
                                AND l.user_id = %s
                                ORDER BY m.match_score DESC
                                LIMIT 1
                            ) AS best_match
                        )
                        """,
                        (found_item_id, claim_user_id)
                    )
                connection.commit()
                messagebox.showinfo(
                    "Claim Updated",
                    f"Claim #{claim_id} has been {status.lower()}."
                )
                selected_claim[0] = None
                load_claims()
            except Exception as error:
                connection.rollback()
                database_error(error)
            finally:
                cursor.close()
                connection.close()
        def load_claims():
            for item in tree.get_children():
                tree.delete(item)
            connection = connect_database()
            if connection is None:
                return
            cursor = connection.cursor()
            try:
                query = """
                    SELECT
                        c.claim_id,
                        u.username,
                        f.item_name,
                        c.proof_description,
                        c.claim_status,
                        c.submitted_at
                    FROM claims c
                    INNER JOIN users u
                        ON c.user_id = u.user_id
                    INNER JOIN found_items f
                        ON c.found_item_id = f.found_item_id
                    ORDER BY
                        CASE
                            WHEN c.claim_status = 'PENDING'
                            THEN 0
                            ELSE 1
                        END,
                        c.submitted_at DESC
                """
                cursor.execute(query)
                for row in cursor.fetchall():
                    tree.insert(
                        "",
                        "end",
                        values=row
                    )
            except Exception as error:
                database_error(error)
            finally:
                cursor.close()
                connection.close()
        ctk.CTkButton(
            button_frame,
            text="APPROVE CLAIM",
            width=160,
            height=42,
            corner_radius=10,
            fg_color=GREEN,
            hover_color=GREEN_HOVER,
            command=lambda: verify_claim("APPROVED")
        ).pack(
            side="left",
            padx=(0, 8)
        )
        ctk.CTkButton(
            button_frame,
            text="REJECT CLAIM",
            width=160,
            height=42,
            corner_radius=10,
            fg_color=RED,
            hover_color=RED_HOVER,
            command=lambda: verify_claim("REJECTED")
        ).pack(
            side="left",
            padx=8
        )
        ctk.CTkButton(
            button_frame,
            text="REFRESH",
            width=120,
            height=42,
            corner_radius=10,
            fg_color=GRAY,
            hover_color=GRAY_HOVER,
            command=load_claims
        ).pack(
            side="left",
            padx=8
        )
        load_claims()
    def show_users():
        clear_content()
        set_active("users")
        header_label.configure(
            text="Manage Users"
        )
        subtitle = ctk.CTkLabel(
            content,
            text="View registered Claimsure user accounts.",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13
            ),
            text_color=SECONDARY_TEXT
        )
        subtitle.grid(
            row=1,
            column=0,
            sticky="nw",
            padx=30,
            pady=(20, 15)
        )
        users_frame = section_card(
            content
        )
        users_frame.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=30,
            pady=(0, 25)
        )
        users_frame.grid_columnconfigure(0, weight=1)
        users_frame.grid_rowconfigure(0, weight=1)
        columns = (
            "id",
            "name",
            "username",
            "contact",
            "role",
            "created"
        )
        tree = ttk.Treeview(
            users_frame,
            columns=columns,
            show="headings"
        )
        headings = {
            "id": "ID",
            "name": "Full Name",
            "username": "Username",
            "contact": "Contact",
            "role": "Role",
            "created": "Created"
        }
        widths = {
            "id": 70,
            "name": 220,
            "username": 150,
            "contact": 150,
            "role": 100,
            "created": 180
        }
        for column in columns:
            tree.heading(
                column,
                text=headings[column]
            )
            tree.column(
                column,
                width=widths[column],
                anchor="center"
            )
        scrollbar = ttk.Scrollbar(
            users_frame,
            orient="vertical",
            command=tree.yview
        )
        tree.configure(
            yscrollcommand=scrollbar.set
        )
        tree.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(20, 0),
            pady=20
        )
        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
            padx=(0, 20),
            pady=20
        )
        def change_user_password():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("No User Selected", "Please select a user first.", parent=window)
                return
            values = tree.item(selected[0])["values"]
            if not values:
                return
            selected_user_id, selected_full_name, selected_username = values[:3]
            if int(selected_user_id) == int(user_id):
                messagebox.showwarning("Not Allowed", "You cannot change your own password from Manage Users.", parent=window)
                return
            password_window = ctk.CTkToplevel(window)
            password_window.title("Change Password")
            password_window.geometry("460x360")
            password_window.resizable(False, False)
            password_window.transient(window)
            password_window.grab_set()
            ctk.CTkLabel(password_window, text="Change User Password", font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_COLOR).pack(pady=(25,5))
            ctk.CTkLabel(password_window, text=f"{selected_full_name}  •  @{selected_username}", font=ctk.CTkFont(size=12), text_color=SECONDARY_TEXT).pack(pady=(0,20))
            new_password=ctk.CTkEntry(password_window,width=340,height=42,corner_radius=10,placeholder_text="New password",show="•")
            new_password.pack(pady=6)
            confirm_password=ctk.CTkEntry(password_window,width=340,height=42,corner_radius=10,placeholder_text="Confirm new password",show="•")
            confirm_password.pack(pady=6)
            def save_password():
                password=new_password.get(); confirmation=confirm_password.get()
                if not password or not confirmation:
                    messagebox.showwarning("Required","Please enter and confirm the new password.",parent=password_window); return
                if len(password)<6:
                    messagebox.showwarning("Invalid Password","Password must be at least 6 characters long.",parent=password_window); return
                if password!=confirmation:
                    messagebox.showwarning("Password Mismatch","The passwords do not match.",parent=password_window); return
                if not messagebox.askyesno("Confirm Password Change",f"Change the password for {selected_username}?",parent=password_window): return
                connection=connect_database()
                if connection is None: return
                cursor=connection.cursor()
                try:
                    cursor.execute("UPDATE users SET password = %s WHERE user_id = %s",(password,selected_user_id))
                    connection.commit()
                    messagebox.showinfo("Password Updated",f"The password for {selected_username} has been changed successfully.",parent=password_window)
                    password_window.destroy()
                except Exception as error:
                    connection.rollback(); database_error(error)
                finally:
                    cursor.close(); connection.close()
            button_row=ctk.CTkFrame(password_window,fg_color="transparent")
            button_row.pack(pady=20)
            ctk.CTkButton(button_row,text="SAVE PASSWORD",width=170,height=42,corner_radius=10,fg_color=BLUE,hover_color=BLUE_HOVER,command=save_password).pack(side="left",padx=5)
            ctk.CTkButton(button_row,text="CANCEL",width=110,height=42,corner_radius=10,fg_color=GRAY,hover_color=GRAY_HOVER,command=password_window.destroy).pack(side="left",padx=5)
        def load_users():
            for item in tree.get_children():
                tree.delete(item)
            connection = connect_database()
            if connection is None:
                return
            cursor = connection.cursor()
            try:
                cursor.execute(
                    """
                    SELECT
                        user_id,
                        full_name,
                        username,
                        contact_number,
                        role,
                        created_at
                    FROM users
                    ORDER BY created_at DESC
                    """
                )
                for row in cursor.fetchall():
                    tree.insert(
                        "",
                        "end",
                        values=row
                    )
            except Exception as error:
                database_error(error)
            finally:
                cursor.close()
                connection.close()
        load_users()
        ctk.CTkButton(
            users_frame, text="CHANGE PASSWORD", width=180, height=42,
            corner_radius=10, fg_color=BLUE, hover_color=BLUE_HOVER,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=change_user_password
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0,20))
    return_to_login = [False]
    def logout():
        confirmed = messagebox.askyesno(
            "Confirm Logout",
            "Are you sure you want to log out?",
            icon="question",
            parent=window
        )
        if not confirmed:
            return
        return_to_login[0] = True
        window.destroy()
    nav_buttons["dashboard"] = ctk.CTkButton(
        nav_frame,
        text="🏠  Dashboard",
        command=show_dashboard,
        **nav_btn_kwargs
    )
    nav_buttons["dashboard"].grid(
        row=0,
        column=0,
        sticky="ew",
        padx=14,
        pady=5
    )
    nav_buttons["reports"] = ctk.CTkButton(
        nav_frame,
        text="📋  Manage Reports",
        command=show_reports,
        **nav_btn_kwargs
    )
    nav_buttons["reports"].grid(
        row=1,
        column=0,
        sticky="ew",
        padx=14,
        pady=5
    )
    nav_buttons["claims"] = ctk.CTkButton(
        nav_frame,
        text="✓  Verify Claims",
        command=show_claims,
        **nav_btn_kwargs
    )
    nav_buttons["claims"].grid(
        row=2,
        column=0,
        sticky="ew",
        padx=14,
        pady=5
    )
    nav_buttons["users"] = ctk.CTkButton(
        nav_frame,
        text="👥  Manage Users",
        command=show_users,
        **nav_btn_kwargs
    )
    nav_buttons["users"].grid(
        row=3,
        column=0,
        sticky="ew",
        padx=14,
        pady=5
    )
    ctk.CTkButton(
        sidebar,
        text="🚪  Logout",
        height=46,
        corner_radius=10,
        fg_color=RED,
        hover_color=RED_HOVER,
        text_color="white",
        font=ctk.CTkFont(
            family="Segoe UI",
            size=13,
            weight="bold"
        ),
        command=logout
    ).grid(
        row=5,
        column=0,
        sticky="ew",
        padx=14,
        pady=(10, 20)
    )
    show_dashboard()
    window.mainloop()
    if return_to_login[0]:
        from login import open_login
        open_login()