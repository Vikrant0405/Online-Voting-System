"""
Voting Assistant  -  Tkinter + MySQL
Requires:  pip install mysql-connector-python matplotlib pillow
"""
import functools
import os
import re
import shutil
import uuid
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import mysql.connector
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk, ImageOps, ImageDraw

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
DB_CONFIG = dict(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="vikrant",
    database="voting_system",
    ssl_disabled=True,
    connection_timeout=10,
    autocommit=True,
)

# ----------------------------------------------------------------------
# Colour theme / fonts  (change them here and the whole app follows)
# ----------------------------------------------------------------------
BG = "#1E1F22"          # window background
HEADER = "#17181B"      # top bar
PANEL = "#26282E"       # cards / panels
PANEL_ALT = "#2F3139"   # inputs, secondary buttons
BORDER = "#3A3D45"
ACCENT = "#BEB09D"      # gold / sand accent
ACCENT_HOVER = "#D6C9B4"
TEXT = "#F2F2F2"
MUTED = "#9A9DA5"
GREEN = "#2E7D55"
GREEN_HOVER = "#3A9667"
RED = "#9B3535"
RED_HOVER = "#B84444"
FONT = "Segoe UI"
CHART_COLORS = ["#BEB09D", "#4C9F70", "#5B8DEF", "#E07A5F", "#B56CD9", "#E5C158", "#4CC3D9", "#D96C8A"]

THUMB = (56, 56)        # table thumbnails
ROW_HEIGHT = 64


# ----------------------------------------------------------------------
# Small UI helpers
# ----------------------------------------------------------------------
def make_button(parent, text, command, kind="secondary", size=13, width=None, padx=20, pady=9):
    """Flat button with hover effect. kind: primary | secondary | success | danger"""
    palette = {
        "primary": (ACCENT, "#1E1F22", ACCENT_HOVER),
        "secondary": (PANEL_ALT, ACCENT, BORDER),
        "success": (GREEN, "#FFFFFF", GREEN_HOVER),
        "danger": (RED, "#FFFFFF", RED_HOVER),
    }
    bg, fg, hover = palette[kind]
    btn = tk.Button(parent, text=text, command=command, font=(FONT, size, "bold"),
                    bg=bg, fg=fg, activebackground=hover, activeforeground=fg,
                    disabledforeground="#6C6F78", relief="flat", bd=0, cursor="hand2",
                    padx=padx, pady=pady, highlightthickness=0)
    if width:
        btn.config(width=width)

    def on_enter(_):
        if str(btn["state"]) == "normal":
            btn.config(bg=hover)

    def on_leave(_):
        btn.config(bg=bg if str(btn["state"]) == "normal" else PANEL_ALT)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


