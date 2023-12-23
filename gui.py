from delivery_services.routing import auto_router
from delivery_services.pkg_handler import PkgObject

import pandas as pd
from pandastable import Table, config
from CTkTable import *
import tkinter as tk
from tkinter import ttk
import tkintermapview
from CTkMessagebox import CTkMessagebox
import customtkinter as ctk
from pathlib import Path


class App(ctk.CTk):
    pkgs, trucks = auto_router()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pkgs = App.pkgs
        self.trucks = App.trucks
        self.welcome_msg()
        self.time = 0
        self.pkgs_file = Path.cwd() / 'input_files' / '__WGUPS Package File.csv'
        self.pkgs_df = pd.read_csv(self.pkgs_file)

        self.options = {'cellbackgr': '#DDDDDD',
                        'font': 'Arial',
                        'fontsize': 12,
                        'grid_color': '#999933',
                        'rowselectedcolor': '#88CCEE',
                        'linewidth': 1,
                        'textcolor': 'black'}


        # These options configure the initial GUI window
        self.title("Gerald Carter's Algorithm Project")
        self.geometry(f"{1100}x{580}")

        # Sets the side of the GUI Grid (4x4) in this case
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # Creates the sidebar with buttons and adds a title
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Ship-O-Matic",
                                       font=ctk.CTkFont(family='Arial', size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = ctk.CTkButton(self.sidebar_frame, command=self.sidebar_button_event)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = ctk.CTkButton(self.sidebar_frame, command=self.open_input_dialog_event)
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

        # Creates the box that accepts text entry from a user
        self.entry = ctk.CTkEntry(self, placeholder_text="Enter Package ID")
        self.entry.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.string_input_button = ctk.CTkButton(master=self, fg_color="transparent", border_width=2,
                                                 text_color=("gray10", "#DCE4EE"), command=self.search_button_event)
        self.string_input_button.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # Defines a textbox for use by other methods
        self.textbox = ctk.CTkTextbox(self, width=250)
        self.textbox.grid(row=0, rowspan=3, column=1, columnspan=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # Sets the names of all the buttons and their default values if needed
        self.string_input_button.configure(text='Submit')
        self.sidebar_button_1.configure(text='List All Packages')
        self.sidebar_button_2.configure(text='Option 2')
        self.sidebar_button_3.configure(text="Option 3")
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")
        self.textbox.insert("0.0", self.welcome_msg())

    # Display a welcome message with pertinent project information
    @staticmethod
    def welcome_msg() -> str:
        welcome_msg = f'Student Name: Gerald Carter\n'
        welcome_msg += f'Student ID: 000366007\n'
        welcome_msg += f"Course: Data Structures & Algorithms II - C950\n"
        welcome_msg += f'Algorith Name: Nearest Neighbor\n'
        welcome_msg += f"Data Structure: Chaining HashTable"
        return welcome_msg

    def error_text(self, error: str) -> str:
        '''
        Ensures any error message shown the user is consistent
        :param error:
        :return:
        '''
        if error == 'wrong_id':
            return 'The package identification number you\'ve entered is incorrect.\n' \
                    'Please check the identification number and try again.'

        if error == 'invalid_type':
            return 'Your entry is an invalid package ID number. Please ensure you are entering'\
                    'an integer and try again.'

    def open_input_dialog_event(self):
        pkg_id_input = ctk.CTkInputDialog(text="Type in a number:", title="Enter Package ID")
        time_input = ctk.CTkInputDialog(text='Please enter a time value in the format HH:MM (ex: 10:30)',
                                        title="Enter Time")
        return pkg_id_input.get_input(), time_input.get_input()

    def change_appearance_mode_event(self, new_appearance_mode: str) -> None:
        ctk.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str) -> None:
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self) -> None:
        '''
        This method listens for button press events for the sidebar buttons
        in this instances it converts the packages file into a table for viewing
        :param: None
        :return: None
        '''
        if self.sidebar_button_1:
            self.textbox.delete("0.0", "200.0")
            pkgs_frame = ctk.CTkFrame(self, width=250)
            pkgs_frame.grid(row=0, rowspan=3, column=1, columnspan=3,
                            padx=(20, 20), pady=(20, 20), sticky="nsew")
            pt = Table(pkgs_frame)
            pkgs_df = pd.read_csv(self.pkgs_file, delimiter=';', header=0)
            pkgs_table = pt = Table(pkgs_frame, dataframe=pkgs_df,
                                    showtoolbar=False, showstatusbar=True)

            config.apply_options(self.options, pkgs_table)
            pt.show()

    # Provides an error message if an incorrect value/value type is used
    def invalid_pkg_entry_event(self, error_type=str()):
        if error_type == 'wrong_id':
            msg = CTkMessagebox(title="Invalid Entry", message=self.error_text(error_type), icon="warning",
                                option_1="Retry", cancel_button="cross")
            if msg.get() == "Retry":
                msg.destroy()

        elif error_type == 'invalid_type':
            msg = CTkMessagebox(title="Invalid Entry", message=self.error_text(error_type), icon="warning",
                                option_1="Ok", cancel_button="cross")
            if msg.get() == "Ok":
                msg.destroy()

    def get_pkg_info(self, pkg: PkgObject, time: int) -> dict:
        '''
        This builds a dictionary of attributes for the specified package IO
        :param pkg:
        :param time:
        :return: Dictionary of package status information
        '''
        pkg_dict = {'Pkg ID': pkg.pkg_id, 'Pkg Address': pkg.str_addr, 'City': pkg.city,
                    'State/Postal Code': [pkg.state, pkg.postal_code],'Pkg Status': pkg.__get_pkg_status(time),
                    'Pkg Delivery Promise': pkg.promise_format(), 'Pkg Weight': pkg.weight}
        return pkg_dict

    def search_button_event(self):
        if self.string_input_button:
            pkg_ids = self.pkgs_df.index.to_list()
            usr_txt = self.entry.get()
            try:
                usr_txt = int(usr_txt)
                if usr_txt not in pkg_ids:
                    self.invalid_pkg_entry_event('wrong_id')
                else:
                    self.pkg_info_return_event()
            except ValueError:
                self.invalid_pkg_entry_event('invalid_type')

    def pkg_info_return_event(self):
        tmp_pkgs = self.pkgs
        self.textbox.delete("0.0", "200.0")
        s_pkgs_frame = ctk.CTkFrame(self, width=250)
        s_pkgs_frame.grid(row=0, rowspan=3, column=1, columnspan=3,
                          padx=(20, 20), pady=(20, 20), sticky="nsew")
        st = Table(s_pkgs_frame)
        while not (pkg_id := self.entry.get()) in tmp_pkgs:
            self.invalid_pkg_entry_event('invalid_id')

        pkg = tmp_pkgs.get(pkg_id)
        pkg_dict = self.get_pkg_info(pkg, self.time)

        df = pd.DataFrame(pkg_dict, index=[1])
        single_table = st = Table(s_pkgs_frame, dataframe=df, showtoolbar=False,
                                  showstatusbar=False)
        config.apply_options(self.options, single_table)
        st.show()


if __name__ == "__main__":
    app = App()
    app.mainloop()
