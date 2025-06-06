import re
import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox, ttk
from datetime import datetime, timezone, timedelta

from PIL import Image, ImageTk, ImageSequence

from logic.auth import account_login, account_creation, account_deletion, get_all_admins, get_admin_details, \
    account_edit
from logic.models import new_car_owner, get_car_owners, get_owner_vehicles, record_found, get_owner, get_vehicle_type, \
    park_vehicle, get_parking_slots, unpark_vehicle, get_parkslot_info, assign_vehicle, \
    check_plate_number, get_vehicles, get_vehicle_owner, get_reservations, get_res_id_details, \
    accept_reservation, reject_reservation, update_reservation_late_status, cancel_accepted_reservation, \
    unassign_vehicle, delete_car_owner, edit_car_owner, delete_reservation


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("USA Parking Manager")
        self.geometry("1280x720")
        self.configure(bg="#e6e6e6")
        self.iconbitmap("ui/assets/usa.ico")
        self.admin_name = None

        self.frames = {}
        self._initialize_fonts()
        self._initialize_frames()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.show_frame(LoginScreen)

    def _initialize_fonts(self):
        font_path = "ui/fonts/Helvetica.ttf"
        self.header_font = tkFont.Font(family=font_path, size=22, weight="bold")
        self.subheader_font = tkFont.Font(family=font_path, size=10, weight="bold")
        self.login_font = tkFont.Font(family=font_path, size=10)

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
        super().__init__(master, bg="#f4c2c2")
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
        label_error = tk.Label(self.frame_error, text="Incorrect Username or Password", bg="#ff0000", fg="#ffffff",
                               font=("Arial", 12))
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
        tk.Label(frame_login, text="Sign In", font=self.master.header_font, bg="#b80000", fg="white").grid(row=0,
                                                                                                           column=0,
                                                                                                           sticky="w")

    def _add_spacer(self, frame_login):
        label_spacer = tk.Canvas(frame_login, bg="#b80000", height=20, bd=0, highlightthickness=0)
        label_spacer.grid(row=1, column=0, sticky="ew")

    def _create_username_entry(self, frame_login):
        self.entry_username = tk.Entry(frame_login, font=self.master.login_font, bg="#b80000", fg="white",
                                       relief="flat", insertbackground="white")
        self.entry_username.grid(row=2, column=0, sticky="we")
        self.entry_username.insert(0, "Username")
        self._bind_entry_focus_events(self.entry_username, "Username")
        self.entry_username.bind("<Return>", self.login)

        self.underline_username = tk.Canvas(frame_login, bg="white", height=0, highlightthickness=0)
        self.underline_username.grid(row=3, column=0, sticky="nsew")

        entry_spacer = tk.Canvas(frame_login, bg="#b80000", height=20, bd=0, highlightthickness=0)
        entry_spacer.grid(row=4, column=0, sticky="ew")

    def _create_password_entry(self, frame_login):
        self.entry_password = tk.Entry(frame_login, font=self.master.login_font, bg="#b80000", fg="white",
                                       relief="flat", insertbackground="white")
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

        btn_login = tk.Button(frame_send_buttons, text="Login", bg="#ffcc00", fg="white", relief="flat",
                              font=self.master.subheader_font, width=8, command=self.login)
        btn_login.grid(row=0, column=2, sticky="e")

        def close_app():
            exit()

        btn_close = tk.Button(frame_send_buttons, text="Close", bg="#cccccc", fg="black", relief="flat",
                              font=self.master.subheader_font, width=8, command=close_app)
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
            self.master.admin_name = username
            self.master.show_frame(LoadingScreen)
            self.master.title("USA Parking System | Logged in as: " + username)
            self.after(2000, lambda: self.master.show_frame(DashboardScreen))
        else:
            self.after(1000, lambda: self.frame_error.place(relx=0.5, rely=0.2, anchor="center"))

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
        self.time()
        self._initialize_fonts()
        self.admin_name = self.master.admin_name

        self.frames = {}

        self._initialize_pages()

        self.show_frame(HomePage)

    def _initialize_fonts(self):
        font_path = "ui/fonts/Helvetica.ttf"
        self.header_font = tkFont.Font(family=font_path, size=22, weight="bold")
        self.subheader_font = tkFont.Font(family=font_path, size=10, weight="bold")
        self.login_font = tkFont.Font(family=font_path, size=10)

    def _initialize_pages(self):
        for P in (HomePage, ReservationsPage, VehiclesPage, AccountsPage):
            frame = P(self)
            self.frames[P] = frame
            frame.grid(row=0, column=1, sticky="nsew")

    def show_frame(self, container, *args, **kwargs):
        frame = self.frames[container]
        frame.refresh_data()
        frame.tkraise()
        frame.event_generate("<<ShowFrame>>")

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
            "Home": lambda: self.show_frame(HomePage),
            "Reservations": lambda: self.show_frame(ReservationsPage),
            "Vehicles": lambda: self.show_frame(VehiclesPage),
            "Accounts": lambda: self.show_frame(AccountsPage),
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

            if page is None:
                button.config(state="disabled")

            button.grid(row=i, column=0, sticky="ew", padx=10, pady=5)

    def time(self):
        clock = datetime.now().strftime("%B %d, %Y | %H:%M:%S")
        self.label_time.config(text=clock)
        self.label_time.after(1000, self.time)

    def _add_footer(self, frame_sidebar):
        frame_footer = tk.Frame(frame_sidebar, bg='#ffcc00')
        frame_footer.grid(row=10, column=0, sticky='ew')
        self.label_time = tk.Label(frame_footer, bg='#ffcc00', text="Clock Unavailable!", padx=10, pady=10,
                                   anchor="center")
        self.label_time.pack()