def db_safe(fn):
    """Shows a friendly message instead of crashing when MySQL raises an error."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Something went wrong with the database:\n\n{err}")
    return wrapper


class VotingAssistant:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    IMAGE_DIR = os.path.join(APP_DIR, "images")

    # ==================================================================
    # Start-up
    # ==================================================================
    def __init__(self, root):
        self.root = root
        self.is_on = False          # is voting open?
        self.failed = False
        self.voter = None           # dict of the voter currently voting
        self.user_photos = []       # keep PhotoImage references alive
        self.cand_photos = []
        self.result_photos = []
        self.vote_photos = []

        root.title("Voting Assistant")
        root.geometry("1200x760")
        root.minsize(1000, 650)
        root.configure(bg=BG)
        try:
            root.state("zoomed")
        except tk.TclError:
            try:
                root.attributes("-zoomed", True)
            except tk.TclError:
                pass
        root.protocol("WM_DELETE_WINDOW", self.exit_app)

        self.setup_styles()

        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            self.ensure_photo_columns()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error",
                                 f"Could not connect to the database.\n\nCheck that MySQL is running and the "
                                 f"settings at the top of this file are correct.\n\n{err}")
            self.failed = True
            return

        self.container = tk.Frame(root, bg=BG)
        self.container.pack(fill="both", expand=True)
        self.main_menu()

    def setup_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT,
                        rowheight=ROW_HEIGHT, font=(FONT, 12), borderwidth=0, bordercolor=PANEL,
                        lightcolor=PANEL, darkcolor=PANEL)
        style.map("Treeview", background=[("selected", "#4A463F")], foreground=[("selected", TEXT)])
        style.configure("Treeview.Heading", background=HEADER, foreground=ACCENT,
                        font=(FONT, 12, "bold"), relief="flat", padding=8)
        style.map("Treeview.Heading", background=[("active", "#2A2C32")])
        style.configure("Vertical.TScrollbar", background="#4A4D56", troughcolor=BG, bordercolor=BG,
                        arrowcolor=ACCENT, lightcolor="#4A4D56", darkcolor="#4A4D56")
        style.map("Vertical.TScrollbar", background=[("active", "#6A6E78")])
        style.configure("TCombobox", fieldbackground=PANEL_ALT, background=PANEL_ALT, foreground=TEXT,
                        arrowcolor=ACCENT, bordercolor=BORDER, lightcolor=PANEL_ALT, darkcolor=PANEL_ALT,
                        padding=6)
        style.map("TCombobox", fieldbackground=[("readonly", PANEL_ALT)],
                  foreground=[("readonly", TEXT)], selectbackground=[("readonly", PANEL_ALT)],
                  selectforeground=[("readonly", TEXT)])
        self.root.option_add("*TCombobox*Listbox.background", PANEL_ALT)
        self.root.option_add("*TCombobox*Listbox.foreground", TEXT)
        self.root.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
        self.root.option_add("*TCombobox*Listbox.selectForeground", "#1E1F22")
        self.root.option_add("*TCombobox*Listbox.font", (FONT, 12))

    # ==================================================================
    # Database helpers
    # ==================================================================
    def db_all(self, sql, params=()):
        self.conn.ping(reconnect=True, attempts=2, delay=1)
        cur = self.conn.cursor()
        try:
            cur.execute(sql, params)
            return cur.fetchall()
        finally:
            cur.close()

    def db_one(self, sql, params=()):
        self.conn.ping(reconnect=True, attempts=2, delay=1)
        cur = self.conn.cursor()
        try:
            cur.execute(sql, params)
            return cur.fetchone()
        finally:
            cur.close()

    def db_exec(self, sql, params=()):
        self.conn.ping(reconnect=True, attempts=2, delay=1)
        cur = self.conn.cursor()
        try:
            cur.execute(sql, params)
            return cur.rowcount
        finally:
            cur.close()

    def ensure_photo_columns(self):
        """Adds the image columns (photo_path / symbol_path) if they do not exist yet."""
        for table, column in (("users", "photo_path"), ("candidates", "photo_path"),
                              ("candidates", "symbol_path")):
            found = self.db_one(
                "SELECT COUNT(*) FROM information_schema.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s",
                (table, column))
            if found[0] == 0:
                self.db_exec(f"ALTER TABLE {table} ADD COLUMN {column} VARCHAR(255) NULL")

    # ==================================================================
    # Photo helpers
    # ==================================================================
    def load_image(self, path, size, mode="crop", placeholder="No Photo"):
        """Returns a PIL image of exactly `size`.
        mode 'crop'    -> fills the square (good for faces)
        mode 'contain' -> whole image on a white square (good for party symbols/logos)
        Falls back to a grey placeholder if the file is missing or unreadable."""
        try:
            if path:
                full = path if os.path.isabs(path) else os.path.join(self.APP_DIR, path)
                if os.path.exists(full):
                    img = Image.open(full)
                    if mode == "contain":
                        img = img.convert("RGBA")
                        fitted = ImageOps.contain(img, size)
                        bg = Image.new("RGBA", size, "#FFFFFF")
                        bg.paste(fitted, ((size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2), fitted)
                        return bg.convert("RGB")
                    return ImageOps.fit(img.convert("RGB"), size)
        except Exception:
            pass
        img = Image.new("RGB", size, "#3A3D45")
        draw = ImageDraw.Draw(img)
        box = draw.textbbox((0, 0), placeholder)
        draw.text(((size[0] - (box[2] - box[0])) // 2, (size[1] - (box[3] - box[1])) // 2),
                  placeholder, fill="#C8CAD0")
        return img

    def make_thumb(self, path, size, mode="crop", placeholder="No Photo"):
        return ImageTk.PhotoImage(self.load_image(path, size, mode, placeholder))

    def make_pair_thumb(self, photo_path, symbol_path, size=THUMB):
        """Candidate photo and party symbol side by side (for table rows)."""
        a = self.load_image(photo_path, size, "crop", "No Photo")
        b = self.load_image(symbol_path, size, "contain", "No Symbol")
        pair = Image.new("RGB", (size[0] * 2 + 6, size[1]), PANEL)
        pair.paste(a, (0, 0))
        pair.paste(b, (size[0] + 6, 0))
        return ImageTk.PhotoImage(pair)

    def save_image(self, src, prefix):
        """Copies the chosen photo into ./images and returns the relative path stored in the DB."""
        if not src:
            return None
        os.makedirs(self.IMAGE_DIR, exist_ok=True)
        name = f"{prefix}_{uuid.uuid4().hex}{os.path.splitext(src)[1].lower()}"
        shutil.copy(src, os.path.join(self.IMAGE_DIR, name))
        return "images/" + name

    def delete_image(self, rel_path):
        try:
            if rel_path:
                os.remove(os.path.join(self.APP_DIR, rel_path))
        except OSError:
            pass

    def photo_picker(self, parent, holder, size=(150, 150), button_text="Choose Photo",
                     mode="crop", placeholder="No Photo"):
        """Preview + 'Choose Photo' button. The chosen file path is kept in holder['path']."""
        box = tk.Frame(parent, bg=PANEL)
        empty = self.make_thumb(None, size, mode, placeholder)
        preview = tk.Label(box, image=empty, bg=PANEL, highlightthickness=1,
                           highlightbackground=BORDER)
        preview.image = empty
        preview.pack(pady=(0, 8))

        def browse():
            path = filedialog.askopenfilename(
                parent=parent.winfo_toplevel(), title="Select Photo",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"), ("All files", "*.*")])
            if not path:
                return
            try:
                with Image.open(path) as test:
                    test.verify()
                photo = self.make_thumb(path, size, mode)
            except Exception:
                messagebox.showerror("Photo", "That file could not be opened as an image.",
                                     parent=parent.winfo_toplevel())
                return
            holder["path"] = path
            preview.config(image=photo)
            preview.image = photo

        make_button(box, button_text, browse, "secondary", size=11, pady=6).pack()
        tk.Label(box, text="PNG / JPG (optional)", font=(FONT, 9), bg=PANEL, fg=MUTED).pack(pady=(6, 0))
        return box

    # ==================================================================
    # Layout helpers (screens + dialogs)
    # ==================================================================
    def clear_container(self):
        for w in self.container.winfo_children():
            w.destroy()

    def new_screen(self, title, back=None, back_text="←  Back", right=None):
        """Standard screen: header (back button | title | extra widget) + body frame."""
        self.clear_container()
        header = tk.Frame(self.container, bg=HEADER, height=72)
        header.pack(fill="x")
        header.pack_propagate(False)
        header.columnconfigure(0, weight=1, uniform="h")
        header.columnconfigure(1, weight=0)
        header.columnconfigure(2, weight=1, uniform="h")
        header.rowconfigure(0, weight=1)

        if back:
            make_button(header, back_text, back, "secondary", size=12, pady=6).grid(
                row=0, column=0, sticky="w", padx=24)
        tk.Label(header, text=title, font=(FONT, 22, "bold"), bg=HEADER, fg=ACCENT).grid(row=0, column=1)
        if right:
            holder = tk.Frame(header, bg=HEADER)
            holder.grid(row=0, column=2, sticky="e", padx=24)
            right(holder)
        tk.Frame(self.container, bg=ACCENT, height=2).pack(fill="x")

        body = tk.Frame(self.container, bg=BG)
        body.pack(fill="both", expand=True, padx=40, pady=24)
        return body

    def make_dialog(self, title, heading):
        """Modal pop-up. Returns (window, body_frame)."""
        win = tk.Toplevel(self.root)
        win.title(title)
        win.configure(bg=BG)
        win.transient(self.root)
        win.resizable(False, False)
        card = tk.Frame(win, bg=PANEL, highlightthickness=2, highlightbackground=ACCENT)
        card.pack(padx=22, pady=22)
        body = tk.Frame(card, bg=PANEL)
        body.pack(padx=34, pady=26)
        tk.Label(body, text=heading, font=("Georgia", 22, "bold"), bg=PANEL, fg=ACCENT).pack(pady=(0, 6))
        tk.Frame(body, bg=BORDER, height=1).pack(fill="x", pady=(4, 8))
        return win, body

    def open_dialog(self, win, focus=None):
        win.update_idletasks()
        w, h = win.winfo_reqwidth(), win.winfo_reqheight()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - w) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - h) // 2
        win.geometry(f"{w}x{h}+{max(x, 0)}+{max(y, 0)}")
        win.grab_set()
        (focus or win).focus_force()

    def form_field(self, parent, label, show=None, width=26):
        tk.Label(parent, text=label, font=(FONT, 11), bg=PANEL, fg=MUTED, anchor="w").pack(fill="x", pady=(10, 2))
        entry = tk.Entry(parent, font=(FONT, 13), width=width, show=show or "", bg=PANEL_ALT, fg=TEXT,
                         insertbackground=TEXT, relief="flat", highlightthickness=1,
                         highlightbackground=BORDER, highlightcolor=ACCENT)
        entry.pack(fill="x", ipady=6)
        return entry

    def form_combo(self, parent, label, values):
        tk.Label(parent, text=label, font=(FONT, 11), bg=PANEL, fg=MUTED, anchor="w").pack(fill="x", pady=(10, 2))
        var = tk.StringVar(value="Select")
        combo = ttk.Combobox(parent, textvariable=var, values=values, state="readonly", font=(FONT, 13))
        combo.pack(fill="x")
        return var

    def build_table(self, parent, columns, widths, photo_heading="Photo", photo_width=90):
        wrap = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        wrap.pack(fill="both", expand=True)
        tree = ttk.Treeview(wrap, columns=columns, show="tree headings", selectmode="browse")
        tree.heading("#0", text=photo_heading)
        tree.column("#0", width=photo_width, anchor="center", stretch=False)
        for col, width in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=width, minwidth=60)
        sb = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        tree.tag_configure("odd", background="#2B2D33")
        tree.tag_configure("even", background=PANEL)
        return tree

    def search_bar(self, parent, on_search, on_reset):
        bar = tk.Frame(parent, bg=BG)
        bar.pack(fill="x", pady=(0, 14))
        var = tk.StringVar()
        entry = tk.Entry(bar, textvariable=var, font=(FONT, 13), width=34, bg=PANEL_ALT, fg=TEXT,
                         insertbackground=TEXT, relief="flat", highlightthickness=1,
                         highlightbackground=BORDER, highlightcolor=ACCENT)
        entry.pack(side="left", ipady=7, padx=(0, 10))
        entry.bind("<Return>", lambda e: on_search())
        make_button(bar, "Search", on_search, "primary", size=12, pady=6).pack(side="left", padx=(0, 8))
        make_button(bar, "Reset", on_reset, "secondary", size=12, pady=6).pack(side="left")
        count = tk.Label(bar, text="", font=(FONT, 12), bg=BG, fg=MUTED)
        count.pack(side="right")
        return var, count

    # ==================================================================
    # Main menu
    # ==================================================================
    def main_menu(self):
        self.voter = None
        self.clear_container()
        wrap = tk.Frame(self.container, bg=BG)
        wrap.pack(fill="both", expand=True)

        card = tk.Frame(wrap, bg=PANEL, highlightthickness=2, highlightbackground=ACCENT)
        card.place(relx=0.5, rely=0.5, anchor="center")
        inner = tk.Frame(card, bg=PANEL)
        inner.pack(padx=80, pady=56)

        tk.Label(inner, text="VOTING ASSISTANT", font=("Georgia", 38, "bold"), bg=PANEL, fg=ACCENT).pack()
        tk.Label(inner, text="Secure  •  Simple  •  Transparent", font=(FONT, 13),
                 bg=PANEL, fg=MUTED).pack(pady=(6, 26))
        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", pady=(0, 30))

        make_button(inner, "Admin Login", self.admin_login, "secondary", size=17, width=24, pady=14).pack(pady=10)
        make_button(inner, "User Login", self.user_login, "primary", size=17, width=24, pady=14).pack(pady=10)

        status_color = "#4CAF7A" if self.is_on else "#D9534F"
        status_text = "●  Voting is OPEN" if self.is_on else "●  Voting is CLOSED"
        tk.Label(inner, text=status_text, font=(FONT, 12, "bold"), bg=PANEL, fg=status_color).pack(pady=(26, 0))

    # ==================================================================
    # Admin login
    # ==================================================================
    def admin_login(self):
        win, body = self.make_dialog("Admin Login", "Admin Login")
        user = self.form_field(body, "Username")
        pwd = self.form_field(body, "Password", show="•")

        @db_safe
        def submit(_=None):
            username, password = user.get().strip(), pwd.get()
            if not username or not password:
                messagebox.showerror("Login", "Enter username and password.", parent=win)
                return
            rows = self.db_all("SELECT role FROM users WHERE username = %s AND pwd = %s", (username, password))
            if any(r[0] == "admin" for r in rows):
                win.destroy()
                self.admin_panel()
            elif rows:
                messagebox.showerror("Access Denied", "You are not authorized as admin.", parent=win)
                pwd.delete(0, "end")
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.", parent=win)
                pwd.delete(0, "end")

        btns = tk.Frame(body, bg=PANEL)
        btns.pack(fill="x", pady=(22, 0))
        make_button(btns, "Login", submit, "primary", width=12).pack(side="left", expand=True, padx=(0, 6))
        make_button(btns, "Cancel", win.destroy, "secondary", width=12).pack(side="left", expand=True, padx=(6, 0))
        win.bind("<Return>", submit)
        win.bind("<Escape>", lambda e: win.destroy())
        self.open_dialog(win, user)

    # ==================================================================
    # Voter login
    # ==================================================================
    def user_login(self):
        if not self.is_on:
            messagebox.showinfo("Voting Closed", "Voting is not open right now.\nPlease try again later.")
            return
        win, body = self.make_dialog("User Login", "Voter Login")
        ident = self.form_field(body, "Aadhar / Voter ID number")
        pwd = self.form_field(body, "Password", show="•")

        @db_safe
        def submit(_=None):
            ident_val, password = ident.get().strip(), pwd.get()
            if not ident_val or not password:
                messagebox.showerror("Login", "Enter your ID and password.", parent=win)
                return
            row = self.db_one(
                "SELECT user_id, username, gender, adharId, voterID, is_voted, role, photo_path "
                "FROM users WHERE (voterID = %s OR adharId = %s) AND pwd = %s",
                (ident_val, ident_val, password))
            if not row:
                messagebox.showerror("Login Failed", "Invalid ID or password.", parent=win)
                pwd.delete(0, "end")
                return
            uid, name, gender, aadhar, voter_id, is_voted, role, photo = row
            if role != "voter":
                messagebox.showerror("Not Allowed", "Admin accounts cannot vote.", parent=win)
                return
            if is_voted:
                messagebox.showwarning("Already Voted", "You have already cast your vote.", parent=win)
                return
            self.voter = dict(uid=uid, name=name, gender=gender, aadhar=aadhar, voter_id=voter_id, photo=photo)
            win.destroy()
            self.voting_screen()

        btns = tk.Frame(body, bg=PANEL)
        btns.pack(fill="x", pady=(22, 0))
        make_button(btns, "Login", submit, "primary", width=12).pack(side="left", expand=True, padx=(0, 6))
        make_button(btns, "Cancel", win.destroy, "secondary", width=12).pack(side="left", expand=True, padx=(6, 0))
        win.bind("<Return>", submit)
        win.bind("<Escape>", lambda e: win.destroy())
        self.open_dialog(win, ident)

    # ==================================================================
    # Admin dashboard
    # ==================================================================
    @db_safe
    def admin_panel(self):
        def status_badge(parent):
            color = "#4CAF7A" if self.is_on else "#D9534F"
            text = "●  Voting OPEN" if self.is_on else "●  Voting CLOSED"
            tk.Label(parent, text=text, font=(FONT, 12, "bold"), bg=HEADER, fg=color).pack()

        body = self.new_screen("Admin Dashboard", back=self.main_menu, back_text="⏻  Logout", right=status_badge)

        total, voted = self.db_one("SELECT COUNT(*), COALESCE(SUM(is_voted), 0) FROM users WHERE role = 'voter'")
        total, voted = int(total), int(voted)
        cands = int(self.db_one("SELECT COUNT(*) FROM candidates")[0])

        content = tk.Frame(body, bg=BG)
        content.place(relx=0.5, rely=0.5, anchor="center")

        # --- stat cards -------------------------------------------------
        stats = tk.Frame(content, bg=BG)
        stats.pack(pady=(0, 24))
        for i, (label, value) in enumerate([("Registered Voters", total), ("Votes Cast", voted),
                                            ("Candidates", cands)]):
            c = tk.Frame(stats, bg=PANEL, highlightthickness=1, highlightbackground=BORDER)
            c.grid(row=0, column=i, padx=14)
            tk.Label(c, text=str(value), font=(FONT, 28, "bold"), bg=PANEL, fg=ACCENT, width=8).pack(pady=(14, 0))
            tk.Label(c, text=label, font=(FONT, 11), bg=PANEL, fg=MUTED).pack(pady=(0, 14), padx=20)

        # --- action buttons (3 x 3 grid) ---------------------------------
        grid = tk.Frame(content, bg=BG)
        grid.pack()
        vote_text = "■  Stop Voting" if self.is_on else "▶  Start Voting"
        actions = [
            ("＋  Add New User", self.add_new_user, "secondary"),
            ("＋  Add Candidate", self.add_candidate_window, "secondary"),
            (vote_text, self.toggle_voting, "danger" if self.is_on else "success"),
            ("☰  Show Users", self.show_users, "secondary"),
            ("☰  Show Candidates", self.show_candidates, "secondary"),
            ("↺  Reset All Votes", self.reset_voting, "danger"),
            ("🏆  Show Result", self.show_result, "secondary"),
            ("▥  Show Graph", self.show_graph, "secondary"),
            ("✕  Exit", self.exit_app, "secondary"),
        ]
        for i, (text, cmd, kind) in enumerate(actions):
            make_button(grid, text, cmd, kind, size=15, width=22, pady=22).grid(
                row=i // 3, column=i % 3, padx=12, pady=12)

    def toggle_voting(self):
        self.is_on = not self.is_on
        messagebox.showinfo("Voting", "Voting is now OPEN." if self.is_on else "Voting is now CLOSED.")
        self.admin_panel()

    @db_safe
    def reset_voting(self):
        if not messagebox.askyesno("Reset Votes",
                                   "This will erase ALL votes and let every voter vote again.\n\nContinue?",
                                   icon="warning"):
            return
        self.db_exec("UPDATE users SET is_voted = 0, voted_condi = 0")
        self.db_exec("UPDATE candidates SET voter = 0")
        messagebox.showinfo("Reset", "Voting has been reset successfully.")
        self.admin_panel()

    def exit_app(self):
        if messagebox.askyesno("Exit", "Close the Voting Assistant?"):
            try:
                self.conn.close()
            except Exception:
                pass
            self.root.destroy()

    # ==================================================================
    # Add user
    # ==================================================================
    def add_new_user(self):
        win, body = self.make_dialog("Add New User", "Add New User")
        cols = tk.Frame(body, bg=PANEL)
        cols.pack()
        left = tk.Frame(cols, bg=PANEL)
        left.pack(side="left", padx=(0, 34))
        right = tk.Frame(cols, bg=PANEL)
        right.pack(side="left", anchor="n", pady=(26, 0))

        name = self.form_field(left, "Full Name")
        aadhar = self.form_field(left, "Aadhar Card Number (12 digits)")
        voter_id = self.form_field(left, "Voter ID Card Number")
        gender = self.form_combo(left, "Gender", ["Male", "Female", "Other"])
        pwd = self.form_field(left, "Password", show="•")

        holder = {"path": None}
        self.photo_picker(right, holder).pack()

        @db_safe
        def submit(_=None):
            u, a, v, g, p = name.get().strip(), aadhar.get().strip(), voter_id.get().strip(), gender.get(), pwd.get()
            if not u or not p:
                return messagebox.showerror("Error", "Name and password are required.", parent=win)
            if not re.fullmatch(r"\d{12}", a):
                return messagebox.showerror("Error", "Invalid Aadhar (must be 12 digits).", parent=win)
            if not re.fullmatch(r"[A-Za-z0-9]{5,15}", v):
                return messagebox.showerror("Error", "Invalid Voter ID (5-15 letters/digits).", parent=win)
            if g not in ("Male", "Female", "Other"):
                return messagebox.showerror("Error", "Select a gender.", parent=win)
            photo_path = None
            try:
                photo_path = self.save_image(holder["path"], "user")
                self.db_exec("INSERT INTO users (username, pwd, adharId, voterID, gender, role, photo_path) "
                             "VALUES (%s, %s, %s, %s, %s, 'voter', %s)", (u, p, a, v, g, photo_path))
            except mysql.connector.Error as err:
                self.delete_image(photo_path)
                msg = "That Aadhar or Voter ID is already registered." if getattr(err, "errno", 0) == 1062 else str(err)
                return messagebox.showerror("Database Error", msg, parent=win)
            messagebox.showinfo("Success", "User registered successfully.", parent=win)
            win.destroy()
            self.admin_panel()

        btns = tk.Frame(body, bg=PANEL)
        btns.pack(fill="x", pady=(24, 0))
        make_button(btns, "Register", submit, "primary", width=16).pack(side="left", expand=True, padx=(0, 8))
        make_button(btns, "Cancel", win.destroy, "secondary", width=16).pack(side="left", expand=True, padx=(8, 0))
        win.bind("<Escape>", lambda e: win.destroy())
        self.open_dialog(win, name)

    # ==================================================================
    # Add candidate
    # ==================================================================
    def add_candidate_window(self):
        win, body = self.make_dialog("Add Candidate", "Register New Candidate")
        cols = tk.Frame(body, bg=PANEL)
        cols.pack()
        left = tk.Frame(cols, bg=PANEL)
        left.pack(side="left", padx=(0, 34))
        right = tk.Frame(cols, bg=PANEL)
        right.pack(side="left", anchor="n", pady=(10, 0))

        name = self.form_field(left, "Candidate Name")
        age = self.form_field(left, "Age")
        gender = self.form_combo(left, "Gender", ["Male", "Female", "Other"])
        party = self.form_field(left, "Party Name")
        symbol = self.form_field(left, "Party Symbol Name")

        holder = {"path": None}
        symbol_holder = {"path": None}
        tk.Label(right, text="Candidate Photo", font=(FONT, 11), bg=PANEL, fg=MUTED).pack(anchor="w")
        self.photo_picker(right, holder, size=(130, 130)).pack(pady=(4, 14))
        tk.Label(right, text="Party Symbol Image", font=(FONT, 11), bg=PANEL, fg=MUTED).pack(anchor="w")
        self.photo_picker(right, symbol_holder, size=(100, 100), button_text="Choose Symbol",
                          mode="contain", placeholder="No Symbol").pack(pady=(4, 0))

        @db_safe
        def submit(_=None):
            n, a, g, p, s = name.get().strip(), age.get().strip(), gender.get(), party.get().strip(), symbol.get().strip()
            if not re.fullmatch(r"[A-Za-z ]{3,25}", n):
                return messagebox.showerror("Error", "Invalid name (3-25 letters only).", parent=win)
            if not re.fullmatch(r"\d{1,2}", a) or not 18 <= int(a) <= 99:
                return messagebox.showerror("Error", "Invalid age (must be between 18 and 99).", parent=win)
            if g not in ("Male", "Female", "Other"):
                return messagebox.showerror("Error", "Select a gender.", parent=win)
            if not re.fullmatch(r"[A-Za-z0-9 .-]{3,30}", p):
                return messagebox.showerror("Error", "Invalid party name (3-30 characters).", parent=win)
            if not re.fullmatch(r"[A-Za-z0-9 _-]{2,20}", s):
                return messagebox.showerror("Error", "Invalid party symbol (2-20 characters).", parent=win)
            photo_path = symbol_path = None
            try:
                photo_path = self.save_image(holder["path"], "cand")
                symbol_path = self.save_image(symbol_holder["path"], "sym")
                self.db_exec("INSERT INTO candidates (name, age, gender, party_name, symbol, photo_path, symbol_path) "
                             "VALUES (%s, %s, %s, %s, %s, %s, %s)", (n, int(a), g, p, s, photo_path, symbol_path))
            except mysql.connector.Error as err:
                self.delete_image(photo_path)
                self.delete_image(symbol_path)
                return messagebox.showerror("Database Error", str(err), parent=win)
            messagebox.showinfo("Success", "Candidate registered successfully.", parent=win)
            win.destroy()
            self.admin_panel()

        btns = tk.Frame(body, bg=PANEL)
        btns.pack(fill="x", pady=(24, 0))
        make_button(btns, "Register Candidate", submit, "primary", width=16).pack(side="left", expand=True, padx=(0, 8))
        make_button(btns, "Cancel", win.destroy, "secondary", width=16).pack(side="left", expand=True, padx=(8, 0))
        win.bind("<Escape>", lambda e: win.destroy())
        self.open_dialog(win, name)

    # ==================================================================
    # Show users
    # ==================================================================
    @db_safe
    def show_users(self):
        body = self.new_screen("Registered Users", back=self.admin_panel, back_text="←  Dashboard")
        var, count = self.search_bar(body, lambda: self.load_users(var.get(), count), lambda: (
            var.set(""), self.load_users("", count)))
        self.users_table = self.build_table(
            body, ("ID", "Username", "Aadhar No", "Voter ID", "Gender", "Role", "Voted"),
            (70, 180, 180, 160, 110, 110, 90))
        self.load_users("", count)

    @db_safe
    def load_users(self, keyword, count_label):
        sql = ("SELECT user_id, username, adharId, voterID, gender, role, is_voted, photo_path FROM users")
        params = ()
        keyword = keyword.strip().lower()
        if keyword:
            sql += " WHERE LOWER(username) LIKE %s OR LOWER(adharId) LIKE %s OR LOWER(voterID) LIKE %s"
            params = (f"%{keyword}%",) * 3
        rows = self.db_all(sql + " ORDER BY user_id", params)

        self.users_table.delete(*self.users_table.get_children())
        self.user_photos = []
        for i, r in enumerate(rows):
            photo = self.make_thumb(r[7], THUMB)
            self.user_photos.append(photo)
            self.users_table.insert("", "end", image=photo, tags=("odd" if i % 2 else "even",),
                                    values=(r[0], r[1], r[2], r[3], r[4], r[5].capitalize(),
                                            "Yes" if r[6] else "No"))
        count_label.config(text=f"{len(rows)} user(s)")

    # ==================================================================
    # Show candidates
    # ==================================================================
    @db_safe
    def show_candidates(self):
        body = self.new_screen("Candidates", back=self.admin_panel, back_text="←  Dashboard")
        var, count = self.search_bar(body, lambda: self.load_candidates(var.get(), count), lambda: (
            var.set(""), self.load_candidates("", count)))
        self.candidate_table = self.build_table(
            body, ("ID", "Name", "Age", "Gender", "Party", "Symbol"), (70, 210, 80, 110, 230, 130),
            photo_heading="Photo / Symbol", photo_width=175)
        self.load_candidates("", count)

    @db_safe
    def load_candidates(self, keyword, count_label):
        sql = ("SELECT candidate_id, name, age, gender, party_name, symbol, photo_path, symbol_path "
               "FROM candidates")
        params = ()
        keyword = keyword.strip().lower()
        if keyword:
            sql += " WHERE LOWER(name) LIKE %s OR LOWER(party_name) LIKE %s OR LOWER(symbol) LIKE %s"
            params = (f"%{keyword}%",) * 3
        rows = self.db_all(sql + " ORDER BY candidate_id", params)

        self.candidate_table.delete(*self.candidate_table.get_children())
        self.cand_photos = []
        for i, r in enumerate(rows):
            photo = self.make_pair_thumb(r[6], r[7])
            self.cand_photos.append(photo)
            self.candidate_table.insert("", "end", image=photo, tags=("odd" if i % 2 else "even",), values=r[:6])
        count_label.config(text=f"{len(rows)} candidate(s)")

    # ==================================================================
    # Voting screen
    # ==================================================================
    @db_safe
    def voting_screen(self):
        v = self.voter
        body = self.new_screen("Cast Your Vote", back=self.cancel_voting, back_text="←  Cancel")

        # --- voter strip ------------------------------------------------
        strip = tk.Frame(body, bg=PANEL, highlightthickness=1, highlightbackground=BORDER)
        strip.pack(fill="x")
        self.voter_photo = self.make_thumb(v["photo"], (72, 72))
        tk.Label(strip, image=self.voter_photo, bg=PANEL).pack(side="left", padx=16, pady=12)
        info = tk.Frame(strip, bg=PANEL)
        info.pack(side="left")
        tk.Label(info, text=v["name"], font=(FONT, 17, "bold"), bg=PANEL, fg=TEXT, anchor="w").pack(anchor="w")
        tk.Label(info, text=f"Voter ID: {v['voter_id']}     •     Gender: {v['gender']}",
                 font=(FONT, 12), bg=PANEL, fg=MUTED).pack(anchor="w", pady=(2, 0))
        tk.Label(strip, text="Select ONE candidate, then press  Cast Vote", font=(FONT, 12),
                 bg=PANEL, fg=ACCENT).pack(side="right", padx=24)

        # --- footer (packed before the scroll area so it is always visible)
        footer = tk.Frame(body, bg=BG)
        footer.pack(side="bottom", fill="x", pady=(14, 0))
        self.selected_label = tk.Label(footer, text="No candidate selected", font=(FONT, 13), bg=BG, fg=MUTED)
        self.selected_label.pack(side="left")
        self.cast_btn = make_button(footer, "✔  Cast Vote", self.confirm_and_vote, "success", size=15, pady=11,
                                    padx=36)
        self.cast_btn.pack(side="right")
        self.cast_btn.config(state="disabled", bg=PANEL_ALT)

        candidates = self.db_all("SELECT candidate_id, name, party_name, symbol, photo_path, symbol_path "
                                 "FROM candidates ORDER BY candidate_id")
        if not candidates:
            tk.Label(body, text="No candidates are available yet.", font=(FONT, 18), bg=BG, fg="#D9534F").pack(
                expand=True)
            return

        # --- scrollable candidate grid -----------------------------------
        area = tk.Frame(body, bg=BG)
        area.pack(fill="both", expand=True, pady=(16, 0))
        canvas = tk.Canvas(area, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(area, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        grid = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0, 0), window=grid, anchor="nw")

        self.candidate_var = tk.IntVar(value=0)
        self.candidate_info = {}
        self.card_widgets = {}
        self.vote_photos = []
        cards = []
        for cid, name, party, symbol, photo_path, symbol_path in candidates:
            self.candidate_info[cid] = (name, party)
            cards.append(self.make_candidate_card(grid, cid, name, party, symbol, photo_path, symbol_path))
        self.candidate_var.trace_add("write", self.refresh_selection)

        state = {"cols": 0}

        def relayout(_=None):
            w = canvas.winfo_width()
            canvas.itemconfigure(win_id, width=w)
            cols = max(1, min(len(cards), w // 262))
            if cols != state["cols"]:
                state["cols"] = cols
                for i, card in enumerate(cards):
                    card.grid(row=i // cols, column=i % cols, padx=14, pady=14, sticky="n")
                for c in range(len(cards)):
                    grid.columnconfigure(c, weight=1 if c < cols else 0)
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind("<Configure>", relayout)
        grid.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        def wheel(e):
            if e.num == 4:
                canvas.yview_scroll(-1, "units")
            elif e.num == 5:
                canvas.yview_scroll(1, "units")
            else:
                canvas.yview_scroll(int(-e.delta / 120), "units")

        def bind_wheel(_):
            for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                canvas.bind_all(seq, wheel)

        def unbind_wheel(_):
            for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                canvas.unbind_all(seq)

        canvas.bind("<Enter>", bind_wheel)
        canvas.bind("<Leave>", unbind_wheel)
        canvas.bind("<Destroy>", unbind_wheel)

    def make_candidate_card(self, parent, cid, name, party, symbol, photo_path, symbol_path):
        card = tk.Frame(parent, bg=PANEL, highlightthickness=3, highlightbackground=BORDER,
                        cursor="hand2", width=230, height=365)
        card.pack_propagate(False)
        widgets = [card]

        photo = self.make_thumb(photo_path, (150, 150))
        self.vote_photos.append(photo)
        img = tk.Label(card, image=photo, bg=PANEL)
        img.pack(pady=(14, 0))
        widgets.append(img)

        for text, font, color, pad in ((name, (FONT, 16, "bold"), TEXT, (10, 2)),
                                       (party, (FONT, 12), ACCENT, (0, 4))):
            lbl = tk.Label(card, text=text, font=font, bg=PANEL, fg=color, wraplength=190, justify="center")
            lbl.pack(pady=pad)
            widgets.append(lbl)

        # party symbol: image (if uploaded) + its name
        sym_row = tk.Frame(card, bg=PANEL)
        sym_row.pack(pady=(2, 8))
        widgets.append(sym_row)
        if symbol_path:
            sym_img = self.make_thumb(symbol_path, (64, 64), mode="contain")
            self.vote_photos.append(sym_img)
            lbl = tk.Label(sym_row, image=sym_img, bg=PANEL)
            lbl.pack(side="left", padx=(0, 10))
            widgets.append(lbl)
        if symbol or not symbol_path:
            lbl = tk.Label(sym_row, text=symbol or "—", font=(FONT, 13, "bold"), bg=PANEL, fg=TEXT,
                           wraplength=110)
            lbl.pack(side="left")
            widgets.append(lbl)

        tag = tk.Label(card, text="Click to select", font=(FONT, 11, "bold"), bg=PANEL, fg=MUTED)
        tag.pack()
        widgets.append(tag)
        for w in widgets:
            w.bind("<Button-1>", lambda e, c=cid: self.candidate_var.set(c))
        self.card_widgets[cid] = (card, tag)
        return card

    def refresh_selection(self, *_):
        selected = self.candidate_var.get()
        for cid, (card, tag) in self.card_widgets.items():
            if cid == selected:
                card.config(highlightbackground=ACCENT)
                tag.config(text="✔  SELECTED", fg=ACCENT)
            else:
                card.config(highlightbackground=BORDER)
                tag.config(text="Click to select", fg=MUTED)
        if selected in self.candidate_info:
            self.selected_label.config(text=f"Selected:  {self.candidate_info[selected][0]}", fg=TEXT)
            self.cast_btn.config(state="normal", bg=GREEN)

    def confirm_and_vote(self):
        cid = self.candidate_var.get()
        if cid not in self.candidate_info:
            messagebox.showerror("Vote", "Please select a candidate before voting.")
            return
        name, party = self.candidate_info[cid]
        if messagebox.askyesno("Confirm Your Vote",
                               f"You are voting for:\n\n{name}\n({party})\n\n"
                               "Your vote cannot be changed afterwards.\nContinue?", icon="question"):
            self.submit_vote(cid)

    @db_safe
    def submit_vote(self, cid):
        self.conn.ping(reconnect=True, attempts=2, delay=1)
        self.conn.start_transaction()
        cur = self.conn.cursor()
        try:
            # only succeeds if this voter has not voted yet -> no double voting
            cur.execute("UPDATE users SET is_voted = 1, voted_condi = 1 "
                        "WHERE user_id = %s AND is_voted = 0 AND role = 'voter'", (self.voter["uid"],))
            if cur.rowcount != 1:
                self.conn.rollback()
                messagebox.showerror("Vote", "You have already voted.")
                self.main_menu()
                return
            cur.execute("UPDATE candidates SET voter = voter + 1 WHERE candidate_id = %s", (cid,))
            if cur.rowcount != 1:
                self.conn.rollback()
                messagebox.showerror("Vote", "That candidate no longer exists. Please try again.")
                self.voting_screen()
                return
            self.conn.commit()
        except mysql.connector.Error:
            self.conn.rollback()
            raise
        finally:
            cur.close()
        messagebox.showinfo("Thank You", "✅  Your vote has been recorded successfully!")
        self.main_menu()

    def cancel_voting(self):
        if messagebox.askyesno("Cancel", "Leave without voting?"):
            self.main_menu()

    # ==================================================================
    # Results
    # ==================================================================
    @db_safe
    def show_result(self):
        body = self.new_screen("Election Result", back=self.admin_panel, back_text="←  Dashboard")
        rows = self.db_all("SELECT name, party_name, voter, photo_path, symbol_path FROM candidates "
                           "ORDER BY voter DESC, name")
        total_votes = sum(r[2] for r in rows)

        if not rows:
            text, color = "No candidates have been added yet.", MUTED
        elif total_votes == 0:
            text, color = "No votes have been cast yet.", MUTED
        else:
            top = rows[0][2]
            winners = [r[0] for r in rows if r[2] == top]
            if len(winners) > 1:
                text, color = f"🤝  It's a tie between {', '.join(winners)}  ({top} votes each)", ACCENT
            else:
                text, color = f"🏆  Winner: {winners[0]}  with {top} votes", ACCENT

        banner = tk.Frame(body, bg=PANEL, highlightthickness=2, highlightbackground=ACCENT if total_votes else BORDER)
        banner.pack(fill="x", pady=(0, 18))
        tk.Label(banner, text=text, font=("Georgia", 24, "bold"), bg=PANEL, fg=color,
                 wraplength=1000, pady=18).pack()
        total, voted = self.db_one("SELECT COUNT(*), COALESCE(SUM(is_voted), 0) FROM users WHERE role = 'voter'")
        total, voted = int(total), int(voted)
        turnout = f"{voted / total * 100:.1f}%" if total else "0%"
        tk.Label(banner, text=f"Turnout: {voted} of {total} registered voters ({turnout})",
                 font=(FONT, 12), bg=PANEL, fg=MUTED).pack(pady=(0, 14))

        table = self.build_table(body, ("Rank", "Name", "Party", "Votes", "Share"), (80, 230, 250, 100, 100),
                                 photo_heading="Photo / Symbol", photo_width=175)
        self.result_photos = []
        rank, last = 0, None
        for i, (name, party, votes, photo_path, symbol_path) in enumerate(rows):
            if votes != last:
                rank, last = i + 1, votes
            photo = self.make_pair_thumb(photo_path, symbol_path)
            self.result_photos.append(photo)
            share = f"{votes / total_votes * 100:.1f}%" if total_votes else "0%"
            table.insert("", "end", image=photo, tags=("odd" if i % 2 else "even",),
                         values=(f"#{rank}", name, party, votes, share))

    # ==================================================================
    # Graphs
    # ==================================================================
    @db_safe
    def show_graph(self):
        body = self.new_screen("Voting Graphs", back=self.admin_panel, back_text="←  Dashboard")
        cands = self.db_all("SELECT name, voter FROM candidates ORDER BY candidate_id")
        genders = self.db_all("SELECT gender, COUNT(*) FROM users WHERE is_voted = 1 AND role = 'voter' "
                              "GROUP BY gender")
        status = dict(self.db_all("SELECT is_voted, COUNT(*) FROM users WHERE role = 'voter' GROUP BY is_voted"))

        if not cands or sum(c[1] for c in cands) == 0:
            tk.Label(body, text="No votes have been cast yet.", font=(FONT, 20), bg=BG, fg=MUTED).pack(expand=True)
            return

        names = [c[0] for c in cands]
        votes = [c[1] for c in cands]
        colors = [CHART_COLORS[i % len(CHART_COLORS)] for i in range(len(names))]

        fig = Figure(figsize=(11, 6), dpi=100, facecolor=PANEL)
        ax1, ax2, ax3, ax4 = fig.subplots(2, 2).flatten()

        def style(ax, title):
            ax.set_facecolor(PANEL)
            ax.set_title(title, color=ACCENT, fontsize=12, fontweight="bold", pad=10)
            ax.tick_params(colors=TEXT, labelsize=9)
            for spine in ax.spines.values():
                spine.set_color(BORDER)

        style(ax1, "Votes per Candidate")
        ax1.bar(names, votes, color=colors)
        ax1.set_ylabel("Votes", color=TEXT)
        ax1.tick_params(axis="x", rotation=25)
        ax1.yaxis.get_major_locator().set_params(integer=True)

        style(ax2, "Vote Share")
        with_votes = [(n, v, c) for n, v, c in zip(names, votes, colors) if v > 0]
        _, _, autotexts = ax2.pie([x[1] for x in with_votes], labels=[x[0] for x in with_votes],
                                  colors=[x[2] for x in with_votes], autopct="%1.1f%%", startangle=140,
                                  textprops={"color": TEXT, "fontsize": 9}, wedgeprops={"edgecolor": PANEL})
        for t in autotexts:
            t.set_color("#1E1F22")
        ax2.axis("equal")

        style(ax3, "Voted by Gender")
        g_names = [g[0] for g in genders]
        g_counts = [g[1] for g in genders]
        ax3.barh(g_names, g_counts, color=[CHART_COLORS[i + 1] for i in range(len(g_names))])
        ax3.set_xlabel("Number of votes", color=TEXT)
        ax3.xaxis.get_major_locator().set_params(integer=True)

        style(ax4, "Turnout")
        voted, not_voted = status.get(1, 0), status.get(0, 0)
        ax4.pie([voted, not_voted], labels=["Voted", "Not Voted"], colors=["#4C9F70", "#5A5D66"],
                autopct="%1.1f%%", startangle=90, textprops={"color": TEXT, "fontsize": 9},
                wedgeprops={"edgecolor": PANEL})
        ax4.axis("equal")

        fig.tight_layout(pad=2.5)
        frame = tk.Frame(body, bg=PANEL, highlightthickness=1, highlightbackground=BORDER)
        frame.pack(fill="both", expand=True)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = VotingAssistant(root)
    if app.failed:
        root.destroy()
    else:
        root.mainloop()
