import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox
from PIL import Image, ImageTk, ImageSequence
from logic.auth import account_login, account_creation
from logic.models import new_car_owner


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("USA Parking Manager")
        self.geometry("1280x720")
        self.configure(bg="#e6e6e6")

        self.frames = {}
        self._initialize_fonts()
        self._initialize_frames()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.show_frame(LoginScreen)

    def _initialize_fonts(self):
        font_path = "ui/fonts/Helvetica.ttf"
        self.header_font = tkFont.Font(family=font_path, size=22, weight="bold")
        self.subheader_font = tkFont.Font(family=font_path, size=12)
        self.login_font = tkFont.Font(family=font_path, size=12)

    def _initialize_frames(self):
        for F in (LoadingScreen, LoginScreen, DashboardScreen):
            frame = F(self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, container, *args, **kwargs):
        frame = self.frames[container]
        frame.tkraise()


class LoadingScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#e6e6e6")
        self.master = master
        self.pack(fill="both", expand=True)

        self.gif_path = "ui/assets/loading.gif"
        self.gif = Image.open(self.gif_path)
        self.label = tk.Label(self, bg="#e6e6e6")
        self.label.pack(expand=True)

        self.frames = [ImageTk.PhotoImage(frame.copy().convert("RGBA")) for frame in ImageSequence.Iterator(self.gif)]
        self.frame_index = 0

        self.animate()

    def animate(self):
        frame = self.frames[self.frame_index]
        self.label.configure(image=frame)
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.after(50, self.animate)


class LoginScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#e6e6e6")
        self._configure_grid()
        self._create_error_frame()
        self._create_login_frame()

    def _configure_grid(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

    def _create_error_frame(self):
        self.frame_error = tk.Frame(self, bg="#ff0000", width=425, height=55)
        self.frame_error.pack_propagate(False)
        label_error = tk.Label(self.frame_error, text="Incorrect Username or Password", bg="#ff0000", fg="#ffffff", font=("Arial", 12))
        label_error.pack(expand=True, fill="x")

    def _create_login_frame(self):
        frame_login = tk.Frame(self, bg="#b80000", width=425, height=300, padx=20, pady=20)
        frame_login.grid(row=1, column=1)
        frame_login.grid_propagate(False)

        self._add_widgets_to_login_frame(frame_login)

    def _add_widgets_to_login_frame(self, frame_login):
        self._create_header(frame_login)
        self._add_spacer(frame_login)
        self._create_username_entry(frame_login)
        self._create_password_entry(frame_login)
        self._add_buttons(frame_login)

    def _create_header(self, frame_login):
        tk.Label(frame_login, text="Sign In", font=self.master.header_font, bg="#b80000", fg="white").grid(row=0, column=0, sticky="w")

    def _add_spacer(self, frame_login):
        label_spacer = tk.Canvas(frame_login, bg="#b80000", height=20, bd=0, highlightthickness=0)
        label_spacer.grid(row=1, column=0, sticky="ew")

    def _create_username_entry(self, frame_login):
        self.entry_username = tk.Entry(frame_login, font=self.master.login_font, bg="#b80000", fg="white", relief="flat", insertbackground="white")
        self.entry_username.grid(row=2, column=0, sticky="we")
        self.entry_username.insert(0, "Username")
        self._bind_entry_focus_events(self.entry_username, "Username")

        self.underline_username = tk.Canvas(frame_login, bg="white", height=0, highlightthickness=0)
        self.underline_username.grid(row=3, column=0, sticky="nsew")

        entry_spacer = tk.Canvas(frame_login, bg="#b80000", height=20, bd=0, highlightthickness=0)
        entry_spacer.grid(row=4, column=0, sticky="ew")

    def _create_password_entry(self, frame_login):
        self.entry_password = tk.Entry(frame_login, font=self.master.login_font, bg="#b80000", fg="white", relief="flat", insertbackground="white")
        self.entry_password.grid(row=5, column=0, sticky="we")
        self.entry_password.insert(0, "Password")
        self._bind_entry_focus_events(self.entry_password, "Password")

        self.underline_password = tk.Canvas(frame_login, bg="white", height=0, highlightthickness=0)
        self.underline_password.grid(row=6, column=0, sticky="nsew")

        eframe_spacer = tk.Canvas(frame_login, bg="#b80000", height=20, bd=0, highlightthickness=0)
        eframe_spacer.grid(row=7, column=0, sticky="ew")

    def _add_buttons(self, frame_login):
        frame_send_buttons = tk.Frame(frame_login, bg="#b80000")
        frame_send_buttons.grid(row=8, column=0, sticky="nsew")

        frame_send_buttons.grid_columnconfigure(0, weight=1)

        btn_login = tk.Button(frame_send_buttons, text="Login", bg="#ffcc00", fg="white", relief="flat", font=self.master.subheader_font, width=8, command=self.login)
        btn_login.grid(row=0, column=2, sticky="e")

        btn_close = tk.Button(frame_send_buttons, text="Close", bg="#cccccc", fg="black", relief="flat", font=self.master.subheader_font, width=8)
        btn_close.grid(row=0, column=0, sticky="e")

        frame_send_buttons.grid_columnconfigure(1, weight=0)

        btn_spacer = tk.Canvas(frame_send_buttons, bg="#b80000", width=5, height=0, bd=0, highlightthickness=0)
        btn_spacer.grid(row=0, column=1, sticky="ew")

    def _bind_entry_focus_events(self, entry, text):
        entry.bind("<FocusIn>", lambda _: self.on_focus(entry, text))
        entry.bind("<FocusOut>", lambda _: self.on_unfocus(entry, text))

    def login(self):
        self.frame_error.place_forget()
        username = self.entry_username.get()
        password = self.entry_password.get()

        if account_login(username, password):
            self.master.show_frame(LoadingScreen)
            self.master.title("USA Parking System |" + username)
            self.after(2000, lambda: self.master.show_frame(DashboardScreen))
        else:
            self.frame_error.place(relx=0.5, rely=0.2, anchor="center")

    def on_focus(self, entry, text):
        if entry.get() == text:
            entry.delete(0, tk.END)

        if entry is self.entry_username:
            self.fade_color(self.underline_username, "#fffff", "#ffcc00")

        if entry is self.entry_password:
            self.fade_color(self.underline_password, "#ffffff", "#ffcc00")
            entry.config(show="*")

    def on_unfocus(self, entry, text):
        if entry.get() == "":
            entry.insert(tk.END, text)

        if entry is self.entry_username:
            self.fade_color(self.underline_username, "#ffcc00", "#ffffff")

        if entry is self.entry_password:
            self.fade_color(self.underline_password, "#ffcc00", "#ffffff")
            if entry.get() == "":
                entry.insert(0, "Password")
            if entry.get() == "Password":
                entry.config(show="")

    def fade_color(self, widget, from_color, to_color, steps=10, delay=30):
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

        def rgb_to_hex(rgb):
            return "#{:02x}{:02x}{:02x}".format(*rgb)

        from_rgb = hex_to_rgb(from_color)
        to_rgb = hex_to_rgb(to_color)

        def step(i):
            if i > steps:
                return
            interpolated = tuple(
                int(from_rgb[j] + (to_rgb[j] - from_rgb[j]) * i / steps)
                for j in range(3)
            )
            widget.configure(bg=rgb_to_hex(interpolated))
            widget.after(delay, lambda: step(i + 1))

        step(0)


class DashboardScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#e6e6e6")
        self.sidebar()
        self.home_page()

    def sidebar(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        frame_sidebar = tk.Frame(self, bg='#b80000', width=300)
        frame_sidebar.grid(row=0, column=0, sticky='ns')
        frame_sidebar.grid_propagate(False)

        for i in range(3, 10):
            frame_sidebar.grid_rowconfigure(i, weight=0)
        frame_sidebar.grid_rowconfigure(9, weight=1)

        self._add_sidebar_logo(frame_sidebar)
        self._add_sidebar_buttons(frame_sidebar)
        self._add_footer(frame_sidebar)

    def _add_sidebar_logo(self, frame_sidebar):
        logo = Image.open('ui/assets/logo.png')
        self.tk_image = ImageTk.PhotoImage(logo)

        label_logo = tk.Label(frame_sidebar, image=self.tk_image, bg='#b80000')
        label_logo.grid(row=0, column=0, pady=5)

        tk.Frame(frame_sidebar, height=100, bg='#b80000').grid(row=1, column=0)

    def _add_sidebar_buttons(self, frame_sidebar):
        nav = {
            "Home": self.home_page,
            "Reservations": self.reservations_page,
            "Vehicles": None,
            "Accounts": self.accounts_page,
            "Map": None
        }
        for i, (name, page) in enumerate(nav.items(), start=2):
            button = tk.Button(
                frame_sidebar,
                font=self.master.header_font,
                text=name,
                bg='#b80000',
                fg="#ffffff",
                relief="flat",
                anchor="center",
                padx=20,
                command=page
            )
            button.grid(row=i, column=0, sticky="ew", padx=10, pady=5)

    def _add_footer(self, frame_sidebar):
        frame_footer = tk.Frame(frame_sidebar, bg='#ffcc00')
        frame_footer.grid(row=10, column=0, sticky='ew')
        footer_label = tk.Label(frame_footer, text="© 2025 JABOL", bg='#ffcc00')
        footer_label.pack(padx=10, pady=10)

    def home_page(self):
        self.page_home = tk.Frame(self, bg='#e6e6e6')
        self.page_home.grid(row=0, column=1, sticky='nsew')

        def new_car_owner_ui():
            self.frame_owner = tk.Frame(self.page_home, bg='#e6e6e6', relief='raised', width=300)
            self.frame_owner.grid(row=0, column=0)

            self.label_owner_name = tk.Label(self.frame_owner, text="Name", bg='#e6e6e6')
            self.label_owner_name.grid(row=0, column=0)

            self.entry_owner_name = tk.Entry(self.frame_owner, bg='#e6e6e6')
            self.entry_owner_name.grid(row=0, column=1)

            self.label_owner_type = tk.Label(self.frame_owner, text="Type", bg='#e6e6e6')
            self.label_owner_type.grid(row=1, column=0)

            self.entry_owner_type = tk.Entry(self.frame_owner, bg='#e6e6e6')
            self.entry_owner_type.grid(row=1, column=1)

            self.label_owner_email = tk.Label(self.frame_owner, text="Email", bg='#e6e6e6')
            self.label_owner_email.grid(row=2, column=0)

            self.entry_owner_email = tk.Entry(self.frame_owner, bg='#e6e6e6')
            self.entry_owner_email.grid(row=2, column=1)

            self.label_owner_number = tk.Label(self.frame_owner, text="Contact Number", bg='#e6e6e6')
            self.label_owner_number.grid(row=3, column=0)

            self.entry_owner_number = tk.Entry(self.frame_owner, bg='#e6e6e6')
            self.entry_owner_number.grid(row=3, column=1)

            def submit_owner():
                try:
                    owner_name = self.entry_owner_name.get()
                    owner_type = self.entry_owner_type.get()
                    email_address = self.entry_owner_email.get()
                    contact_number = self.entry_owner_number.get()

                    if new_car_owner(owner_name, email_address, owner_type, contact_number):
                        messagebox.askokcancel("Info","Successfully added" + owner_name)

                        self.entry_owner_name.delete(0, tk.END)
                        self.entry_owner_type.delete(0, tk.END)
                        self.entry_owner_email.delete(0, tk.END)
                        self.entry_owner_number.delete(0, tk.END)
                except Exception as e:
                    messagebox.showinfo("showerror", "Error")

            self.add_button = tk.Button(self.frame_owner, text="Submit", bg='#b80000', fg='#ffffff', relief='flat', command=submit_owner)
            self.add_button.grid(row=4, column=1, sticky='ew')

        new_car_owner_ui()

    def reservations_page(self):
        self.page_home.grid_forget()

        self.page_reservations = tk.Frame(self, bg='#e6e6e6')
        self.page_reservations.grid(row=0, column=1, sticky='nsew')

        self.label_placeholder = tk.Label(self.page_reservations, text="RESERVATIONS PAGE", bg='#e6e6e6', font=self.master.header_font)
        self.label_placeholder.grid(row=0, column=0, sticky='nsew')

    def accounts_page(self):
        self.page_accounts = tk.Frame(self, bg='#e6e6e6')
        self.page_accounts.grid(row=0, column=1, sticky='nsew')

        def new_admin_ui():
            self.frame_new_admin = tk.Frame(self.page_accounts, bg='#e6e6e6')
            self.frame_new_admin.grid(row=0, column=0, sticky='nsew')

            self.label_admin_name = tk.Label(self.frame_new_admin, text="Admin Name", bg='#e6e6e6')
            self.label_admin_name.grid(row=0, column=0)

            self.entry_admin_name = tk.Entry(self.frame_new_admin, bg='#e6e6e6')
            self.entry_admin_name.grid(row=0, column=1)

            self.label_admin_email = tk.Label(self.frame_new_admin, text="Admin Email", bg='#e6e6e6')
            self.label_admin_email.grid(row=1, column=0)

            self.entry_admin_email = tk.Entry(self.frame_new_admin, bg='#e6e6e6')
            self.entry_admin_email.grid(row=1, column=1)

            self.label_admin_user = tk.Label(self.frame_new_admin, text="Username", bg='#e6e6e6')
            self.label_admin_user.grid(row=2, column=0)

            self.entry_admin_user = tk.Entry(self.frame_new_admin, bg='#e6e6e6')
            self.entry_admin_user.grid(row=2, column=1)

            self.label_admin_password = tk.Label(self.frame_new_admin, text="Password", bg='#e6e6e6')
            self.label_admin_password.grid(row=3, column=0)

            self.entry_admin_password = tk.Entry(self.frame_new_admin, bg='#e6e6e6')
            self.entry_admin_password.grid(row=3, column=1)

            self.label_master_password = tk.Label(self.frame_new_admin, text="Master Password", bg='#e6e6e6')
            self.label_master_password.grid(row=4, column=0)

            self.entry_master_password = tk.Entry(self.frame_new_admin, bg='#e6e6e6')
            self.entry_master_password.grid(row=4, column=1)

            def submit_new_admin():
                try:
                    admin_name = self.entry_admin_name.get()
                    admin_email = self.entry_admin_email.get()
                    admin_user = self.entry_admin_user.get()
                    admin_password = self.entry_admin_password.get()
                    master_password = self.entry_master_password.get()

                    if account_creation(admin_user, admin_password, admin_name, admin_email, master_password):
                        messagebox.showinfo("Notification", "Successfully added " + admin_name)

                        self.entry_admin_name.delete(0, tk.END)
                        self.entry_admin_email.delete(0, tk.END)
                        self.entry_admin_user.delete(0, tk.END)
                        self.entry_admin_password.delete(0, tk.END)
                        self.entry_master_password.delete(0, tk.END)
                except Exception as e:
                    messagebox.showerror("Error!", f"Error: {e}")

            self.button_new_admin = tk.Button(self.frame_new_admin, text="Create Account", bg='#b80000', fg='#ffffff',
                                              relief='flat', command=submit_new_admin)
            self.button_new_admin.grid(row=5, column=0, sticky='ew')



        new_admin_ui()

if __name__ == "__main__":
    app = App()
    app.mainloop()