class HomePage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#e6e6e6", padx=10, pady=10)

        self._initialize_inner_frames()

        self.frames = {
            "Park Vehicle": self.frame_park_vehicle,
            "Vehicle Info": self.frame_vehicle_info,
            "Parking Slots": self.frame_park_slots
        }

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.previous_slot_status = {}
        self.park_slot_buttons = {}

        self._initialize_frame_titles()
        self._initialize_grid()
        self._initialize_styles()
        self._create_reservation_info_labels()
        self._create_vehicle_info_labels()
        self._create_park_vehicle_labels()
        self._create_park_vehicle_entries()
        self._park_spacer_and_underline()
        self._create_binds()

        self.fetch_database(None)

        self._create_slot_buttons()
        self._create_submit_buttons()

    def refresh_data(self):
        self.fetch_database(None)
        self.start_timer_updates()

    def start_timer_updates(self):
        self.update_timers_only()
        self.after(1000, self.start_timer_updates)

    def _initialize_inner_frames(self):
        self.frame_park_vehicle = tk.Frame(self, bg='#b80000', padx=10, pady=10)
        self.frame_vehicle_info = tk.Frame(self, bg='#b80000', padx=10, pady=10)
        self.frame_park_slots = tk.Frame(self, bg='#b80000', padx=10, pady=10)
        self.frame_reservation_info = tk.Frame(self.frame_park_slots, bg='#b80000')

    def _initialize_frame_titles(self):
        for (title, f) in self.frames.items():
            if title == "Parking Slots":
                tk.Frame(f, bg='#b80000', height=60).grid(row=0, column=0, sticky='w')
                tk.Label(f, text=title, bg='#b80000', fg="white",
                         font=self.master.header_font).place(x=0, y=5)
            else:
                tk.Frame(f, bg='#b80000', height=50).grid(row=0, column=0, sticky='w')
                tk.Label(f, text=title, bg='#b80000', fg="white",
                         font=self.master.header_font).place(x=0, y=0)

    def _initialize_grid(self):
        self.frames["Park Vehicle"].grid(row=0, column=0, sticky='new')
        self.frames["Vehicle Info"].grid(row=0, column=2, sticky='new')
        self.frames["Parking Slots"].grid(row=2, column=0, columnspan=3, sticky='nsew')
        self.frame_reservation_info.grid(row=0, column=2, columnspan=3, sticky='e')

    def _initialize_styles(self):
        combobox_style = ttk.Style()
        combobox_style.theme_use('default')
        combobox_style.configure("CustomCombobox.TCombobox", fieldbackground="#b80000", foreground="#ffffff",
                                 relief="flat", borderwidth=0, highlightcolor="#b80000")
        combobox_style.map("CustomCombobox.TCombobox", selectbackground=[('!disabled', "#e6e6e6")], selectforeground=[('!disabled', "black")])

    def _create_reservation_info_labels(self):
        self.r_info = {
            "Reservation Name": tk.StringVar(),
            "Reservation Date": tk.StringVar(),
            "Reservation Time": tk.StringVar(),
        }

        for i, (label_text, var) in enumerate(self.r_info.items()):

            tk.Label(self.frame_reservation_info, text=label_text, bg='#b80000', fg="white",
                     font=self.master.subheader_font, padx=10).grid(row=0, column=i, sticky='se')
            tk.Label(self.frame_reservation_info, textvariable=var, bg='#b80000',fg="white",
                     font=self.master.login_font, padx=10).grid(row=1, column=i, sticky='ne')


        self.btn_reservation_view_more = tk.Button(self.frame_reservation_info, bg='#ffcc00', fg="black",
                                              text="View More Details", font=self.master.subheader_font, relief="flat",
                                              padx=5)
        self.btn_reservation_view_more.grid(row=0, column=8, rowspan=2, sticky='nsew')
        self.btn_reservation_view_more.grid_remove()

        for var in self.r_info.values():
            var.set("None")

        self.frame_park_slots.columnconfigure(2, weight=1)

    def _create_vehicle_info_labels(self):
        self.v_info = {
            "Slot Number": tk.StringVar(),
            "Plate Number": tk.StringVar(),
            "Vehicle Type": tk.StringVar(),
            "Owner Name": tk.StringVar(),
            "Contact Number": tk.StringVar()
        }

        for i, (label_text, var) in enumerate(self.v_info.items(), start=1):
            tk.Label(self.frame_vehicle_info, text=label_text, bg='#b80000', fg="white",
                     font=self.master.subheader_font, pady=5).grid(row=i, column=0, sticky='w')
            tk.Label(self.frame_vehicle_info, textvariable=var, bg='#b80000', fg="white",
                     font=self.master.login_font, pady=5, width=20, anchor='e').grid(row=i, column=2, sticky='e')

            if label_text == "Vehicle Type":
                self.v_info["Vehicle Type"].set("Select a slot")

    def _create_slot_buttons(self):
        j = 0
        i = 1

        for slot in self.park_slots:
            slot_number = slot[1]
            slot_status = slot[2]
            has_reservation = get_res_id_details(slot_number)

            upcoming_reservation = False  # Initialize as False

            if has_reservation:
                res_date = datetime.strptime(has_reservation[7], "%m-%d-%Y")
                res_time = datetime.strptime(has_reservation[8], "%H:%M")

                # Get current date and time
                current_date = datetime.now().date()
                current_time = datetime.now().time()

                # Check if reservation is today
                if res_date.date() == current_date:
                    # Fix: Use .date() and .time() to extract the components properly
                    reservation_datetime = datetime.combine(res_date.date(), res_time.time())
                    current_datetime = datetime.now()

                    # Check if current time is within 1 hour before reservation
                    time_diff = reservation_datetime - current_datetime

                    # If time difference is between 0 and 1 hour (3600 seconds)
                    if 0 <= time_diff.total_seconds() <= 3600:
                        upcoming_reservation = True

                print(f"Slot {slot_number}: upcoming_reservation = {upcoming_reservation}")

            fgcolor = "white"

            if upcoming_reservation and slot_status == 1:
                bgcolor = "blue"
            elif upcoming_reservation and slot_status == 0:
                bgcolor = "yellow"
                fgcolor = "black"
            elif not upcoming_reservation and slot_status == 1:
                bgcolor = "gray"
            else:
                bgcolor = "green"

            timer_text = None
            if has_reservation:
                timer_text = self.reservation_timer(has_reservation[7], has_reservation[8])

            if timer_text:
                if slot_status == 0:
                    pkg_text = f"{slot_number}\nAvailable\nReservation in: {timer_text}"
                else:
                    pkg_text = f"{slot_number}\n{slot[5]}\n{slot[3]}\nReservation in: {timer_text}"
            else:
                pkg_text = f"{slot_number}\nAvailable\n" if slot_status == 0 else f"{slot_number}\n{slot[5]}\n{slot[3]}"

            button = tk.Button(self.frame_park_slots, text=pkg_text, bg=bgcolor, fg=fgcolor, width=20,
                               command=lambda x=slot[1]: self.get_slot_info(x),
                               anchor="center", font=("Helvetica", 10), relief="ridge")
            button.grid(row=i, column=j, sticky='nsew')

            self.park_slot_buttons[slot[1]] = button

            j += 1

            if j == 5:
                j = 0
                i += 1

    def _create_park_vehicle_labels(self):
        left_labels = ["Owner Name", "Vehicle Type", "Contact Number"]
        right_labels = ["Plate Number", "Owner Type", "Park Slot"]

        i = 1

        for label in left_labels:

            tk.Label(self.frame_park_vehicle, text=label, bg='#b80000', fg='white',
                     font=self.master.subheader_font).grid(row=i, column=0, sticky='w')
            i += 4

        i = 1

        for label in right_labels:
            tk.Label(self.frame_park_vehicle, text=label, bg='#b80000', fg='white',
                     font=self.master.subheader_font).grid(row=i, column=2, sticky='w')

            i += 4


    def _create_park_vehicle_entries(self):
        self.dropdown_owner = ttk.Combobox(self.frame_park_vehicle, values=sorted([name[1] for name in get_car_owners()]), state="normal",
                                      style="CustomCombobox.TCombobox")
        self.dropdown_owner.grid(row=3, column=0, sticky='nsew')

        self.dropdown_plate_number = ttk.Combobox(self.frame_park_vehicle, state='normal', style="CustomCombobox.TCombobox")
        self.dropdown_plate_number.grid(row=3, column=2, sticky='nsew')

        self.entry_vehicle_type = tk.Entry(self.frame_park_vehicle, bg='#b80000', fg="white", relief="flat")
        self.entry_vehicle_type.grid(row=7, column=0, sticky='nsew')

        self.dropdown_type = ttk.Combobox(self.frame_park_vehicle, values=("Student", "Faculty", "Staff", "Visitor"),
                                         style="CustomCombobox.TCombobox")
        self.dropdown_type.grid(row=7, column=2, sticky='nsew')

        self.entry_contact_number = tk.Entry(self.frame_park_vehicle, bg='#b80000', fg="white", relief="flat")
        self.entry_contact_number.grid(row=11, column=0, sticky='nsew')

        self.dropdown_park_slot = ttk.Combobox(self.frame_park_vehicle, values=("park_slots", "temporary"), style="CustomCombobox.TCombobox")
        self.dropdown_park_slot.grid(row=11, column=2, sticky='nsew')

    def _create_submit_buttons(self):
        self.park_button = tk.Button(self.frame_park_vehicle, text="Park Vehicle", bg='#ffcc00', fg='black',
                  relief="flat", command=self.submit_park, font=self.master.subheader_font)
        self.park_button.grid(row=14, column=0, columnspan=3, sticky='nsew')

        self.unpark_button = tk.Button(self.frame_vehicle_info, text="Unpark Vehicle", bg='#ffcc00', fg='black',
                                     relief="flat", command=self.submit_unpark, font=self.master.subheader_font)
        self.unpark_button.grid(row=7, column=0, columnspan=3, sticky='nsew')

    def _create_binds(self):
        self.bind("<<ShowFrame>>", self.fetch_database)
        self.dropdown_owner.bind("<<ComboboxSelected>>", self.filter_owner_vehicles)
        self.dropdown_owner.bind("<Return>", self.filter_owner_vehicles)
        self.dropdown_owner.bind("<<ComboboxSelected>>", self.auto_fill_entries, add='+')
        self.dropdown_owner.bind("<Return>", self.auto_fill_entries, add='+')
        self.dropdown_plate_number.bind("<<ComboboxSelected>>", self.auto_fill_entries)
        self.dropdown_plate_number.bind("<Return>", self.auto_fill_entries)

    def _park_spacer_and_underline(self):

        i = 3

        while i <= 12:
            tk.Canvas(self.frame_park_vehicle, bg="white", height=0,
                      width=200, highlightthickness=0).grid(row=i, column=0,sticky='sew')
            tk.Canvas(self.frame_park_vehicle, bg="white", height=0,
                      width=200, highlightthickness=0).grid(row=i, column=2, sticky='sew')

            tk.Frame(self.frame_park_vehicle, bg='#b80000', height=15).grid(row=i+1, column=2, sticky='nsew')

            i += 4

        tk.Frame(self.frame_park_vehicle, bg='#b80000', width=100).grid(row=1, column=1, sticky='ew')
        tk.Frame(self.frame_park_vehicle, bg='#b80000', height=10).grid(row=13, column=0, sticky='nsew')

        self.frame_park_vehicle.columnconfigure(0, weight=2)
        self.frame_park_vehicle.columnconfigure(2, weight=2)

        tk.Frame(self.frame_vehicle_info, bg='#b80000', width=15).grid(row=3, column=1, sticky='nsew')
        tk.Frame(self.frame_vehicle_info, bg='#b80000', height=29).grid(row=6, column=1, sticky='nsew')

        self.frame_vehicle_info.columnconfigure(2, weight=2)

        for i in range(0, 5):
            self.frame_park_slots.columnconfigure(i, weight=2)

        for i in range(1, 6):
            self.frame_park_slots.rowconfigure(i, weight=1)

        # tk.Frame(self, bg='#e6e6e6', width=15).grid(row=0, column=1, sticky='n')
        tk.Frame(self, bg='#e6e6e6', height=15).grid(row=1, column=0, sticky='ns')

        self.grid_columnconfigure(0, weight=3)
        self.grid_rowconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=2)
        self.grid_rowconfigure(2, weight=10)

    def update_timers_only(self):
        """Update only the timer displays without refreshing database"""
        try:
            timer_expired = False
            reservation_cancelled = False

            for slot in self.park_slots:
                slot_number = slot[1]
                slot_status = slot[2]

                prev_status = self.previous_slot_status.get(slot_number)
                has_reservation = get_res_id_details(slot_number)
                current_status = (slot_status, has_reservation)

                timer_text = None
                just_expired = False
                grace_timer_text = None

                if has_reservation:
                    # Check if reservation is late and get appropriate timer
                    if has_reservation[11]:  # is_late is at index 11
                        grace_result = self.grace_period_timer(has_reservation[12])  # grace_period_until at index 12
                        if grace_result:
                            grace_timer_text, grace_expired = grace_result
                            if grace_expired:
                                # Grace period expired - cancel the reservation
                                print(
                                    f"Grace period expired for reservation {has_reservation[0]} in slot {slot_number}")
                                if cancel_accepted_reservation(has_reservation[0]):
                                    print(f"Reservation {has_reservation[0]} cancelled successfully")
                                    reservation_cancelled = True
                                else:
                                    print(f"Failed to cancel reservation {has_reservation[0]}")
                                timer_expired = True
                    else:
                        timer_result = self.reservation_timer(has_reservation[7], has_reservation[8])
                        if timer_result:
                            timer_text, just_expired = timer_result
                            if just_expired:
                                # Set is_late to True in database
                                self.set_reservation_late(has_reservation[0])  # Pass reservation ID
                                timer_expired = True

                should_update = (prev_status != current_status) or timer_text or grace_timer_text

                if should_update:
                    if grace_timer_text:
                        if slot_status == 0:
                            pkg_text = f"{slot_number}\nAvailable\nGrace period: {grace_timer_text}"
                        else:
                            pkg_text = f"{slot_number}\n{slot[5]}\n{slot[3]}\nGrace period: {grace_timer_text}"
                    elif timer_text:
                        if slot_status == 0:
                            pkg_text = f"{slot_number}\nAvailable\nReservation in: {timer_text}"
                        else:
                            pkg_text = f"{slot_number}\n{slot[5]}\n{slot[3]}\nReservation in: {timer_text}"
                    else:
                        pkg_text = f"{slot_number}\nAvailable\n" if slot_status == 0 else f"{slot_number}\n{slot[5]}\n{slot[3]}"

                    if slot_number in self.park_slot_buttons:
                        self.park_slot_buttons[slot_number].config(text=pkg_text)

            if timer_expired:
                if reservation_cancelled:
                    print("Reservation cancelled due to grace period expiration - refreshing database")
                else:
                    print("Timer expired - refreshing database")
                self.fetch_database(None)

        except Exception as e:
            print(f"Timer update error!", e)

    def reservation_timer(self, reservation_date, reservation_time):
        try:
            # GMT+8 timezone offset
            ph_offset = timezone(timedelta(hours=8))
            ph_time = datetime.now(ph_offset)

            # Combine date and time
            reservation_datetime_str = f"{reservation_date} {reservation_time}"
            res_time = datetime.strptime(reservation_datetime_str, "%m-%d-%Y %H:%M")

            ph_time = ph_time.replace(tzinfo=None)
            fake_ph_time = ph_time + timedelta(hours=2)

            # Check if reservation is today
            if res_time.date() != ph_time.date():
                return None

            # Calculate time difference
            time_diff = res_time - ph_time

            # Check if reservation is within 1 hour and in the future
            if time_diff.total_seconds() <= 0 or time_diff.total_seconds() > 3600:
                return None

            # Format the countdown timer
            total_seconds = int(time_diff.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60

            timer_text = f"{minutes:02d}:{seconds:02d}"
            just_expired = total_seconds <= 1

            return timer_text, just_expired

        except Exception as e:
            print(f"Timer calculation error: {e}")
            return None

    def grace_period_timer(self, grace_period_until_str):
        """Handle the 15-minute grace period using the stored end time"""
        try:
            if not grace_period_until_str:
                return None

            # Parse the grace period end time
            grace_end_time = datetime.strptime(grace_period_until_str, "%m-%d-%Y %H:%M")
            current_time = datetime.now()

            # Calculate remaining time
            time_diff = grace_end_time - current_time

            if time_diff.total_seconds() <= 0:
                return None, True  # Grace period expired

            # Calculate remaining time
            total_seconds = int(time_diff.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60

            timer_text = f"{minutes:02d}:{seconds:02d}"
            grace_expired = total_seconds <= 1

            return timer_text, grace_expired

        except Exception as e:
            print(f"Grace period timer calculation error: {e}")
            return None

    def set_reservation_late(self, reservation_id):
        """Set the is_late flag to True and calculate grace period end time"""
        try:
            # Calculate grace period end time (15 minutes from now)
            grace_end_time = datetime.now() + timedelta(minutes=16)
            grace_end_str = grace_end_time.strftime("%m-%d-%Y %H:%M")

            # Update database with is_late=True and grace_period_until
            update_reservation_late_status(reservation_id, grace_end_str)
            print(f"Reservation {reservation_id} marked as late with grace period until {grace_end_str}")
        except Exception as e:
            print(f"Error setting reservation late status: {e}")

    def fetch_database(self, event):
        try:
            self.car_owners = sorted([name[1] for name in get_car_owners()])
            self.vehicles = sorted([plate[2] for plate in get_vehicles()])
            self.park_slots = sorted([slot for slot in get_parking_slots()])
            self.slot_numbers = [slot[1] for slot in self.park_slots]

            self.dropdown_owner.config(values=self.car_owners)
            self.dropdown_plate_number.config(values=self.vehicles)
            self.dropdown_park_slot.config(values=self.slot_numbers)

            timer_expired = False

            for slot in self.park_slots:
                slot_number = slot[1]
                slot_status = slot[2]
                print(slot)

                prev_status = (self.previous_slot_status.get(slot_number), get_res_id_details(slot_number))
                has_reservation = get_res_id_details(slot_number)
                current_status = (slot_status, has_reservation)

                timer_text = None
                grace_timer_text = None
                just_expired = False

                upcoming_reservation = False

                if has_reservation:
                    res_date = datetime.strptime(has_reservation[7], "%m-%d-%Y")
                    res_time = datetime.strptime(has_reservation[8], "%H:%M")

                    current_date = datetime.now().date()
                    current_time = datetime.now().time()

                    if res_date.date() == current_date:
                        # Fix: Use reservation time, not current time
                        reservation_datetime = datetime.combine(res_date.date(), res_time.time())
                        current_datetime = datetime.now()

                        time_diff = reservation_datetime - current_datetime

                        if 0 <= time_diff.total_seconds() <= 3600:
                            upcoming_reservation = True

                fgcolor = "white"
                bgcolor = "green"  # Default color

                # Handle colors for different states including grace period
                if has_reservation and has_reservation[11]:  # is_late is True (index 11)
                    bgcolor = "orange"  # Grace period color
                    fgcolor = "black"
                elif upcoming_reservation and slot_status == 1:
                    bgcolor = "blue"
                elif upcoming_reservation and slot_status == 0:
                    bgcolor = "yellow"
                    fgcolor = "black"
                elif slot_status == 1:
                    bgcolor = "gray"
                else:
                    bgcolor = "green"

                if has_reservation:
                    if has_reservation[11]:  # is_late is True - show grace period timer (index 11)
                        grace_result = self.grace_period_timer(has_reservation[12])  # grace_period_until at index 12
                        if grace_result:
                            grace_timer_text, grace_expired = grace_result
                            if grace_expired:
                                # Grace period expired - cancel the reservation
                                print(
                                    f"Grace period expired for reservation {has_reservation[0]} in slot {slot_number}")
                                if cancel_accepted_reservation(has_reservation[0]):
                                    print(f"Reservation {has_reservation[0]} cancelled successfully")
                                else:
                                    print(f"Failed to cancel reservation {has_reservation[0]}")
                                timer_expired = True
                    else:  # Normal reservation timer
                        timer_result = self.reservation_timer(has_reservation[7], has_reservation[8])
                        if timer_result:
                            timer_text, just_expired = timer_result
                            if just_expired:
                                # Set is_late to True
                                self.set_reservation_late(has_reservation[0])
                                timer_expired = True

                # Display appropriate text based on timer state
                if grace_timer_text:
                    if slot_status == 0:
                        pkg_text = f"{slot_number}\nAvailable\nGrace period: {grace_timer_text}"
                    else:
                        pkg_text = f"{slot_number}\n{slot[5]}\n{slot[3]}\nGrace period: {grace_timer_text}"
                elif timer_text and not timer_expired:
                    if slot_status == 0:
                        pkg_text = f"{slot_number}\nAvailable\nReservation in: {timer_text}"
                    else:
                        pkg_text = f"{slot_number}\n{slot[5]}\n{slot[3]}\nReservation in: {timer_text}"
                else:
                    pkg_text = f"{slot_number}\nAvailable\n" if slot_status == 0 else f"{slot_number}\n{slot[5]}\n{slot[3]}"

                if slot_number in self.park_slot_buttons:
                    self.park_slot_buttons[slot_number].config(text=pkg_text, bg=bgcolor, fg=fgcolor)

                self.previous_slot_status[slot_number] = (slot_status, has_reservation)
        except Exception as e:
            print(f"Fetch Error!", e)

    def open_view_more(self, slot_number):
        reservation = get_res_id_details(slot_number)

        self.r_more_info = {
            "Reservation Name": tk.StringVar(),
            "Reservation Date": tk.StringVar(),
            "Reservation Time": tk.StringVar(),
            "Owner Type": tk.StringVar(),
            "Contact Number": tk.StringVar(),
            "Plate Number": tk.StringVar(),
            "Vehicle Type": tk.StringVar(),
            "Assigned Slot": tk.StringVar()
        }

        self.window_view_more = tk.Toplevel(self.frame_reservation_info, bg='#e6e6e6', padx=10, pady=10)
        self.window_view_more.title("Reservation Details")
        self.window_view_more.geometry("350x380")

        self.frame_view_more = tk.Frame(self.window_view_more, bg='#b80000', padx=10, pady=10)
        self.frame_view_more.grid(row=0, column=0, sticky='nsew')

        self.btn_frame = tk.Frame(self.window_view_more, bg='#b80000', padx=10, pady=10)
        self.btn_frame.grid(row=1, column=0, sticky='nsew')

        tk.Frame(self.frame_view_more, bg='#b80000', height=50).grid(row=0, column=0, sticky='w')
        tk.Label(self.frame_view_more, text="Reservation Details", bg='#b80000', fg="white",
                 font=self.master.header_font).place(x=0, y=0)

        for i, (label_text, var) in enumerate(self.r_more_info.items(), start=1):
            tk.Label(self.frame_view_more, text=label_text, bg='#b80000', fg="white",
                     font=self.master.subheader_font, pady=5).grid(row=i, column=0, sticky='w')
            tk.Label(self.frame_view_more, textvariable=var, bg='#b80000', fg="white",
                     font=self.master.login_font, pady=5).grid(row=i, column=1, sticky='e')

        self.window_view_more.grid_columnconfigure(0, weight=1)
        self.frame_view_more.grid_columnconfigure(1, weight=1)
        self.frame_view_more.grid_columnconfigure(0, weight=1)
        self.btn_frame.grid_columnconfigure(0, weight=1)
        self.btn_frame.grid_columnconfigure(1, weight=1)

        self.r_more_info["Reservation Name"].set(reservation[1])
        self.r_more_info["Reservation Date"].set(reservation[7])
        self.r_more_info["Reservation Time"].set(reservation[8])
        self.r_more_info["Owner Type"].set(reservation[2])
        self.r_more_info["Contact Number"].set(reservation[4])
        self.r_more_info["Plate Number"].set(reservation[5])
        self.r_more_info["Vehicle Type"].set(reservation[6])
        self.r_more_info["Assigned Slot"].set(reservation[10])

        self.btn_park_reservation = tk.Button(self.btn_frame, text="Park Reservation", bg='#ffcc00', fg="black",
                                              font=self.master.subheader_font, relief="flat", command=lambda: self.park_reservation(slot_number))
        self.btn_park_reservation.grid(row=0, column=0, sticky='w')

        self.btn_cancel_reservation = tk.Button(self.btn_frame, text="Cancel Reservation", bg='red',
                                              fg="white", relief="flat", font=self.master.subheader_font, command=lambda: self.cancel_reservation(reservation[0]))
        self.btn_cancel_reservation.grid(row=0, column=1, sticky='e')

    def cancel_reservation(self, reservation_id):
        try:
            if messagebox.askquestion("Confirm", "Are you sure you want to cancel the reservation?") == "yes":
                if cancel_accepted_reservation(reservation_id):
                    messagebox.showinfo("Success", "Reservation Canceled")
                    self.window_view_more.destroy()
                    self.fetch_database(None)
        except Exception as e:
            print(f"Fetch Error!", e)

    def park_reservation(self, slot_number):
        try:
            reservation = get_res_id_details(slot_number)

            if reservation:
                if park_vehicle(slot_number, reservation[6], reservation[1], reservation[5], reservation[2], reservation[4]):
                    messagebox.showinfo("Success", "Reservation Parked")
                    delete_reservation(reservation[0])
                    self.window_view_more.destroy()
                    self.fetch_database(None)

        except Exception as e:
            print(f"Error! {e}")

    def get_slot_info(self, slot_number):

        for text in self.r_info:
            self.r_info[text].set("None")

        self.btn_reservation_view_more.grid_remove()

        for res in self.v_info:
            self.v_info[res].set("")

        if self.park_slot_buttons[slot_number]:

            result = next((res for res in self.park_slots if res[1] == slot_number))
            reservation_info = get_res_id_details(result[1])

            self.v_info["Slot Number"].set(result[1])
            self.v_info["Plate Number"].set(result[5])
            self.v_info["Vehicle Type"].set(result[3])
            self.v_info["Owner Name"].set(result[4])
            self.v_info["Contact Number"].set(result[7])

            self.unpark_button.configure(state="normal")

            if result[5] is None:
                self.unpark_button.configure(state="disabled")
                self.dropdown_park_slot.delete(0, "end")
                self.dropdown_park_slot.insert(0, result[1])

            if reservation_info:
                self.r_info["Reservation Name"].set(reservation_info[1])
                self.r_info["Reservation Date"].set(reservation_info[7])
                self.r_info["Reservation Time"].set(reservation_info[8])
                self.btn_reservation_view_more.grid()
                self.btn_reservation_view_more.configure(command=lambda: self.open_view_more(result[1]))

    def filter_owner_vehicles(self, event):
        owner_name = self.dropdown_owner.get()

        self.dropdown_plate_number.config(values=sorted([plate[2] for plate in get_owner_vehicles(owner_name)]))

    def auto_fill_entries(self, event):
        owner_name = self.dropdown_owner.get()

        owner_details = get_owner(owner_name)
        vehicle_details = get_vehicle_type(self.dropdown_plate_number.get())

        if owner_details:
            for entry in (self.dropdown_owner, self.dropdown_type, self.entry_contact_number):
                entry.delete(0, tk.END)

            self.dropdown_owner.insert(0, owner_details[1])
            self.dropdown_type.insert(0, owner_details[2])
            self.entry_contact_number.insert(0, owner_details[3])

        if vehicle_details:
            self.entry_vehicle_type.delete(0, tk.END)
            self.entry_vehicle_type.insert(0, vehicle_details[0])

    def submit_park(self):
        try:
            slot_number = self.dropdown_park_slot.get()
            vehicle_type = self.entry_vehicle_type.get()
            owner_name = self.dropdown_owner.get()
            plate_number = self.dropdown_plate_number.get()
            status_type = self.dropdown_type.get()
            contact_number = self.entry_contact_number.get()

            if not all([slot_number, vehicle_type, owner_name, plate_number, status_type, contact_number]):
                raise Exception("Please enter all required fields!",
                                messagebox.showerror("Error", "Please enter all required fields!"))

            if get_parkslot_info(slot_number)[2] == 1:
                raise Exception("Slot is occupied!", messagebox.showerror("Error", f"Slot {slot_number} is occupied!"))

            if not is_valid_plate_number(plate_number):
                raise Exception("Invalid plate number!", messagebox.showerror("Error", "Invalid Plate Number"))

            if not slot_number in self.slot_numbers:
                raise Exception(messagebox.showerror("Error", "Slot number must be in parking slots!"))

            if park_vehicle(slot_number, vehicle_type, owner_name, plate_number, status_type,
                            contact_number):
                messagebox.showinfo("Success", f"{vehicle_type} | {plate_number}\nParked Successfully!")
                self.fetch_database(None)

                for e in (self.dropdown_owner, self.dropdown_plate_number, self.entry_vehicle_type, self.entry_contact_number,
                          self.dropdown_type, self.dropdown_park_slot):
                    e.delete(0, tk.END)
        except Exception as e:
            print(f"Error: {e.args[0]}")

    def submit_unpark(self):
        try:
            slot = self.v_info["Slot Number"].get()

            if unpark_vehicle(slot):
                messagebox.showinfo("Success", f"Slot {slot}\nVehicle Unparked!")
                self.fetch_database(None)

                for v_info in self.v_info.values():
                    v_info.set("")

                self.v_info["Vehicle Type"].set("Select a slot")
                self.unpark_button.configure(state="disabled")


        except Exception as e:
            print(f"Error: {e.args[0]}")

class ReservationsPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#e6e6e6", padx=10, pady=10)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._initialize_inner_frames()
        self._initialize_frame_titles()
        self._initialize_grid()
        self._initialize_detail_labels()
        self._initialize_table_style()
        self._initialize_legend()
        self._initialize_action_widgets()
        self._initialize_buttons()
        self._create_table()
        self.fetch_reservations()

    def refresh_data(self):
        self.fetch_reservations()

    def _initialize_inner_frames(self):
        self.reservation_manager = tk.Frame(self, bg="#b80000", padx=10, pady=10)
        self.reservation_details = tk.Frame(self.reservation_manager, bg="#8f0000", padx=10, pady=10)
        self.reservations_actions = tk.Frame(self.reservation_manager, bg='#8f0000', padx=10, pady=10)

    def _initialize_legend(self):
        self.frame_legend = tk.Frame(self.reservation_manager, bg="#b80000")
        self.frame_legend.grid(row=0, column=1, sticky="nsew")

        tk.Frame(self.frame_legend, bg="#b80000", height=8).grid(row=0, column=0, sticky="nsew")

        self.square_pending = tk.Canvas(self.frame_legend, bg="#fe9705", width=5, height=5)
        self.square_pending.grid(row=1, column=1, sticky="nsew")

        self.label_pending = tk.Label(self.frame_legend, bg="#b80000", fg="white", text="Pending", font=self.master.login_font, padx=10)
        self.label_pending.grid(row=1, column=2, sticky="nw")

        self.square_approved = tk.Canvas(self.frame_legend, bg="#3ac430", width=5, height=5)
        self.square_approved.grid(row=1, column=3, sticky="nsew")

        self.label_approved = tk.Label(self.frame_legend, bg="#b80000", fg="white", text="Approved", font=self.master.login_font, padx=10)
        self.label_approved.grid(row=1, column=4, sticky="nw")

        self.square_rejected = tk.Canvas(self.frame_legend, bg="#a9a9a9", width=5, height=5)
        self.square_rejected.grid(row=1, column=5, sticky="nsew")

        self.label_rejected = tk.Label(self.frame_legend, bg="#b80000", fg="white", text="Rejected", font=self.master.login_font, padx=10)
        self.label_rejected.grid(row=1, column=6, sticky="nw")

        for i in range(1, 7, 2):
            self.frame_legend.columnconfigure(i, weight=1)

    def _initialize_frame_titles(self):
        tk.Frame(self.reservation_manager, bg="#b80000", height=50).grid(row=0, column=0, sticky="w")
        tk.Label(self.reservation_manager, text="Manage Reservations", bg="#b80000", fg="white", font=self.master.header_font).place(x=0, y=0)

        tk.Frame(self.reservation_details, bg="#8f0000", height=35).grid(row=0, column=0, sticky="w")
        tk.Label(self.reservation_details, text="Reservation Details", bg="#8f0000", fg="white", font=("Helvetica", 16, "bold")).place(x=0, y=0)

        tk.Frame(self.reservations_actions, bg="#8f0000", height=35).grid(row=0, column=0, sticky="w")
        tk.Label(self.reservations_actions, text="Actions", bg="#8f0000", fg="white", font=("Helvetica", 16, "bold")).place(x=0, y=0)

    def _initialize_grid(self):
        self.reservation_manager.grid(column=0, row=0, sticky="nsew")
        self.reservation_details.grid(column=0, row=3, sticky="nsew")
        self.reservations_actions.grid(row=3, column=1, sticky="nsew")

        self.reservation_manager.columnconfigure(0, weight=1)
        self.reservation_manager.columnconfigure(1, weight=1)
        self.reservation_manager.rowconfigure(4, weight=1)

        for i in range(0, 8):
            self.reservation_details.rowconfigure(i, weight=1)

        self.reservation_details.columnconfigure(2, weight=1)

        self.reservations_actions.columnconfigure(1, weight=2)
        self.reservations_actions.columnconfigure(2, weight=1)

    def _initialize_action_widgets(self):
        label_select_slot = tk.Label(self.reservations_actions, text="Select a slot:", font=self.master.subheader_font, bg="#8f0000", fg="white")
        label_select_slot.grid(row=1, column=0, sticky="w")

        self.selected_slot = tk.StringVar()
        self.selected_slot.set("None")

        label_selected_slot = tk.Label(self.reservations_actions, textvariable=self.selected_slot, font=self.master.login_font, bg="#8f0000", fg="white")
        label_selected_slot.grid(row=1, column=1, sticky="e")

    def _initialize_detail_labels(self):
        self.details = {
            "Owner Name": tk.StringVar(),
            "Owner Type": tk.StringVar(),
            "Email": tk.StringVar(),
            "Contact Number": tk.StringVar(),
            "Plate Number": tk.StringVar(),
            "Vehicle Type": tk.StringVar(),
            "Reservation Date": tk.StringVar(),
            "Reservation Time": tk.StringVar(),
            "Status": tk.StringVar()
        }

        for i, (label_text, var) in enumerate(self.details.items(), start=1):
            tk.Label(self.reservation_details, text=label_text, bg='#8f0000', fg="white",
                     font=self.master.subheader_font, pady=3).grid(row=i, column=0, sticky='w')
            tk.Label(self.reservation_details, textvariable=var, bg='#8f0000', fg="white",
                     font=self.master.login_font, pady=3, width=20, anchor='e').grid(row=i, column=2, sticky='e')

    def _initialize_buttons(self):
        select_slot_button = tk.Button(self.reservations_actions, text="View Grid", bg="#ffcc00", fg="black",
                                       relief="flat", command=self.slot_selection_window)
        select_slot_button.grid(row=1, column=2, sticky="ne")

        tk.Frame(self.reservations_actions, height=5, bg="#8f0000").grid(row=2, column=0, sticky="nsew")

        accept_reservation_button = tk.Button(self.reservations_actions, text="Accept Reservation", bg="green", fg="white",
                                              relief="flat", command=self.accept_reservation)
        accept_reservation_button.grid(row=3, column=0, columnspan=3, sticky="nsew")

        tk.Frame(self.reservations_actions, height=5, bg="#8f0000").grid(row=4, column=0, sticky="nsew")

        reject_reservation_button = tk.Button(self.reservations_actions, text="Reject Reservation", bg="gray",
                                              relief="flat", command=self.reject_reservation)
        reject_reservation_button.grid(row=5, column=0, columnspan=3, sticky="nsew")

        tk.Frame(self.reservations_actions, height=5, bg="#8f0000").grid(row=6, column=0, sticky="nsew")

        refresh_button = tk.Button(self.reservations_actions, text="Refresh", bg="#ffcc00", fg="black", relief="flat",
                                   command=self.fetch_reservations)
        refresh_button.grid(row=7, column=0, columnspan=3, sticky="nsew")

    def slot_selection_window(self):
        window = tk.Toplevel(self.reservations_actions, bg="#e6e6e6")
        window.title("Assign Slot to Reservation")
        window.geometry("800x600")

        frame_park_slots = tk.Frame(window, bg="#b80000", padx=5, pady=5)
        frame_park_slots.pack(pady=20, padx=20, fill="both", expand=True)

        for col in range(5):
            frame_park_slots.columnconfigure(col, weight=1)

        j = 0
        i = 1
        park_slot_buttons = {}

        for slot in self.park_slots:
            slot_number = slot[1]
            slot_status = slot[2]
            has_reservation = get_res_id_details(slot_number)

            upcoming_reservation = False

            if has_reservation:
                res_date = datetime.strptime(has_reservation[7], "%m-%d-%Y")
                res_time = datetime.strptime(has_reservation[8], "%H:%M")

                current_date = datetime.now().date()

                if res_date.date() == current_date:
                    reservation_datetime = datetime.combine(res_date.date(), res_time.time())
                    current_datetime = datetime.now()

                    time_diff = reservation_datetime - current_datetime

                    if 0 <= time_diff.total_seconds() <= 3600:
                        upcoming_reservation = True

            fgcolor = "white"

            if upcoming_reservation and slot_status == 1:
                bgcolor = "blue"
            elif upcoming_reservation and slot_status == 0:
                bgcolor = "yellow"
                fgcolor = "black"
            elif not upcoming_reservation and slot_status == 1:
                bgcolor = "gray"
            else:
                bgcolor = "green"

            has_reservation_today = False
            if has_reservation:
                res_date = datetime.strptime(has_reservation[7], "%m-%d-%Y")
                current_date = datetime.now().date()

                if res_date.date() == current_date:
                    has_reservation_today = True

            pkg_text = f"{slot_number}\nAvailable\n" if slot_status == 0 else f"{slot_number}\n{slot[5]}\n{slot[3]}"

            button_state = "disabled" if has_reservation_today else "normal"

            button = tk.Button(frame_park_slots, text=pkg_text, bg=bgcolor, fg=fgcolor, width=20,
                               command=lambda x=slot[1]: self.select_slot_for_reservation(x, window),
                               anchor="center", font=("Helvetica", 10), relief="ridge", state=button_state)
            button.grid(row=i, column=j, sticky='nsew', padx=2, pady=2)

            park_slot_buttons[slot[1]] = button

            j += 1

            if j == 5:
                j = 0
                i += 1

        for row in range(i + 1):
            frame_park_slots.rowconfigure(row, weight=1)

    def select_slot_for_reservation(self, slot_number, window):
        self.selected_slot.set(slot_number)
        window.destroy()

    def accept_reservation(self):
        try:
            slot_number = self.selected_slot.get()

            if not slot_number or slot_number == "None":
                raise Exception(messagebox.showerror("Error", "Select a parking slot first."))

            selection = self.reservation_table.selection()

            if not selection:
                raise Exception(messagebox.showerror("Error", "Select a reservation first."))

            reservation_values = self.reservation_table.item(selection[0], 'values')

            if reservation_values[9] != "PENDING":
                raise Exception(messagebox.showerror("Error", "That reservation is already approved or rejected."))

            if accept_reservation(reservation_values[0], slot_number):
                messagebox.showinfo("Success", f"Reservation {reservation_values[0]} is accepted and assigned to {slot_number}")
                self.selected_slot.set("None")
                self.fetch_reservations()
        except Exception as e:
            print(f"Error Occurred!", e)

    def reject_reservation(self):
        try:
            selection = self.reservation_table.selection()

            if not selection:
                raise Exception(messagebox.showerror("Error", "Select a reservation first."))

            reservation_values = self.reservation_table.item(selection[0], 'values')

            if reservation_values[9] != "PENDING":
                raise Exception(messagebox.showerror("Error", "That reservation is already approved or rejected."))

            if reject_reservation(reservation_values[0]):
                messagebox.showinfo("Success", f"Reservation {reservation_values[0]} is rejected.")
                self.fetch_reservations()
        except Exception as e:
            print(f"Error Occurred!", e)


    def _initialize_table_style(self):
        style = ttk.Style()

        style.theme_use("default")

        style.configure("Custom.Treeview", background="#8f0000", foreground="white", fieldbackground="#8f0000",
                        font=self.master.login_font, rowheight=30, relief="ridge")

        style.configure("Custom.Treeview.Heading", background="#ffcc00", foreground="black", font=self.master.subheader_font,
                        relief="raised", borderwidth=1)

        style.map("Custom.Treeview", background=[("selected", "#3390FF")], foreground=[("selected", "white")], bordercolor=[("selected", "black")], borderwidth=[("selected", 2)])

    def _create_table(self):
        table_columns = ("ID", "Name", "Type", "Email", "Contact Number", "Plate Number", "Vehicle Type", "Reservation Date", "Reservation Time")

        self.reservation_table = ttk.Treeview(self.reservation_manager, columns=table_columns, show="headings", style="Custom.Treeview", selectmode="browse")

        for col in table_columns:
            self.reservation_table.heading(col, text=col, anchor="w")

            if col == "ID":
                self.reservation_table.column(col, width=40, minwidth=40)
            elif col in ("Name", "Email"):
                self.reservation_table.column(col, width=150, minwidth=100)
            elif col in ("Plate Number", "Vehicle Type", "Type"):
                self.reservation_table.column(col, width=100, minwidth=60)
            else:
                self.reservation_table.column(col, width=120, minwidth=80)

        v_scrollbar = ttk.Scrollbar(self.reservation_manager, orient="vertical",
                                    command=self.reservation_table.yview)
        h_scrollbar = ttk.Scrollbar(self.reservation_manager, orient="horizontal",
                                    command=self.reservation_table.xview)

        self.reservation_table.configure(yscrollcommand=v_scrollbar.set,
                                         xscrollcommand=h_scrollbar.set)

        self.reservation_table.tag_configure('pending', background="#fe9705", foreground="white")
        self.reservation_table.tag_configure('approved', background="#3ac430", foreground="white")
        self.reservation_table.tag_configure('rejected', background="#a9a9a9", foreground="gray")

        self.reservation_table.bind("<<TreeviewSelect>>", self.on_table_selection)

        self.reservation_table.grid(column=0, row=1, columnspan=2, sticky="nsew")
        v_scrollbar.grid(column=2, row=1, sticky="ns")
        h_scrollbar.grid(column=0, row=2, columnspan=2, sticky="ew")

    def on_table_selection(self, event):
        selection = self.reservation_table.selection()

        if not selection:
            return

        values = self.reservation_table.item(selection[0], 'values')

        for i, results in enumerate(self.details.values(), start=1):
            results.set(values[i])

    def fetch_reservations(self):
        try:
            self.park_slots = sorted([slot for slot in get_parking_slots()])

            self.reservation_table.delete(*self.reservation_table.get_children())

            reservations_data = get_reservations()

            if not reservations_data:
                return

            for i, reservations in enumerate(reservations_data):
                if reservations[9] == "PENDING":
                    tag = "pending"
                elif reservations[9] == "APPROVED":
                    tag = "approved"
                else:
                    tag = "rejected"

                self.reservation_table.insert("", "end", values=reservations, tags=(tag,))
        except Exception as e:
            print(f"Error fetching reservations: {e}")


class VehiclesPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#e6e6e6", padx=10, pady=10)

        self.refresh_data()

        self._initialize_inner_frames()

        self.frames = {
            "Assign Vehicle": self.frame_assign_vehicle,
            "Unassign Vehicle": self.frame_unassign_vehicle
        }

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._initialize_frame_titles()
        self._initialize_grid()
        self._initialize_styles()
        self._create_assign_vehicle_labels()
        self._create_assign_vehicle_entries()
        self._create_unassign_vehicle_labels()
        self._create_unassign_vehicle_entries()
        self._assign_spacer_and_underline()
        self._create_submit_buttons()
        self._create_binds()

    def refresh_data(self):
        self.fetch_database()

    def _initialize_inner_frames(self):
        self.frame_assign_vehicle = tk.Frame(self, bg='#b80000', padx=10, pady=10)
        self.frame_unassign_vehicle = tk.Frame(self, bg='#b80000', padx=10, pady=10)

    def _initialize_frame_titles(self):
        for (title, f) in self.frames.items():
            tk.Frame(f, bg='#b80000', height=50).grid(row=0, column=0, sticky='w')
            tk.Label(f, text=title, bg='#b80000', fg="white",
                     font=self.master.header_font).place(x=0, y=0)

    def _initialize_grid(self):
        self.frames["Assign Vehicle"].grid(row=0, column=0, sticky='new')
        self.frames["Unassign Vehicle"].grid(row=0, column=2, sticky='new')

    def _initialize_styles(self):
        combobox_style = ttk.Style()
        combobox_style.theme_use('default')
        combobox_style.configure("CustomCombobox.TCombobox", fieldbackground="#b80000", foreground="#ffffff",
                                 relief="flat", borderwidth=0, highlightcolor="#b80000")
        combobox_style.map("CustomCombobox.TCombobox", selectbackground=[('!disabled', "#e6e6e6")],
                           selectforeground=[('!disabled', "black")])

    def _create_assign_vehicle_labels(self):
        labels = ["Owner Name", "Plate Number", "Vehicle Type"]

        i = 1
        for label in labels:
            tk.Label(self.frame_assign_vehicle, text=label, bg='#b80000', fg='white',
                     font=self.master.subheader_font).grid(row=i, column=0, sticky='w')
            i += 4

    def _create_assign_vehicle_entries(self):
        # Owner Name combobox
        self.dropdown_assign_owner = ttk.Combobox(self.frame_assign_vehicle, values=self.car_owners, state="normal",
                                                  style="CustomCombobox.TCombobox")
        self.dropdown_assign_owner.grid(row=3, column=0, sticky='nsew')

        # Plate Number entry
        self.entry_assign_plate = tk.Entry(self.frame_assign_vehicle, bg='#b80000', fg="white", relief="flat")
        self.entry_assign_plate.grid(row=7, column=0, sticky='nsew')

        # Vehicle Type entry
        self.entry_assign_vehicle_type = tk.Entry(self.frame_assign_vehicle, bg='#b80000', fg="white", relief="flat")
        self.entry_assign_vehicle_type.grid(row=11, column=0, sticky='nsew')

    def _create_unassign_vehicle_labels(self):
        labels = ["Owner Name", "Plate Number"]

        i = 1
        for label in labels:
            tk.Label(self.frame_unassign_vehicle, text=label, bg='#b80000', fg='white',
                     font=self.master.subheader_font).grid(row=i, column=0, sticky='w')
            i += 4

    def _create_unassign_vehicle_entries(self):
        # Owner Name combobox
        self.dropdown_unassign_owner = ttk.Combobox(self.frame_unassign_vehicle, values=self.car_owners, state="normal",
                                                    style="CustomCombobox.TCombobox")
        self.dropdown_unassign_owner.grid(row=3, column=0, sticky='nsew')

        # Plate Number combobox
        self.dropdown_unassign_plate = ttk.Combobox(self.frame_unassign_vehicle, values=[], state="normal",
                                                    style="CustomCombobox.TCombobox")
        self.dropdown_unassign_plate.grid(row=7, column=0, sticky='nsew')

    def _create_submit_buttons(self):
        # Assign Vehicle button
        self.assign_button = tk.Button(self.frame_assign_vehicle, text="Assign Vehicle", bg='#ffcc00', fg='black',
                                       relief="flat", command=self.submit_assign, font=self.master.subheader_font)
        self.assign_button.grid(row=14, column=0, sticky='nsew')

        # Unassign Vehicle button
        self.unassign_button = tk.Button(self.frame_unassign_vehicle, text="Unassign Vehicle", bg='#ffcc00', fg='black',
                                         relief="flat", command=self.submit_unassign, font=self.master.subheader_font)
        self.unassign_button.grid(row=10, column=0, sticky='nsew')

    def _create_binds(self):
        self.dropdown_unassign_owner.bind("<<ComboboxSelected>>", self.filter_owner_vehicles)
        self.dropdown_unassign_owner.bind("<Return>", self.filter_owner_vehicles)

    def _assign_spacer_and_underline(self):
        # Assign vehicle frame spacing
        i = 3
        while i <= 12:
            tk.Canvas(self.frame_assign_vehicle, bg="white", height=0,
                      width=200, highlightthickness=0).grid(row=i, column=0, sticky='sew')
            tk.Frame(self.frame_assign_vehicle, bg='#b80000', height=15).grid(row=i + 1, column=0, sticky='nsew')
            i += 4

        tk.Frame(self.frame_assign_vehicle, bg='#b80000', height=10).grid(row=13, column=0, sticky='nsew')
        self.frame_assign_vehicle.columnconfigure(0, weight=2)

        # Unassign vehicle frame spacing
        i = 3
        while i <= 8:
            tk.Canvas(self.frame_unassign_vehicle, bg="white", height=0,
                      width=200, highlightthickness=0).grid(row=i, column=0, sticky='sew')
            tk.Frame(self.frame_unassign_vehicle, bg='#b80000', height=15).grid(row=i + 1, column=0, sticky='nsew')
            i += 4

        tk.Frame(self.frame_unassign_vehicle, bg='#b80000', height=10).grid(row=9, column=0, sticky='nsew')
        self.frame_unassign_vehicle.columnconfigure(0, weight=2)

        # Main grid configuration
        tk.Frame(self, bg='#e6e6e6', width=15).grid(row=0, column=1, sticky='n')

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def fetch_database(self):
        try:
            self.car_owners = sorted([name[1] for name in get_car_owners()])
            self.dropdown_assign_owner.configure(values=self.car_owners)
            self.dropdown_unassign_owner.configure(values=self.car_owners)
        except Exception as e:
            print(f"Error: {e}")

    def filter_owner_vehicles(self, event):
        owner_name = self.dropdown_unassign_owner.get()

        self.dropdown_unassign_plate.config(values=sorted([plate[2] for plate in get_owner_vehicles(owner_name)]))

    def submit_assign(self):
        try:
            owner_name = self.dropdown_assign_owner.get()
            plate_number = self.entry_assign_plate.get()
            vehicle_type = self.entry_assign_vehicle_type.get()

            if not all([owner_name, plate_number, vehicle_type]):
                messagebox.showerror("Error", "You need to fill out all details")

            if assign_vehicle(owner_name, plate_number, vehicle_type):
                messagebox.showinfo("Success", f"Vehicle {plate_number} \nhas been assigned to {owner_name}")
                self.dropdown_assign_owner.delete(0, 'end')
                self.entry_assign_plate.delete(0, 'end')
                self.entry_assign_vehicle_type.delete(0, 'end')

        except Exception as e:
            print(f"Error: {e}")

    def submit_unassign(self):
        try:
            owner_name = self.dropdown_unassign_owner.get()
            plate_number = self.dropdown_unassign_plate.get()

            if not all([owner_name, plate_number]):
                raise Exception(messagebox.showerror("Error", "You must select at least one owner and plate number."))

            if unassign_vehicle(plate_number):
                messagebox.showinfo("Success", f"Vehicle {plate_number}\nhas been unassigned.")
                self.dropdown_unassign_plate.delete(0, tk.END)
                self.dropdown_unassign_owner.delete(0, tk.END)

        except Exception as e:
            print(f"Error: {e}")


class AccountsPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#e6e6e6", padx=10, pady=10)

        self._initialize_inner_frames()

        self.frames = {
            "New Car Owner": self.frame_new_car_owner,
            "Edit Car Owner": self.frame_edit_car_owner,
            "New Admin": self.frame_new_admin,
            "Edit Admin": self.frame_edit_admin
        }

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._initialize_frame_titles()
        self._initialize_grid()
        self._initialize_styles()
        self._create_new_car_owner_labels()
        self._create_new_car_owner_entries()
        self._create_edit_car_owner_labels()
        self._create_edit_car_owner_entries()
        self._create_new_admin_labels()
        self._create_new_admin_entries()
        self._create_edit_admin_labels()
        self._create_edit_admin_entries()
        self._accounts_spacer_and_underline()
        self._create_submit_buttons()
        self._create_binds()

        self.refresh_data()

    def refresh_data(self):
        self.car_owners = sorted([name[1] for name in get_car_owners()])
        self.dropdown_edit_name.config(values=self.car_owners)

        self.admins = sorted([username[1] for username in get_all_admins()])
        self.dropdown_edit_username.config(values=self.admins)

    def _initialize_inner_frames(self):
        self.frame_new_car_owner = tk.Frame(self, bg='#b80000', padx=10, pady=10)
        self.frame_edit_car_owner = tk.Frame(self, bg='#b80000', padx=10, pady=10)
        self.frame_new_admin = tk.Frame(self, bg='#b80000', padx=10, pady=10)
        self.frame_edit_admin = tk.Frame(self, bg='#b80000', padx=10, pady=10)

    def _initialize_frame_titles(self):
        for (title, f) in self.frames.items():
            tk.Frame(f, bg='#b80000', height=50).grid(row=0, column=0, sticky='w')
            tk.Label(f, text=title, bg='#b80000', fg="white",
                     font=self.master.header_font).place(x=0, y=0)

    def _initialize_grid(self):
        self.frames["New Car Owner"].grid(row=0, column=0, sticky='nsew')
        self.frames["Edit Car Owner"].grid(row=0, column=1, sticky='nsew')
        self.frames["New Admin"].grid(row=2, column=0, sticky='nsew')
        self.frames["Edit Admin"].grid(row=2, column=1, sticky='nsew')

    def _initialize_styles(self):
        combobox_style = ttk.Style()
        combobox_style.theme_use('default')

        # Configure the base style for readonly combobox
        combobox_style.configure("CustomCombobox.TCombobox",
                                 fieldbackground="#b80000",
                                 foreground="#ffffff",
                                 relief="flat",
                                 borderwidth=0,
                                 insertcolor="#ffffff",  # cursor color
                                 arrowcolor="#ffffff")  # dropdown arrow color

        # Map different states for proper readonly behavior
        combobox_style.map("CustomCombobox.TCombobox",
                           # Background colors for different states
                           fieldbackground=[('readonly', '#b80000'),
                                            ('disabled', '#808080'),
                                            ('active', '#c91010')],  # slightly lighter on hover

                           # Foreground colors for different states
                           foreground=[('readonly', '#ffffff'),
                                       ('disabled', '#cccccc'),
                                       ('active', '#ffffff')],

                           # Selection colors (for the dropdown list)
                           selectbackground=[('readonly', '#e6e6e6'),
                                             ('!disabled', '#e6e6e6')],
                           selectforeground=[('readonly', 'black'),
                                             ('!disabled', 'black')],

                           # Arrow color for different states
                           arrowcolor=[('readonly', '#ffffff'),
                                       ('disabled', '#cccccc'),
                                       ('active', '#ffffff')],

                           # Border/focus ring
                           focuscolor=[('readonly', '#b80000'),
                                       ('!disabled', '#b80000')])

    def _create_new_car_owner_labels(self):
        labels = ["Name", "Owner Type", "Email Address", "Contact Number"]

        for i, label in enumerate(labels, start=1):
            tk.Label(self.frame_new_car_owner, text=label, bg='#b80000', fg='white',
                     font=self.master.subheader_font).grid(row=i * 4 - 3, column=0, sticky='w')

    def _create_new_car_owner_entries(self):
        self.entry_new_name = tk.Entry(self.frame_new_car_owner, bg='#b80000', fg="white", relief="flat")
        self.entry_new_name.grid(row=2, column=0, sticky='nsew')

        self.dropdown_new_owner_type = ttk.Combobox(self.frame_new_car_owner,
                                                    values=["Student", "Staff", "Alumni", "Visitor"],
                                                    state="readonly", style="CustomCombobox.TCombobox")
        self.dropdown_new_owner_type.grid(row=6, column=0, sticky='nsew')

        self.entry_new_email = tk.Entry(self.frame_new_car_owner, bg='#b80000', fg="white", relief="flat")
        self.entry_new_email.grid(row=10, column=0, sticky='nsew')

        self.entry_new_contact = tk.Entry(self.frame_new_car_owner, bg='#b80000', fg="white", relief="flat")
        self.entry_new_contact.grid(row=14, column=0, sticky='nsew')

    def _create_edit_car_owner_labels(self):
        labels = ["Name", "Owner Type", "Email Address", "Contact Number"]

        for i, label in enumerate(labels, start=1):
            tk.Label(self.frame_edit_car_owner, text=label, bg='#b80000', fg='white',
                     font=self.master.subheader_font).grid(row=i * 4 - 3, column=0, columnspan=2, sticky='w')

    def _create_edit_car_owner_entries(self):
        self.dropdown_edit_name = ttk.Combobox(self.frame_edit_car_owner, values=[],
                                               state="readonly", style="CustomCombobox.TCombobox")
        self.dropdown_edit_name.grid(row=2, column=0, columnspan=2, sticky='nsew')

        self.dropdown_edit_owner_type = ttk.Combobox(self.frame_edit_car_owner,
                                                     values=["Student", "Staff", "Alumni", "Visitor"],
                                                     state="readonly", style="CustomCombobox.TCombobox")
        self.dropdown_edit_owner_type.grid(row=6, column=0, columnspan=2, sticky='nsew')

        self.entry_edit_email = tk.Entry(self.frame_edit_car_owner, bg='#b80000', fg="white", relief="flat")
        self.entry_edit_email.grid(row=10, column=0, columnspan=2, sticky='nsew')

        self.entry_edit_contact = tk.Entry(self.frame_edit_car_owner, bg='#b80000', fg="white", relief="flat")
        self.entry_edit_contact.grid(row=14, column=0, columnspan=2, sticky='nsew')

    def _create_new_admin_labels(self):
        labels = ["Username", "Password", "Admin Name", "Admin Email", "Master Password"]

        for i, label in enumerate(labels, start=1):
            tk.Label(self.frame_new_admin, text=label, bg='#b80000', fg='white',
                     font=self.master.subheader_font).grid(row=i * 4 - 3, column=0, sticky='w')

    def _create_new_admin_entries(self):
        self.entry_new_username = tk.Entry(self.frame_new_admin, bg='#b80000', fg="white", relief="flat")
        self.entry_new_username.grid(row=2, column=0, sticky='nsew')

        self.entry_new_password = tk.Entry(self.frame_new_admin, bg='#b80000', fg="white", relief="flat", show="*")
        self.entry_new_password.grid(row=6, column=0, sticky='nsew')

        self.entry_new_admin_name = tk.Entry(self.frame_new_admin, bg='#b80000', fg="white", relief="flat")
        self.entry_new_admin_name.grid(row=10, column=0, sticky='nsew')

        self.entry_new_admin_email = tk.Entry(self.frame_new_admin, bg='#b80000', fg="white", relief="flat")
        self.entry_new_admin_email.grid(row=14, column=0, sticky='nsew')

        self.entry_new_master_password = tk.Entry(self.frame_new_admin, bg='#b80000', fg="white", relief="flat",
                                                  show="*")
        self.entry_new_master_password.grid(row=18, column=0, sticky='nsew')

    def _create_edit_admin_labels(self):
        labels = ["Username", "Password", "Admin Name", "Admin Email", "Master Password"]

        for i, label in enumerate(labels, start=1):
            tk.Label(self.frame_edit_admin, text=label, bg='#b80000', fg='white',
                     font=self.master.subheader_font).grid(row=i * 4 - 3, column=0, columnspan=2, sticky='w')

    def _create_edit_admin_entries(self):
        self.dropdown_edit_username = ttk.Combobox(self.frame_edit_admin, values=[],
                                                   state="readonly", style="CustomCombobox.TCombobox")
        self.dropdown_edit_username.grid(row=2, column=0, columnspan=2, sticky='nsew')

        self.entry_edit_password = tk.Entry(self.frame_edit_admin, bg='#b80000', fg="white", relief="flat", show="*")
        self.entry_edit_password.grid(row=6, column=0, columnspan=2, sticky='nsew')

        self.entry_edit_admin_name = tk.Entry(self.frame_edit_admin, bg='#b80000', fg="white", relief="flat")
        self.entry_edit_admin_name.grid(row=10, column=0, columnspan=2, sticky='nsew')

        self.entry_edit_admin_email = tk.Entry(self.frame_edit_admin, bg='#b80000', fg="white", relief="flat")
        self.entry_edit_admin_email.grid(row=14, column=0, columnspan=2, sticky='nsew')

        self.entry_edit_master_password = tk.Entry(self.frame_edit_admin, bg='#b80000', fg="white", relief="flat",
                                                   show="*")
        self.entry_edit_master_password.grid(row=18, column=0, columnspan=2, sticky='nsew')

    def _create_submit_buttons(self):
        self.btn_new_car_owner_submit = tk.Button(self.frame_new_car_owner, text="Submit", bg='#ffcc00', fg='black',
                                                  relief="flat", command=self.submit_new_car_owner,
                                                  font=self.master.subheader_font)
        self.btn_new_car_owner_submit.grid(row=16, column=0, sticky='nsew')

        # Edit Car Owner Buttons
        self.btn_edit_car_owner_delete = tk.Button(self.frame_edit_car_owner, text="Delete", bg='red', fg='white',
                                                   relief="flat", command=self.delete_car_owner,
                                                   font=self.master.subheader_font)
        self.btn_edit_car_owner_delete.grid(row=16, column=0, sticky='ew')

        self.btn_edit_car_owner_confirm = tk.Button(self.frame_edit_car_owner, text="Confirm Edit", bg='#ffcc00',
                                                    fg='black',
                                                    relief="flat", command=self.confirm_edit_car_owner,
                                                    font=self.master.subheader_font)
        self.btn_edit_car_owner_confirm.grid(row=16, column=1, sticky='ew')

        # New Admin Submit Button
        self.btn_new_admin_submit = tk.Button(self.frame_new_admin, text="Submit", bg='#ffcc00', fg='black',
                                              relief="flat", command=self.submit_new_admin,
                                              font=self.master.subheader_font)
        self.btn_new_admin_submit.grid(row=20, column=0, sticky='nsew')

        # Edit Admin Buttons
        self.btn_edit_admin_delete = tk.Button(self.frame_edit_admin, text="Delete Admin", bg='red', fg='white',
                                               relief="flat", command=self.delete_admin,
                                               font=self.master.subheader_font)
        self.btn_edit_admin_delete.grid(row=20, column=0, sticky='ew')

        self.btn_edit_admin_confirm = tk.Button(self.frame_edit_admin, text="Confirm Edit", bg='#ffcc00', fg='black',
                                                relief="flat", command=self.confirm_edit_admin,
                                                font=self.master.subheader_font)
        self.btn_edit_admin_confirm.grid(row=20, column=1, sticky='ew')

    def _create_binds(self):
        # Add any bindings here if needed
        self.dropdown_edit_name.bind("<<ComboboxSelected>>", self.edit_owner_selected)
        self.dropdown_edit_username.bind("<<ComboboxSelected>>", self.edit_admin_selected)

    def _accounts_spacer_and_underline(self):
        for i in [2, 6, 10, 14]:
            tk.Canvas(self.frame_new_car_owner, bg="white", height=0,
                      width=200, highlightthickness=0).grid(row=i, column=0, sticky='sew')
            tk.Frame(self.frame_new_car_owner, bg='#b80000', height=15).grid(row=i + 1, column=0, sticky='nsew')

        tk.Frame(self.frame_new_car_owner, bg='#b80000', height=10).grid(row=15, column=0, sticky='nsew')
        self.frame_new_car_owner.columnconfigure(0, weight=1)

        for i in [2, 6, 10, 14]:
            tk.Canvas(self.frame_edit_car_owner, bg="white", height=0,
                      width=200, highlightthickness=0).grid(row=i, column=0, columnspan=2, sticky='sew')
            tk.Frame(self.frame_edit_car_owner, bg='#b80000', height=15).grid(row=i + 1, column=0, columnspan=2,
                                                                              sticky='nsew')

        tk.Frame(self.frame_edit_car_owner, bg='#b80000', height=10).grid(row=15, column=0, columnspan=2, sticky='nsew')
        self.frame_edit_car_owner.columnconfigure(0, weight=1)
        self.frame_edit_car_owner.columnconfigure(1, weight=1)

        # New Admin frame spacing
        for i in [2, 6, 10, 14, 18]:
            tk.Canvas(self.frame_new_admin, bg="white", height=0,
                      width=200, highlightthickness=0).grid(row=i, column=0, sticky='sew')
            tk.Frame(self.frame_new_admin, bg='#b80000', height=15).grid(row=i + 1, column=0, sticky='nsew')

        tk.Frame(self.frame_new_admin, bg='#b80000', height=10).grid(row=19, column=0, sticky='nsew')
        self.frame_new_admin.columnconfigure(0, weight=1)

        # Edit Admin frame spacing
        for i in [2, 6, 10, 14, 18]:
            tk.Canvas(self.frame_edit_admin, bg="white", height=0,
                      width=200, highlightthickness=0).grid(row=i, column=0, columnspan=2, sticky='sew')
            tk.Frame(self.frame_edit_admin, bg='#b80000', height=15).grid(row=i + 1, column=0, columnspan=2,
                                                                          sticky='nsew')

        tk.Frame(self.frame_edit_admin, bg='#b80000', height=10).grid(row=19, column=0, columnspan=2, sticky='nsew')
        self.frame_edit_admin.columnconfigure(0, weight=1)
        self.frame_edit_admin.columnconfigure(1, weight=1)

        tk.Frame(self, bg='#e6e6e6', height=15).grid(row=1, column=0, columnspan=2, sticky='ew')

    def submit_new_car_owner(self):
        try:
            owner_name = self.entry_new_name.get()
            owner_type = self.dropdown_new_owner_type.get()
            owner_email = self.entry_new_email.get()
            owner_number = self.entry_new_contact.get()

            if not all([owner_name, owner_type, owner_email, owner_number]):
                raise Exception(messagebox.showerror("Error", "Please enter all fields before submitting a new car owner"))

            if not is_valid_email(owner_email):
                raise Exception(messagebox.showerror("Error", "Please enter a valid email address"))

            if new_car_owner(owner_name, owner_email, owner_type, owner_number):
                messagebox.showinfo("Success", "New car owner successfully submitted")
                for e in (self.entry_new_name, self.entry_new_email, self.entry_new_contact):
                    e.delete(0, tk.END)
                self.dropdown_new_owner_type.set("")
                self.refresh_data()
        except Exception as e:
            print(f"Error: {e}")

    def edit_owner_selected(self, event=None):
        try:
            self.dropdown_edit_owner_type.set("")
            self.entry_edit_email.delete(0, tk.END)
            self.entry_edit_contact.delete(0, tk.END)

            owner_name = self.dropdown_edit_name.get()

            owner_details = get_owner(owner_name)

            if owner_details:
                self.dropdown_edit_name.configure(state="readonly")
                self.entry_edit_email.configure(state="normal")
                self.entry_edit_contact.configure(state="normal")

                self.dropdown_edit_owner_type.set(owner_details[2])
                self.entry_edit_email.insert(0, owner_details[4])
                self.entry_edit_contact.insert(0, owner_details[3])
        except Exception as e:
            print(f"Error: {e}")

    def delete_car_owner(self):
        try:
            owner_name = self.dropdown_edit_name.get()

            if not owner_name:
                raise Exception(messagebox.showerror("Error", "Please select a car owner"))

            if messagebox.askquestion("Delete car owner", "Are you sure you want to delete the car owner?") == "yes":
                if delete_car_owner(owner_name):
                    messagebox.showinfo("Success", "Car owner successfully deleted")
                    self.dropdown_edit_name.set("")
                    self.dropdown_edit_owner_type.set("")
                    self.entry_edit_email.delete(0, tk.END)
                    self.entry_edit_contact.delete(0, tk.END)
                    self.refresh_data()
            else:
                return
        except Exception as e:
            print(f"Error: {e}")

    def confirm_edit_car_owner(self):
        try:
            owner_name = self.dropdown_edit_name.get()
            owner_type = self.dropdown_edit_owner_type.get()
            owner_email = self.entry_edit_email.get()
            owner_contact = self.entry_edit_contact.get()

            if not all([owner_name, owner_type, owner_email, owner_contact]):
                raise Exception(messagebox.showerror("Error", "Please enter all fields before editing a car owner"))

            if not is_valid_email(owner_email):
                raise Exception(messagebox.showerror("Error", "Please enter a valid email address"))

            if edit_car_owner(owner_name, owner_type, owner_email, owner_contact):
                messagebox.showinfo("Success", "Car owner successfully edited")
                self.dropdown_edit_name.set("")
                self.dropdown_edit_owner_type.set("")
                self.entry_edit_email.delete(0, tk.END)
                self.entry_edit_contact.delete(0, tk.END)
                self.refresh_data()

        except Exception as e:
            print(f"Error: {e}")

    def submit_new_admin(self):
        try:
            username = self.entry_new_username.get()
            password = self.entry_new_password.get()
            admin_name = self.entry_new_admin_name.get()
            admin_email = self.entry_new_admin_email.get()
            master_password = self.entry_new_master_password.get()

            if not all([username, password, admin_name, admin_email, master_password]):
                raise Exception(messagebox.showerror("Error", "Please enter all fields before submitting a new admin"))

            if account_creation(username, password, admin_name, admin_email, master_password):
                messagebox.showinfo("Success", "New admin account successfully created")
                for e in (self.entry_new_username, self.entry_new_password, self.entry_new_admin_name, self.entry_new_admin_email, self.entry_new_master_password):
                    e.delete(0, tk.END)
                self.refresh_data()
            else:
                messagebox.showerror("Error", "Username already exists or incorrect master password")
        except Exception as e:
            print(f"Error: {e}")

    def delete_admin(self):
        try:
            username = self.dropdown_edit_username.get()
            master_password = self.entry_edit_master_password.get()

            if not all([username, master_password]):
                raise Exception(messagebox.showerror("Error", "Please select admin and enter master password"))

            if account_deletion(username, master_password):
                messagebox.showinfo("Success", "Admin account successfully deleted")
                self.dropdown_edit_username.set("")
                self.entry_edit_master_password.delete(0, tk.END)
                self.refresh_data()
            else:
                messagebox.showerror("Error", "Incorrect master password")
        except Exception as e:
            print(f"Error: {e}")

    def edit_admin_selected(self, event=None):
        try:
            self.entry_edit_password.delete(0, tk.END)
            self.entry_edit_email.delete(0, tk.END)
            self.entry_edit_admin_name.delete(0, tk.END)

            username = self.dropdown_edit_username.get()

            admin_details = get_admin_details(username)

            if admin_details:
                self.entry_edit_admin_name.insert(0, admin_details[3])
                self.entry_edit_admin_email.insert(0, admin_details[4])

        except Exception as e:
            print(f"Error: {e}")

    def confirm_edit_admin(self):
        try:
            username = self.dropdown_edit_username.get()
            admin_name = self.entry_edit_admin_name.get()
            admin_email = self.entry_edit_admin_email.get()
            master_password = self.entry_edit_master_password.get()

            password = self.entry_edit_password.get().strip()

            if not all([username, admin_name, admin_email, master_password]):
                raise Exception(messagebox.showerror("Error", "Please enter all fields before editing an admin"))

            if password == "":
                password = None

            if account_edit(username, password, admin_name, admin_email, master_password):
                messagebox.showinfo("Success", "Admin account successfully edited")
                self.dropdown_edit_username.set("")
                self.entry_edit_master_password.delete(0, tk.END)
                self.entry_edit_admin_name.delete(0, tk.END)
                self.entry_edit_password.delete(0, tk.END)
                self.entry_edit_admin_email.delete(0, tk.END)
                self.refresh_data()
            else:
                raise Exception(messagebox.showerror("Error", "Incorrect master password"))
        except Exception as e:
            print(f"Error: {e}")

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def is_valid_plate_number(plate_number):
    pattern = r'^[A-Z]{3} \d{4}$'
    return re.match(pattern, plate_number) is not None

if __name__ == "__main__":
    app = App()
    app.mainloop()