import tkinter
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.ttk import Treeview, Style
import re
import mysql.connector
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class VotingAssistant:
    is_on = True

    bg = "yellow"

    # database connection
    try:
        def __init__(self, root):
            self.root = root
            root.geometry("800x500")
            root.title("Voting Assistant")
            root.state("zoomed")
            root.config(bg="#1E1F22")

            self.conn = mysql.connector.connect(
                host="localhost",
                database="voting_system",
                username="root",
                password="vikrant"
            )
            self.cursr = self.conn.cursor()
            self.main_menu()
    except:
        messagebox.showwarning("DatabaseError", "Try again after some time")

    def clear_screen(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, Frame):
                widget.destroy()

    # opening screen
    try:
        def main_menu(self):
            self.center_frame = Frame(self.root, bg="#1E1F22")
            self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
            self.main_frm = Frame(self.center_frame, bg="#26282E", height=500, width=500, borderwidth=1, relief="solid",
                                  highlightthickness=2, highlightbackground="#BEB09D")
            self.main_frm.pack(pady=10)

            title_label = Label(self.main_frm, text="VOTING ASSISTANT", font="georgia 50", bg="#1E1F22", fg="gray",
                                width=20)
            title_label.pack(pady=20)

            Button(self.main_frm, text="Admin Login", font=("Arial", 20), command=self.admin_login, borderwidth=1,
                   relief="solid", bg='#1E1F22', fg="#BEB09D", width=20).pack(pady=20, padx=20, ipadx=30, ipady=5)
            btn = Button(self.main_frm, text="User Login", font=("Arial", 20), borderwidth=1, relief="solid",
                         bg='#1E1F22',
                         fg="#BEB09D", width=20, command=self.user_login).pack(pady=20, padx=20, ipadx=30, ipady=5)
    except:
        messagebox.showerror("VA", "Error in Main Page")

    # admin login screen and check login
    try:
        def admin_login(self):
            self.admin_login_window = Toplevel(self.root)
            self.admin_login_window.title("Admin Login")
            self.admin_login_window.geometry("300x300")
            self.admin_login_window.config(bg="#1E1F22")

            Label(self.admin_login_window, text="Admin Login", font=("Georgia", 20), bg="#1E1F22", fg="white").pack(
                pady=5,
                padx=5)
            Label(self.admin_login_window, text="Username", font=("Arial", 20), bg="#1E1F22", fg="white").pack(pady=5,
                                                                                                               padx=5)
            self.admin_username = Entry(self.admin_login_window, font=("Arial", 20), relief="solid", width=15)
            self.admin_username.pack(pady=5, padx=5)

            Label(self.admin_login_window, text="Password", font=("Arial", 20), bg="#1E1F22", fg="white").pack(pady=5,
                                                                                                               padx=5)
            self.admin_password = Entry(self.admin_login_window, font=("Arial", 20), show="*", relief="solid",
                                        borderwidth=1, width=15)
            self.admin_password.pack(pady=5, padx=5)

            Button(self.admin_login_window, text="Login", font=("Arial", 20), command=self.check_admin_login,
                   bg='#1E1F22', fg="#BEB09D", width=15).pack(pady=5, padx=5)

            Button(self.admin_login_window, text="Back", font=("Arial", 20), command=self.main_menu,
                   bg='#1E1F22', fg="#BEB09D", width=15).pack(pady=5, padx=5)


        def check_admin_login(self):
            if self.conn.is_connected():
                query = "SELECT * FROM users WHERE username = %s AND pwd = %s"
                self.cursr.execute(query, (self.admin_username.get(), self.admin_password.get()))
                user = self.cursr.fetchone()
                if user:
                    if user[8] == "admin":
                        messagebox.showinfo("Login Success", "Admin login successful")

                        self.admin_window_frame()

                        self.admin_username.delete(0, END)
                        self.admin_password.delete(0, END)
                        self.admin_login_window.destroy()
                        self.main_frm.destroy()
                    else:
                        messagebox.showerror("Access Denied", "You are not authorized as admin")

                        self.admin_username.delete(0, END)
                        self.admin_password.delete(0, END)
                        self.admin_login_window.destroy()
                        # self.main_frm.destroy()

                else:
                    messagebox.showerror("Login Failed", "Invalid Username or Password")
                    self.admin_username.delete(0, END)
                    self.admin_password.delete(0, END)
                    self.admin_login_window.destroy()

            else:
                messagebox.showerror("Server Error", "Try again ")
    except:
        messagebox.showerror("VA", "Error in Admin login or Check Login")

    # user login screen and check login
    try:
        def user_login(self):

            if self.is_on == False:
                messagebox.showinfo("VA", "Voting is off now")
            else:

                # self.center_frame.destroy()
                self.user_login_window = Toplevel(self.root)
                self.user_login_window.title("User Login")
                self.user_login_window.geometry("300x300")
                self.user_login_window.config(bg="#1E1F22")

                Label(self.user_login_window, text="User Login", font=("Georgia", 20), bg="#1E1F22", fg="white").pack(
                    pady=5,
                    padx=5)
                Label(self.user_login_window, text="Aadhar/Voter ID number", font=("Arial", 20), bg="#1E1F22",
                      fg="white").pack(pady=5,
                                       padx=5)
                self.user_username = Entry(self.user_login_window, font=("Arial", 20), relief="solid", borderwidth=1,
                                           width=15)
                self.user_username.pack(pady=5, padx=5)

                Label(self.user_login_window, text="Password", font=("Arial", 20), bg="#1E1F22", fg="white").pack(
                    pady=5,
                    padx=5)
                self.user_password = Entry(self.user_login_window, font=("Arial", 20), show="*", relief="solid",
                                           borderwidth=1, width=15)
                self.user_password.pack(pady=5, padx=5)

                Button(self.user_login_window, text="Login", font=("Arial", 20), command=self.check_user_login,
                       bg='#1E1F22', fg="#BEB09D", width=15).pack(pady=5, padx=5)
                Button(self.user_login_window, text="Back", font=("Arial", 20), command=self.main_menu,
                       bg='#1E1F22', fg="#BEB09D", width=15).pack(pady=5, padx=5)

        def check_user_login(self):
            if self.conn.is_connected():
                query = "SELECT * FROM users WHERE ( voterID = %s OR adharId = %s )AND pwd = %s"
                self.cursr.execute(query,
                                   (self.user_username.get(), self.user_username.get(), self.user_password.get()))
                user = self.cursr.fetchone()
                print(user)

                if user:
                    if user[8] == "voter" or user[8] == 'admin':
                        print(user)
                        if user[7] != 0:
                               messagebox.showwarning("Login Fail", "User is already Voted")
                        else:
                            messagebox.showinfo("Login Success", "User login successful")
                            # self.user_username.delete(0, END)
                            # self.user_password.delete(0, END)
                            self.set_username = user[1]
                            self.set_gender = user[5]
                            self.set_aadhar = user[3]
                            self.set_voter = user[4]
                            self.set_uid = user[0]
                            self.user_login_window.destroy()
                            self.voting_screen()



                    else:
                        self.user_login_window.destroy()
                        messagebox.showerror("Login Failed", " user Invalid Username or Password")
                        # self.user_username.delete(0, END)
                        # self.user_password.delete(0, END)
                        self.user_login_window.destroy()



                else:
                    messagebox.showerror("Login Failed", "not userInvalid Username or Password")
                    self.user_login_window.destroy()
            else:
                messagebox.showerror("Server Error", "Try again ")
    except:
        messagebox.showerror("VA", "Error in Usre login or Check Login")

    # start voting
    try:
        def start_voting(self):
            if self.is_on:
                messagebox.showinfo("VA", "Voting is off now")

                self.is_on = False
            else:
                messagebox.showinfo("VA", "Votin is on now")
                self.is_on = True
    except:
        messagebox.showerror("VA", "Error in Start Voting")

    # goto home page
    try:
        def go_to_home(self):
            self.clear_screen()
            self.center_frame.destroy()
            self.main_menu()
    except:
        messagebox.showerror("VA", "Error in Go to home page Btn")
    try:
        def rest_voting(self):
            if self.conn.is_connected():
                self.cursr.execute("UPDATE users SET is_voted = 0, voted_condi = 0")
                self.cursr.execute("UPDATE candidates SET voter = 0")
                self.conn.commit()

                messagebox.showinfo("Success", "Voting has been reset successfully!")
            else:
                messagebox.showerror("VA", "not")

    except:
        messagebox.showerror("VA", "not")

    # admin panel
    try:
        def admin_window_frame(self):
            self.center_frame.destroy()
            self.center_frame = Frame(self.root, bg="#1E1F22")
            self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
            self.admin_main_frm = Frame(self.center_frame, bg="#26282E", height=700, width=800, borderwidth=1,
                                        relief="solid",
                                        highlightthickness=2, highlightbackground="gray")
            self.admin_main_frm.pack(ipady=25, ipadx=25)
            title_label = Label(self.admin_main_frm, text="VOTIONG ASSISTANT", font="georgia 50", bg="#1E1F22",
                                fg="gray")
            title_label.grid(row=0, columnspan=3, pady=20, padx=20)

            Button(self.admin_main_frm, text="Add New User", font="Arial 20", bg='#1E1F22', fg="#BEB09D", width=20,
                   borderwidth=1, relief="solid", command=self.add_new_user).grid(row=1, column=0, padx=15, pady=15,
                                                                                  ipadx=10, ipady=20)
            Button(self.admin_main_frm, text="Add Candidate", font="Arial 20", bg='#1E1F22', fg="#BEB09D", width=20,
                   borderwidth=1, relief="solid", command=self.add_candidate_window).grid(row=1, column=1, padx=15,
                                                                                          pady=15,
                                                                                          ipadx=10, ipady=20)
            Button(self.admin_main_frm, text="Show Users ", font="Arial 20", bg='#1E1F22', fg="#BEB09D", width=20,
                   borderwidth=1, relief="solid", command=self.show_users).grid(row=1, column=2, padx=15, pady=15,
                                                                                ipadx=10, ipady=20)
            Button(self.admin_main_frm, text="Shown All Candidates", font="Arial 20", bg='#1E1F22', fg="#BEB09D",
                   width=20,
                   borderwidth=1, relief="solid", command=self.show_candidates).grid(row=2, column=0, padx=15, pady=15,
                                                                                     ipadx=10, ipady=20)
            Button(self.admin_main_frm, text="Show Result", font="Arial 20", bg='#1E1F22', fg="#BEB09D", width=20,
                   borderwidth=1,
                   relief="solid", command=self.show_result).grid(row=2, column=1, padx=15, pady=15, ipadx=10, ipady=20)
            Button(self.admin_main_frm, text="Show Graph", font="Arial 20", bg='#1E1F22', fg="#BEB09D", width=20,
                   borderwidth=1,
                   relief="solid", command=self.show_graph).grid(row=2, column=2, padx=15, pady=15, ipadx=10, ipady=20)
            Button(self.admin_main_frm, text="Start Voting", font="Arial 20", bg='#1E1F22', fg="#BEB09D", width=20,
                   borderwidth=1, relief="solid", command=self.start_voting).grid(row=3, column=0, padx=15, pady=15,
                                                                                  ipadx=10, ipady=20)
            Button(self.admin_main_frm, text="Go To Home Page", font="Arial 20", bg='#1E1F22', fg="#BEB09D", width=20,
                   borderwidth=1, relief="solid", command=self.go_to_home).grid(row=3, column=1, padx=15, pady=15,
                                                                                ipadx=10, ipady=20)
            Button(self.admin_main_frm, text="Exit", font="Arial 20", bg='#1E1F22', fg="#BEB09D", width=20,
                   borderwidth=1,
                   relief="solid", command=self.root.destroy).grid(row=4, column=1, padx=15, pady=15, ipadx=10,
                                                                   ipady=20)
            Button(self.admin_main_frm, text="Reset", font="Arial 20", bg='#1E1F22', fg="#BEB09D", width=20,
                   borderwidth=1,
                   relief="solid", command=self.rest_voting).grid(row=3, column=2, padx=15, pady=15, ipadx=10,
                                                                  ipady=20)
    except:
        messagebox.showerror("VA", "Error in Admin pannel")

    # voting window
    try:
        def submit_vote(self):
            voterid = self.set_uid
            selected = self.candidate_var.get()

            print(voterid, selected)

            if selected == 0:  # 0 means no selection for IntVar()
                messagebox.showerror("VA", "Please select a candidate before voting.")
                return

            self.cursr.execute("SELECT is_voted FROM users WHERE user_id = %s", (voterid,))
            voter = self.cursr.fetchone()
            print(voter)

            if not voter:
                messagebox.showerror("VA", "Voter not found.")
            elif voter[0] == '1':
                messagebox.showerror("VA", "You have already voted.")
            else:
                # Update candidate's vote count
                # qry ="UPDATE candidates SET voter =voter +1 WHERE candidate_id = %s"
                # self.cursr.execute("UPDATE candidates SET voter = voter + 1 WHERE candidate_id = 1",(selected,))
                self.cursr.execute(
                    "UPDATE users SET is_voted = 1  WHERE user_id = %s",
                    (voterid,)
                )
                self.cursr.execute(
                    "UPDATE candidates SET voter = voter + 1 WHERE candidate_id = %s",
                    (selected,)
                )
                # Mark user as voted
                # self.cursr.execute("UPDATE users SET Is_voted = 'yes' WHERE user_id = % ",(voterid,))

                self.conn.commit()
                messagebox.showinfo("VA", "✅ Your vote has been successfully recorded!")

                self.voting_screen_window.destroy()

        # def voting_screen(self):
        #     self.voting_screen_window = Toplevel(self.root)
        #     self.voting_screen_window.title("Voting Screen")
        #     self.voting_screen_window.geometry("500x600")
        #     self.voting_screen_window.config(bg="#1E1F22")
        #     self.voting_screen_window.state('zoomed')
        #
        #     Label(self.voting_screen_window, text="Voting System", font=("Georgia", 30),
        #           bg="#1E1F22", fg="white", width=25).pack(pady=10)
        #
        #     Label(self.voting_screen_window, text=f'👤 Username : {self.set_username}', font=("Arial", 18),
        #           bg="#1E1F22", fg="white").pack(pady=5)
        #     Label(self.voting_screen_window, text=f'Gender: {self.set_gender}', font=("Arial", 18),
        #           bg="#1E1F22", fg="white").pack(pady=5)
        #     Label(self.voting_screen_window, text=f'🆔 Voter IDv : {self.set_voter}', font=("Arial", 18),
        #           bg="#1E1F22", fg="white").pack(pady=5)
        #
        #     Label(self.voting_screen_window, text="Choose a Candidate", font=("Arial", 16),
        #           bg="#1E1F22", fg="white").pack(pady=15)
        #
        #     # Candidate selection using Radiobuttons
        #     self.candidate_var = IntVar()
        #     self.cursr.execute("SELECT candidate_id, name FROM candidates")
        #     candidates = self.cursr.fetchall()
        #
        #
        #
        #     if not candidates:
        #         Label(self.voting_screen_window, text="No candidates available.",
        #               font=("Arial", 16), bg="#1E1F22", fg="red").pack(pady=10)
        #         return
        #
        #
        #     cols = 2   # 👈 number of cards per row
        #     row = col = 0
        #
        #     for cid, cname in candidates:
        #
        #         card = Frame(self.voting_screen_window, bg="#26282E", bd=2, relief="ridge",width=50)
        #         card.pack(padx=20, pady=8)
        #         col += 1
        #         if col == cols:
        #             col = 0
        #             row += 1
        #
        #         Radiobutton(
        #             card,
        #             text=cname,
        #             variable=self.candidate_var,
        #             value=cid,
        #             font=("Arial", 20),
        #             bg="#1E1F22",
        #             fg="white",
        #             selectcolor="#ff69b4",
        #             activebackground="#1E1F22",
        #             activeforeground="white"
        #         ).grid(row=row,column=col, padx=15, pady=12)
        #
        #     Button(
        #         self.voting_screen_window,
        #         text="Cast Vote",
        #         command=self.submit_vote,
        #         bg="#1E1F22",
        #         fg="white",
        #         font=("Arial", 18),
        #         padx=20,
        #         pady=5
        #     ).pack(pady=20)
        def voting_screen(self):
            self.voting_screen_window = Toplevel(self.root)
            self.voting_screen_window.title("Voting Screen")
            self.voting_screen_window.geometry("500x600")
            self.voting_screen_window.config(bg="#1E1F22")
            self.voting_screen_window.state('zoomed')  # ✅ fixed

            Label(self.voting_screen_window, text="Voting System", font=("Georgia", 30),
                  bg="#1E1F22", fg="white", width=25).pack(pady=10)

            Label(self.voting_screen_window, text=f'👤 Username : {self.set_username}', font=("Arial", 18),
                  bg="#1E1F22", fg="white").pack(pady=5)
            Label(self.voting_screen_window, text=f'Gender: {self.set_gender}', font=("Arial", 18),
                  bg="#1E1F22", fg="white").pack(pady=5)
            Label(self.voting_screen_window, text=f'🆔 Voter ID : {self.set_voter}', font=("Arial", 18),
                  bg="#1E1F22", fg="white").pack(pady=5)

            Label(self.voting_screen_window, text="Choose a Candidate", font=("Arial", 16),
                  bg="#1E1F22", fg="white").pack(pady=15)

            self.candidate_var = IntVar()
            self.cursr.execute("SELECT candidate_id, name FROM candidates")
            candidates = self.cursr.fetchall()

            if not candidates:
                Label(self.voting_screen_window, text="No candidates available.",
                      font=("Arial", 16), bg="#1E1F22", fg="red").pack(pady=10)
                return

            grid_frame = Frame(self.voting_screen_window, bg="#1E1F22")
            grid_frame.pack(padx=20, pady=10, fill="both", expand=True)

            cols = 4
            row = col = 0

            for cid, cname in candidates:
                card = Frame(grid_frame, bg="#26282E", bd=2, relief="ridge", padx=10, pady=10)
                card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

                Radiobutton(
                    card,
                    text=cname,
                    variable=self.candidate_var,
                    value=cid,
                    font=("Arial", 18, "bold"),
                    indicatoron=0,
                    width=20,
                    pady=10,
                    bg="#26282E",
                    fg="white",
                    selectcolor="#ff69b4",
                    activebackground="#26282E",
                    activeforeground="white"
                ).pack(anchor="w")

                col += 1
                if col == cols:
                    col = 0
                    row += 1

            Button(
                self.voting_screen_window,
                text="Cast Vote",
                command=self.submit_vote,
                bg="#1E1F22",
                fg="white",
                font=("Arial", 18),
                padx=20,
                pady=5
            ).pack(pady=20)

            Button(self.voting_screen_window, text="Back", font="Arial 20", bg='#1E1F22', fg="#BEB09D", width=20,
                   borderwidth=1, relief="solid", command=self.admin_window_frame).pack(pady=20)

    except:
        messagebox.showerror("VA", "Error in voting window")

    # add new user and show table
    try:
        def add_new_user_fun(self):
            if self.conn.is_connected():
                # query = "insert into users (username, pwd, adharId, voterID, genter, role) values(%s,%s,%s,%s,%s,'regular')"
                # self.cursr.execute(query, (self.add_new_name.get(),self.add_new_password.get(),self.add_new_adharId.get(),self.add_new_voterId.get(),self.dr_gender.get()))
                # self.conn.commit()
                # messagebox.showinfo("VA","Registration Successful ")
                username = self.add_new_name.get()
                password = self.add_new_password.get()
                aadhar = self.add_new_adharId.get()
                voter_id = self.add_new_voterId.get()
                gender = self.dr_gender.get()

                # Validation
                if not re.fullmatch(r"\d{12}", aadhar):
                    messagebox.showerror("Error", "Invalid Aadhar (must be 12 digits)")
                    return
                if not re.fullmatch(r"[A-Za-z0-9]{5,15}", voter_id):
                    messagebox.showerror("Error", "Invalid Voter ID")
                    return
                if gender not in ["Male", "Female","Other"]:
                    messagebox.showerror("Error", "Select a valid gender")
                    return
                if not username or not password:
                    messagebox.showerror("Error", "All fields are required")
                    return

                # Hash password
                # hashed_pwd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

                try:
                    query = "INSERT INTO users (username, pwd, adharId, voterID, gender, role) VALUES (%s, %s, %s, %s, %s, 'regular')"
                    self.cursr.execute(query, (username, password, aadhar, voter_id, gender))
                    self.conn.commit()
                    messagebox.showinfo("Success", "User registered successfully.")
                    self.add_new_user_window.destroy()
                except mysql.connector.Error as err:
                    messagebox.showerror("DB Error", str(err))

        def add_new_user(self):
            # self.center_frame.destroy()
            self.add_new_user_window = Toplevel(self.root)
            self.add_new_user_window.title("Admin Login")
            self.add_new_user_window.geometry("500x700")
            self.add_new_user_window.config(bg="#1E1F22")

            Label(self.add_new_user_window, text="Add New User", font=("Georgia", 20), bg="#1E1F22", fg="white").pack(
                pady=5,
                padx=5)
            Label(self.add_new_user_window, text="Name", font=("Arial", 20), bg="#1E1F22", fg="white").pack(pady=5,
                                                                                                            padx=5)
            self.add_new_name = Entry(self.add_new_user_window, font=("Arial", 20), relief="solid", borderwidth=1,
                                      width=15)
            self.add_new_name.pack(pady=5, padx=5)

            Label(self.add_new_user_window, text="Aadhar Card Number ", font=("Arial", 20), bg="#1E1F22",
                  fg="white").pack(
                pady=5,
                padx=5)
            self.add_new_adharId = Entry(self.add_new_user_window, font=("Arial", 20), relief="solid", borderwidth=1,
                                         width=15)
            self.add_new_adharId.pack(pady=5, padx=5)

            Label(self.add_new_user_window, text="Voter Id Card Number ", font=("Arial", 20), bg="#1E1F22",
                  fg="white").pack(pady=5,
                                   padx=5)
            self.add_new_voterId = Entry(self.add_new_user_window, font=("Arial", 20), relief="solid", borderwidth=1,
                                         width=15)
            self.add_new_voterId.pack(pady=5, padx=5)

            Label(self.add_new_user_window, text="Select Gender", font=("Arial", 20), bg="#1E1F22", fg="white").pack(
                pady=5,
                padx=5)

            self.dr_gender = StringVar()
            self.dr_gender.set("Select Gender ")
            self.options = ["Select Gender ", "Male", "Female",'Other']
            self.dp_scale = OptionMenu(self.add_new_user_window, self.dr_gender, *self.options, )
            self.dp_scale.pack(pady=5, padx=5)

            Label(self.add_new_user_window, text="Password", font=("Arial", 20), bg="#1E1F22", fg="white").pack(pady=5,
                                                                                                                padx=5)
            self.add_new_password = Entry(self.add_new_user_window, font=("Arial", 20), show="*", relief="solid",
                                          borderwidth=1, width=15)
            self.add_new_password.pack(pady=5, padx=5)

            Button(self.add_new_user_window, text="Register", font=("Arial", 20), command=self.add_new_user_fun,
                   bg='#1E1F22', fg="#BEB09D", width=15).pack(pady=5, padx=5)
            Button(self.add_new_user_window, text="Back", font=("Arial", 20), command=self.add_new_user_window.destroy,
                   bg='#1E1F22', fg="#BEB09D", width=15).pack(pady=5, padx=5)

        def show_users(self):
            self.clear_screen()
            self.center_frame.destroy()

            self.center_frame = Frame(self.root)
            self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

            self.user_table_frame = Frame(
                self.center_frame, bg="#26282E",
                height=600, width=1100,
                borderwidth=1, relief="solid",
                highlightthickness=2, highlightbackground="gray"
            )
            self.user_table_frame.pack(fill="both", expand=True)
            self.user_table_frame.pack_propagate(False)

            title_label = Label(self.user_table_frame, text="USERS", font="georgia 40", bg="#1E1F22", fg="gray")
            title_label.pack(padx=20, pady=20)

            search_frame = Frame(self.user_table_frame, bg="#26282E")
            search_frame.pack(pady=5)

            self.search_var = StringVar()
            search_entry = Entry(search_frame, textvariable=self.search_var, font=("Arial", 14), width=30)
            search_entry.pack(side=LEFT, padx=10)

            search_btn = Button(search_frame, text="Search", font=("Arial", 12), bg="#1E1F22", fg="#BEB09D",
                                command=self.search_users)
            search_btn.pack(side=LEFT, padx=5)

            reset_btn = Button(search_frame, text="Reset", font=("Arial", 12), bg="#1E1F22", fg="#BEB09D",
                               command=self.load_all_users)
            reset_btn.pack(side=LEFT, padx=5)

            style = Style()
            style.configure("Treeview", font=("Arial", 14),rowheight=25)  # Rows font
            style.configure("Treeview.Heading", font=("Arial", 16, "bold"))

            self.users_table = Treeview(self.user_table_frame)
            self.users_table['columns'] = ('User_id', 'Username', 'Password', 'Adharcard_Id', 'Votercard_Id', 'Gender',
                                           'Role')

            for col in self.users_table['columns']:
                self.users_table.column(col, anchor="center", width=160)
                self.users_table.heading(col, text=col)

            self.users_table.config(show="headings")
            self.users_table.pack(fill="both", expand=True, padx=30, pady=30)

            scrollbar = Scrollbar(self.user_table_frame, orient="vertical", command=self.users_table.yview)
            scrollbar.pack(side=RIGHT, fill=Y)
            self.users_table.configure(yscrollcommand=scrollbar.set)

            self.load_all_users()

            Button(self.user_table_frame, text="Back", font="Arial 20", bg='#1E1F22', fg="#BEB09D", width=20,
                   borderwidth=1, relief="solid", command=self.admin_window_frame).pack(pady=20)

        def search_users(self):
            keyword = self.search_var.get().lower()
            if not keyword:
                self.load_all_users()
                return

            self.users_table.delete(*self.users_table.get_children())
            if self.conn.is_connected():
                query = """SELECT user_id, username, pwd, adharId, voterID, gender, role FROM users 
                           WHERE LOWER(username) LIKE %s OR LOWER(adharId) LIKE %s OR LOWER(voterID) LIKE %s"""
                search_term = f"%{keyword}%"
                self.cursr.execute(query, (search_term, search_term, search_term))
                rows = self.cursr.fetchall()
                for row in rows:
                    self.users_table.insert("", END, values=row)

        def load_all_users(self):
            self.users_table.delete(*self.users_table.get_children())
            if self.conn.is_connected():
                self.cursr.execute("SELECT user_id, username, pwd, adharId, voterID, gender, role FROM users")
                rows = self.cursr.fetchall()
                for row in rows:
                    self.users_table.insert("", END, values=row)
    except:
        messagebox.showerror("VA", "Error in add new user or see all user")

  


if __name__ == '__main__':
    root = Tk()
    appobj = VotingAssistant(root)
    root.mainloop()




