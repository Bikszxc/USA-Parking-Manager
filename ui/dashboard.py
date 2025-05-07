import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox, ttk
from ttkwidgets.autocomplete import AutocompleteCombobox
from PIL import Image, ImageTk, ImageSequence
from logic.auth import account_login, account_creation
from logic.models import new_car_owner, get_car_owners, get_owner_vehicles, record_found, get_owner, get_vehicle_type, park_vehicle, get_parking_slots
import re


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
        self.entry_username.bind("<Return>", self.login)

        self.underline_username = tk.Canvas(frame_login, bg="white", height=0, highlightthickness=0)
        self.underline_username.grid(row=3, column=0, sticky="nsew")

        entry_spacer = tk.Canvas(frame_login, bg="#b80000", height=20, bd=0, highlightthickness=0)
        entry_spacer.grid(row=4, column=0, sticky="ew")

    def _create_password_entry(self, frame_login):
        self.entry_password = tk.Entry(frame_login, font=self.master.login_font, bg="#b80000", fg="white", relief="flat", insertbackground="white")
        self.entry_password.grid(row=5, column=0, sticky="we")
        self.entry_password.insert(0, "Password")
        self._bind_entry_focus_events(self.entry_password, "Password")
        self.entry_password.bind("<Return>", self.login)

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

        def close_app():
            exit()

        btn_close = tk.Button(frame_send_buttons, text="Close", bg="#cccccc", fg="black", relief="flat", font=self.master.subheader_font, width=8, command=close_app)
        btn_close.grid(row=0, column=0, sticky="e")

        frame_send_buttons.grid_columnconfigure(1, weight=0)

        btn_spacer = tk.Canvas(frame_send_buttons, bg="#b80000", width=5, height=0, bd=0, highlightthickness=0)
        btn_spacer.grid(row=0, column=1, sticky="ew")

    def _bind_entry_focus_events(self, entry, text):
        entry.bind("<FocusIn>", lambda _: self.on_focus(entry, text))
        entry.bind("<FocusOut>", lambda _: self.on_unfocus(entry, text))

    def login(self, event=None):
        self.frame_error.place_forget()
        username = self.entry_username.get()
        password = self.entry_password.get()

        if account_login(username, password):
            self.master.show_frame(LoadingScreen)
            self.master.title("USA Parking System | Logged in as: " + username)
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
        self.page_home = tk.Frame(self, bg='#e6e6e6', padx=10, pady=10)
        self.page_home.grid(row=0, column=1, sticky='nsew')

        def park_vehicle_ui():

            def check_results(event=None):
                dropdown_vehicle.delete(0, tk.END)
                entry_contact_number.delete(0, tk.END)

                owner_name = dropdown_owner.get()

                if record_found(owner_name):
                    owner_details = get_owner(owner_name)

                    dropdown_type.set(owner_details[2])
                    entry_contact_number.insert(0, owner_details[3])

                    update_vehicles()

            def update_owners(event=None):
                owner_name = dropdown_owner.get()

                for name in owners:
                    if owner_name.lower() == name.lower():
                        dropdown_owner.set(name)
                        check_results()

            def update_vehicles(event=None):
                selected_owner = dropdown_owner.get()
                vehicles = get_owner_vehicles(selected_owner)

                if vehicles:
                    vehicles = sorted([vehicle[2] for vehicle in vehicles])
                    dropdown_vehicle.config(values=vehicles, state="normal")
                else:
                    dropdown_vehicle.set('')
                    dropdown_vehicle.config(state="disabled")

            def update_vehicle_type(event=None):
                plate_number = dropdown_vehicle.get()
                entry_vehicle_type.delete(0, tk.END)

                entry_vehicle_type.insert(0, get_vehicle_type(plate_number))

            def submit_park_vehicle(event=None):
                try:
                    slot_number = dropdown_park_slot.get()
                    vehicle_type = entry_vehicle_type.get()
                    owner_name = dropdown_owner.get()
                    plate_number = dropdown_vehicle.get()
                    status_type = dropdown_type.get()
                    contact_number = entry_contact_number.get()

                    if not all([slot_number, vehicle_type, owner_name, plate_number, status_type, contact_number]):
                        raise Exception(messagebox.showerror("Error", "Please enter all required fields!"))

                    if not slot_number in park_slots:
                        raise Exception(messagebox.showerror("Error", "Slot number must be in parking slots!"))

                    if park_vehicle(slot_number, vehicle_type, owner_name, plate_number, status_type, contact_number):
                        messagebox.showinfo("Success", f"{vehicle_type} | {plate_number}\nParked Successfully!")

                        for e in (dropdown_owner, dropdown_vehicle, entry_vehicle_type, entry_contact_number, dropdown_type, dropdown_park_slot):
                            e.delete(0, tk.END)

                except Exception as e:
                    print(f"Error: {e}")

            frame_park_vehicle = tk.Frame(self.page_home, bg='#b80000', padx=10, pady=10)
            frame_park_vehicle.grid(row=0, column=0, sticky='nsew')

            label_park_title = tk.Label(frame_park_vehicle, text="Park Vehicle", font=self.master.header_font, bg='#b80000', fg='#ffffff')
            label_park_title.grid(row=0, column=0, sticky='w')

            tk.Frame(frame_park_vehicle, bg='#b80000', height=15).grid(row=1, column=0, sticky='nsew')

            combobox_style = ttk.Style()
            combobox_style.theme_use('default')
            combobox_style.configure("CustomCombobox.TCombobox", fieldbackground="#b80000", foreground="#ffffff", relief="flat", borderwidth=0)
            combobox_style.map("CustomCombobox.TCombobox", selectbackground=[('!disabled', "#ffcc00")])

            owners = sorted([name[1] for name in get_car_owners()])

            label_combo_owner = tk.Label(frame_park_vehicle, text="Owner Name", bg='#b80000', fg="white", font=self.master.subheader_font)
            label_combo_owner.grid(row=2, column=0, sticky='w')

            dropdown_owner = ttk.Combobox(frame_park_vehicle, values=owners, state="normal", style="CustomCombobox.TCombobox")
            dropdown_owner.grid(row=3, column=0, sticky='nsew')
            dropdown_owner.bind("<Return>", update_owners)
            dropdown_owner.bind("<<ComboboxSelected>>", check_results)

            tk.Canvas(frame_park_vehicle, bg="white", height=0, highlightthickness=0).grid(row=4, column=0, sticky='nsew')

            tk.Frame(frame_park_vehicle, bg='#b80000', width=100).grid(row=1, column=1, sticky='nsew')

            label_plate_number = tk.Label(frame_park_vehicle, text="Plate Number", bg='#b80000', fg='white', font=self.master.subheader_font)
            label_plate_number.grid(row=2, column=2, sticky='w')

            dropdown_vehicle = ttk.Combobox(frame_park_vehicle, state='normal', style="CustomCombobox.TCombobox")
            dropdown_vehicle.grid(row=3, column=2, sticky='nsew')
            dropdown_vehicle.bind("<<ComboboxSelected>>", update_vehicle_type)

            tk.Canvas(frame_park_vehicle, bg="white", height=0, highlightthickness=0).grid(row=4, column=2, sticky='nsew')
            tk.Frame(frame_park_vehicle, bg='#b80000', height=15).grid(row=5, column=0, sticky='nsew')

            label_vehicle_type = tk.Label(frame_park_vehicle, text="Vehicle Type", bg='#b80000', fg='white', font=self.master.subheader_font)
            label_vehicle_type.grid(row=6, column=0, sticky='w')

            entry_vehicle_type = tk.Entry(frame_park_vehicle, bg='#b80000', fg="white", relief="flat")
            entry_vehicle_type.grid(row=7, column=0, sticky='nsew')

            tk.Canvas(frame_park_vehicle, bg="white", height=0, highlightthickness=0).grid(row=8, column=0, sticky='nsew')

            label_type = tk.Label(frame_park_vehicle, text="Type", bg='#b80000', fg="white", font=self.master.subheader_font)
            label_type.grid(row=6, column=2, sticky='w')

            dropdown_type = ttk.Combobox(frame_park_vehicle, values=["Student", "Faculty", "Staff", "Visitor"], style="CustomCombobox.TCombobox")
            dropdown_type.grid(row=7, column=2, sticky='nsew')

            tk.Canvas(frame_park_vehicle, bg="white", height=0, highlightthickness=0).grid(row=8, column=2,sticky='nsew')
            tk.Frame(frame_park_vehicle, bg='#b80000', height=15).grid(row=9, column=0, sticky='nsew')

            label_contact_number = tk.Label(frame_park_vehicle, text="Contact Number", bg='#b80000', fg="white", font=self.master.subheader_font)
            label_contact_number.grid(row=10, column=0, sticky='w')

            entry_contact_number = tk.Entry(frame_park_vehicle, bg='#b80000', fg="white", relief="flat")
            entry_contact_number.grid(row=11, column=0, sticky='nsew')

            tk.Canvas(frame_park_vehicle, bg="white", height=0, highlightthickness=0).grid(row=12, column=0, sticky='nsew')

            label_park_slot = tk.Label(frame_park_vehicle, text="Park Slot", bg='#b80000', fg="white", font=self.master.subheader_font)
            label_park_slot.grid(row=10, column=2, sticky='w')

            park_slots = [slot[0] for slot in get_parking_slots()]

            dropdown_park_slot = ttk.Combobox(frame_park_vehicle, values=park_slots, style="CustomCombobox.TCombobox")
            dropdown_park_slot.grid(row=11, column=2, sticky='nsew')
            dropdown_park_slot.bind("<Return>", submit_park_vehicle)

            tk.Canvas(frame_park_vehicle, bg="white", height=0, highlightthickness=0).grid(row=12, column=2, sticky='nsew')

            tk.Frame(frame_park_vehicle, bg='#b80000', height=25).grid(row=13, column=0, sticky='nsew')

            button_park_vehicle = tk.Button(frame_park_vehicle, text="Park Vehicle", bg='#ffcc00', fg='black', relief="flat", command=submit_park_vehicle, font=self.master.subheader_font)
            button_park_vehicle.grid(row=14, column=0, columnspan=4, sticky='nsew')

        park_vehicle_ui()


    def reservations_page(self):
        self.page_home.grid_forget()

        self.page_reservations = tk.Frame(self, bg='#e6e6e6')
        self.page_reservations.grid(row=0, column=1, sticky='nsew')

        self.label_placeholder = tk.Label(self.page_reservations, text="RESERVATIONS PAGE", bg='#e6e6e6', font=self.master.header_font)
        self.label_placeholder.grid(row=0, column=0, sticky='nsew')

    def accounts_page(self):
        self.page_accounts = tk.Frame(self, bg='#e6e6e6')
        self.page_accounts.grid(row=0, column=1, sticky='nsew')

        # Function to load owner data
        def load_owner_data():
            for row in tree.get_children():
                tree.delete(row)
            owners = get_car_owners()  # Assume this function gets the list of owners
            for owner in owners:
                tree.insert("", tk.END, values=owner)

        def test_tree_ui():
            global tree

            # Function to sort the data in the Treeview based on the clicked column
            def sort_treeview(column, reverse=False):
                """Sort the Treeview data based on the clicked column."""
                rows = [(tree.item(item)["values"], item) for item in tree.get_children()]
                rows.sort(key=lambda x: x[0][column], reverse=reverse)

                # Rearranging the rows in the Treeview based on the sorted data
                for index, (_, item) in enumerate(rows):
                    tree.move(item, '', index)

                return not reverse

            # Function to handle column click and toggle sorting
            def on_column_click(column):
                nonlocal sort_reverse
                sort_reverse = sort_treeview(column, sort_reverse)

            style = ttk.Style(self.page_accounts)
            style.theme_use("alt")
            style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'), background="#b80000",
                            foreground="white", relief="flat")

            # Frame for Treeview
            frame_tree = tk.Frame(self.page_accounts, bg='#e6e6e6')
            frame_tree.grid(row=1, column=0, sticky='nsew')

            # Create Treeview
            tree = ttk.Treeview(frame_tree, columns=("ID", "Owner Name", "Email Address", "Type", "Contact Number"),
                                show="headings")
            tree.heading("#1", text="ID", anchor="w", command=lambda: on_column_click(0))
            tree.heading("#2", text="Owner Name", anchor="w", command=lambda: on_column_click(1))
            tree.heading("#3", text="Email Address", anchor="w", command=lambda: on_column_click(2))
            tree.heading("#4", text="Type", anchor="w", command=lambda: on_column_click(3))
            tree.heading("#5", text="Contact Number", anchor="w", command=lambda: on_column_click(4))

            # Set column widths
            tree.column("#1", width=50, stretch=tk.NO)
            tree.column("#2", width=150)
            tree.column("#3", width=200)
            tree.column("#4", width=100)
            tree.column("#5", width=120)

            # Layout the Treeview
            tree.grid(row=0, column=0, sticky='nsew')

            # Scrollbar setup
            scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.grid(row=0, column=1, sticky='nsew')

            # Refresh Button
            button_refresh = tk.Button(frame_tree, text="Refresh", command=load_owner_data)
            button_refresh.grid(row=1, column=0, sticky='nsew')

            # Initial data load
            load_owner_data()

            # Sorting order flag (True for descending, False for ascending)
            sort_reverse = False

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

        def new_car_owner_ui():
            self.frame_owner = tk.Frame(self.page_accounts, bg='#e6e6e6', relief='raised', width=300)
            self.frame_owner.grid(row=0, column=1)

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

                    if not all([owner_name, owner_type, email_address, contact_number]):
                        raise Exception(messagebox.showerror("Error", "Please enter all fields"))

                    if not is_valid_email(email_address):
                        raise Exception(messagebox.showerror("Error", "Invalid email address!"))

                    if new_car_owner(owner_name, email_address, owner_type, contact_number, refresh_callback=load_owner_data):
                        messagebox.showinfo("Info","Successfully added" + owner_name)

                        self.entry_owner_name.delete(0, tk.END)
                        self.entry_owner_type.delete(0, tk.END)
                        self.entry_owner_email.delete(0, tk.END)
                        self.entry_owner_number.delete(0, tk.END)
                except Exception as e:
                    print(f"Error: {e}")

            self.add_button = tk.Button(self.frame_owner, text="Submit", bg='#b80000', fg='#ffffff', relief='flat', command=submit_owner)
            self.add_button.grid(row=4, column=1, sticky='ew')

        new_car_owner_ui()
        new_admin_ui()
        test_tree_ui()

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

if __name__ == "__main__":
    app = App()
    app.mainloop()