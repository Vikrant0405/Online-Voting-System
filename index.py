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


if __name__ == '__main__':
    root = Tk()
    appobj = VotingAssistant(root)
    root.mainloop()




