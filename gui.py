# https://github.com/TomSchimansky/CustomTkinter
# https://github.com/TomSchimansky/CustomTkinter/wiki
# https://github.com/TomSchimansky/CustomTkinter/blob/master/examples/complex_example.py


from main import package_table
import pandas as pd
from pandastable import Table, TableModel, config
from CTkTable import *
import tkinter as tk
from tkinter import ttk
import tkintermapview
from CTkMessagebox import CTkMessagebox
import customtkinter as ctk

class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configure welcome message and options/df import for gui
        self.welcome_msg = f"Student Name: {student.first} {student.last}\n" \
                           f"Student ID: {student.stu_id}\n" \
                           f"Course: {student.course_name} - {student.course_id}\n" \
                           f"Algorithm Identity: Dijkstra's Shortest Path\n" \
                           f"Data Structure: Chaining HashTable"

        self.pkgs_file = 'data/reformatted_package.csv'
        self.pkgs_df = pd.read_csv(self.pkgs_file)

        self.options = {'cellbackgr': '#DDDDDD',
                        'font': 'Arial',
                        'fontsize': 12,
                        'grid_color': '#999933',
                        'rowselectedcolor': '#88CCEE',
                        'linewidth': 1,
                        'textcolor': 'black'}
        self.invalid_id = "You Entered An Invalid Package ID\nPlease Check the ID and Try Again"
        self.invalid_entry = "Invalid Entry\nPlease Enter an Integer"


        # configure window
        self.title("Gerald Carter's Algorithm Project")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Ship-O-Matic",
                                       font=ctk.CTkFont(family='Arial', size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = ctk.CTkButton(self.sidebar_frame, command=self.sidebar_button_event)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = ctk.CTkButton(self.sidebar_frame, command=self.sidebar_button_event)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_3 = ctk.CTkButton(self.sidebar_frame, command=self.sidebar_button_event)
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark",
                                                                                         "System"],
                                                             command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = ctk.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%",
                                                                                 "110%", "120%"],
                                                     command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        # create main entry and button
        self.entry = ctk.CTkEntry(self, placeholder_text="Enter Package ID")
        self.entry.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.string_input_button = ctk.CTkButton(master=self, fg_color="transparent", border_width=2,
                                                 text_color=("gray10", "#DCE4EE"), command=self.search_button_event)
        self.string_input_button.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # create textbox
        self.textbox = ctk.CTkTextbox(self, width=250)
        self.textbox.grid(row=0, rowspan=3, column=1, columnspan=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # set default values
        self.string_input_button.configure(text='Submit')
        self.sidebar_button_1.configure(text='Package List')
        self.sidebar_button_2.configure(text='Option 2')
        self.sidebar_button_3.configure(text="Option 3")
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")
        self.textbox.insert("0.0", self.welcome_msg)

    def open_input_dialog_event(self):
        dialog = ctk.CTkInputDialog(text="Type in a number:", title="Enter Package ID")
        print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        if self.sidebar_button_1:
            self.textbox.delete("0.0", "200.0")
            pkgs_frame = ctk.CTkFrame(self, width=250)
            pkgs_frame.grid(row=0, rowspan=3, column=1, columnspan=3,
                            padx=(20, 20), pady=(20, 20), sticky="nsew")
            pt = Table(pkgs_frame)
            pkgs_df = pd.read_csv(self.pkgs_file)
            pkgs_table = pt = Table(pkgs_frame, dataframe=pkgs_df,
                                    showtoolbar=False, showstatusbar=True)

            config.apply_options(self.options, pkgs_table)
            pt.show()

    def invalid_pkg_entry_event(self, error_type=str()):
        if error_type == self.invalid_id:
            msg = CTkMessagebox(title="Invalid Entry", message=error_type, icon="warning",
                                option_1="Retry", cancel_button="cross")
            if msg.get() == "Retry":
                msg.destroy()

        elif error_type == self.invalid_entry:
            msg = CTkMessagebox(title="Invalid Entry", message=error_type, icon="warning",
                                option_1="Ok", cancel_button="cross")
            if msg.get() == "Ok":
                msg.destroy()

    def pkg_info_return_event(self):
        self.textbox.delete("0.0", "200.0")
        s_pkgs_frame = ctk.CTkFrame(self, width=250)
        s_pkgs_frame.grid(row=0, rowspan=3, column=1, columnspan=3,
                          padx=(20, 20), pady=(20, 20), sticky="nsew")
        st = Table(s_pkgs_frame)
        pkg = package_table.get_pkg_by_id(int(self.entry.get()))
        pkg_dict = {"ID": pkg.get_pkg_uid(), "Address": pkg.get_pkg_addr(), "City": pkg.get_city(),
                    "State": pkg.get_state(), "Zip": pkg.get_postal_code(), "Deadline": pkg.get_delivery_promise(),
                    "Weight": pkg.get_pkg_weight(), "Note": pkg.get_note(), "Status": pkg.get_pkg_status()}

        df = pd.DataFrame(pkg_dict, index=[1])
        single_table = st = Table(s_pkgs_frame, dataframe=df, showtoolbar=False,
                                  showstatusbar=False)
        config.apply_options(self.options, single_table)
        st.show()

    def search_button_event(self):
        if self.string_input_button:
            pkg_ids = self.pkgs_df.index.to_list()
            usr_txt = self.entry.get()
            try:
                usr_txt = int(usr_txt)
                if usr_txt not in pkg_ids:
                    self.invalid_pkg_entry_event(self.invalid_id)
                else:
                    self.pkg_info_return_event()
            except ValueError:
                self.invalid_pkg_entry_event(self.invalid_entry)


if __name__ == "__main__":
    app = App()
    app.mainloop()
