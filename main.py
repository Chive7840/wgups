#
# Student Name: Gerald Carter
# Student ID: 000366007
#

# Internal modules
from delivery_services.routing import auto_router
from utilities import convert_minutes, deadline_to_minutes

# External libraries/modules
import pandas as pd
from pandastable import Table, config
from CTkMessagebox import CTkMessagebox
import customtkinter as ctk
import re
from datetime import datetime
from pathlib import Path
from enum import auto, Enum

# direct path link to the main.py file
SOURCE_FILE_MAIN = Path(__file__).resolve()

# formatting options for using pandas as a means of cleanly displaying a table
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.colheader_justify', 'center')
# Sets default appearance for the gui when launched
ctk.set_appearance_mode('dark')


class App(ctk.CTk):
    """
    This class is used for building the GUI and running all the functions within it
    """

    class ErrorCode(Enum):
        """
        This class is used to efficiently surface error messages to the user
        """
        NO_ERR = auto()
        WRONG_ID = auto()
        INVALID_TIME = auto()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pkgs, self.trucks = auto_router()  # Runs the routing algorithm on startup
        self.__error = self.ErrorCode.NO_ERR  # Sets the error handling flag to the default
        self.pkg_index = []  # A list of pkg IDs used in creating a visualization
        self.pkg_id_desc = []  # list of packages in descending order
        self.ordered_pkg_lst = []  # A list with reduced attributes used for a visualization
        self.pkg_data_refresh()  # A method used to populate a list of packages and refresh that list if needed
        # Configuration options for the table display
        self.options = {'cellbackgr': '#DDDDDD',
                        'font': 'Arial',
                        'fontsize': 12,
                        'grid_color': '#999933',
                        'rowselectedcolor': '#88CCEE',
                        'linewidth': 1,
                        'textcolor': 'black'}
        # Configuration for the toplevel GUI frame
        self.title("Gerald Carter's Algorithm Project")
        self.geometry(f"{1100}x{580}")

        # Lays out a grid for the gui to use when creating frames
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # Creates the sidebar with buttons and adds a title
        self.left_sidebar = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.left_sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.left_sidebar.grid_rowconfigure(4, weight=1)
        self.logo_label = ctk.CTkLabel(self.left_sidebar, text="Ship-O-Matic",
                                       font=ctk.CTkFont(family='Arial', size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.display_all_pkgs = ctk.CTkButton(self.left_sidebar, command=self.display_all_pkgs_event)
        self.display_all_pkgs.grid(row=1, column=0, padx=20, pady=10)
        self.status_all_pkgs = ctk.CTkButton(self.left_sidebar, command=self.pkg_status_request_event)
        self.status_all_pkgs.grid(row=2, column=0, padx=20, pady=10)
        self.truck_mileage = ctk.CTkButton(self.left_sidebar, command=self.truck_info_request_event)
        self.truck_mileage.grid(row=3, column=0, padx=20, pady=10)

        # Label for the user package search bars
        self.pkg_search_label = ctk.CTkLabel(self, text="Search for a Package",
                                             font=ctk.CTkFont(family='Arial', size=15, weight="bold"))
        self.pkg_search_label.grid(row=2, column=0, padx=20, pady=(60, 60), sticky="ews")
        # Text input bar for package ID
        self.pkg_id_entry = ctk.CTkEntry(self, placeholder_text="Enter Package ID")
        self.pkg_id_entry.grid(row=2, column=0, padx=(20, 20), pady=(0, 0), sticky="ws")
        # Text input bar for time
        self.time_entry = ctk.CTkEntry(self, placeholder_text="Enter a time: HH:MM")
        self.time_entry.grid(row=2, column=0, padx=(20, 20), pady=(0, 30), sticky="ws")
        # Submit button for individual package search
        self.string_input_button = ctk.CTkButton(master=self, fg_color="transparent", border_width=2,
                                                 text_color=("gray10", "#DCE4EE"), command=self.user_txt_search_event)
        self.string_input_button.grid(row=3, column=0, padx=(20, 20), pady=(20, 20), sticky="ws")

        # Defines a textbox for use by other methods
        self.textbox = ctk.CTkTextbox(master=self, width=250)
        self.textbox.grid(row=0, rowspan=3, column=1, columnspan=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # Sets the names of all the buttons and their default values if needed
        self.display_all_pkgs.configure(text='Show All Packages')
        self.status_all_pkgs.configure(text='Status of All Packages')
        self.truck_mileage.configure(text="Truck Mileage")
        self.string_input_button.configure(text='Submit')
        self.welcome_msg()

    # Display a welcome message with pertinent project information
    def welcome_msg(self):
        """
        Used as a splash screen on startup the method displays student/class information
        :return No return value:
        """
        welcome_msg = [f"Data Structure: Chaining HashTable", f'Algorith Name: Nearest Neighbor\n'
                                                              f"Course: Data Structures & Algorithms II - C950\n",
                       f'Student ID: 000366007\n', f'Student Name: Gerald Carter\n']

        textbox = ctk.CTkTextbox(master=self, width=250, font=ctk.CTkFont(family='Arial', size=15, weight="bold"))
        textbox.grid(row=0, rowspan=3, column=1, columnspan=3, padx=(20, 20), pady=(20, 20), sticky="nsew")
        for item in welcome_msg:
            textbox.insert('0.0', item)

    def pkg_data_refresh(self):
        """
        On program startup this method will create an ordered list of package objects
        sorted by package ID. It will also create an index of the package IDs
        It is a collable method used for refreshing package data in case any changes are made
        :return No return value:
        """
        self.pkg_id_desc = [[pkg_id, pkg_obj] for (pkg_id, pkg_obj) in self.pkgs]
        self.pkg_id_desc.sort(key=lambda x: x[0])

        for pkg in self.pkg_id_desc:
            tmp_time = convert_minutes(pkg[1].delivery_promise)
            self.ordered_pkg_lst.append([pkg[0], pkg[1].address, pkg[1].city, pkg[1].state,
                                         pkg[1].postal_code, tmp_time])
            self.pkg_index.append(pkg[0])

    def __error_no_err(self) -> bool:
        """
        This method is used to check if the error code has been reset
        :return True/False:
        """
        return self.__error == self.ErrorCode.NO_ERR

    def __error_wrong_id(self) -> bool:
        """
        This method is used to check if a wrong_id error message
        should be displayed
        :return True/False:
        """
        return self.__error == self.ErrorCode.WRONG_ID

    def __error_invalid_time(self) -> bool:
        """
        This method is used to check if an invalid time formatting error message
        should be displayed
        :return True/False:
        """
        return self.__error == self.ErrorCode.INVALID_TIME

    def raise_error(self, *args):
        """
        This method creates error messaging and the user facing pop-ups. It also resets
        the error flag back to default
        :param args:
        :return No return value:
        """
        if self.__error_no_err():
            pass

        if self.__error_wrong_id():
            self.__error = self.ErrorCode.NO_ERR
            wrong_id_err_txt = f'The package identification {self.pkg_id_entry.get()}, is incorrect.\n' \
                               'Please check the number and try again.'
            wrong_id_msg = CTkMessagebox(title="Invalid Entry", message=wrong_id_err_txt,
                                         icon="warning", option_1="Retry", cancel_button="cross")
            if wrong_id_msg.get() == "Retry":
                wrong_id_msg.destroy()

        if self.__error_invalid_time():
            self.__error = self.ErrorCode.NO_ERR
            invalid_time_txt = f'The time value {args} that you entered is formatted incorrectly.\n' \
                               'Please check that the format is "HH:MM", and try again.'
            invalid_time_msg = CTkMessagebox(title="Invalid Entry", message=invalid_time_txt, icon="warning",
                                             option_1="Ok", cancel_button="cross")

            if invalid_time_msg.get() == "Ok":
                invalid_time_msg.destroy()

    def time_entry_popup(self) -> str or None:
        """
        Creates a popup that accepts time as an input. The purpose is to allow a user to
        look the package deliver status for all packages at a chosen time.
        The method also checks to see if the user chooses to provide an input.
        IF the user enters an invalid time format, the method will also raise an error message
        :return:
        """
        time_input = ctk.CTkInputDialog(text='Enter a time (HH:MM) value if you would like to see a specific snapshot\n'
                                             'Or close the window and the current system time will be used.',
                                        title='Package Status Snapshot')
        usr_time = time_input.get_input()
        if usr_time is None:
            return None
        elif re.match(r'(?i)(\d?\d):(\d\d)', str(usr_time)):
            return str(usr_time)
        else:
            self.__error = self.ErrorCode.INVALID_TIME
            self.raise_error(usr_time)

    def display_all_pkgs_event(self):  # Explicitly called by pressing the display_all_pkgs button
        """
        This method is initialized when the 'show all packages' (display_all_pkgs) button is pressed.
        After initialization the method builds a stylized table using pandas and pandastable
        The data is pulled, sorted, and refreshed by the 'pkg_data_refresh' method
        Pandas only provides a structure for displaying the information as a table.
        :param self:
        :return No return value:
        """
        if self.display_all_pkgs:
            self.pkg_data_refresh()
            self.textbox.delete("0.0", "200.0")
            pkgs_frame = ctk.CTkFrame(self, width=250)
            pkgs_frame.grid(row=0, rowspan=3, column=1, columnspan=3,
                            padx=(20, 20), pady=(20, 20), sticky="nsew")
            pkgs_frame = ctk.CTkFrame(self, width=250)
            pkgs_frame.grid(row=0, rowspan=3, column=1, columnspan=3,
                            padx=(20, 20), pady=(20, 20), sticky="nsew")
            pt = Table(pkgs_frame)
            pkgs_df = pd.DataFrame(self.ordered_pkg_lst, columns=['Package ID', 'Address', 'City',
                                                                  'State', 'Postal Code', 'Deadline'])
            pkgs_table = pt = Table(pkgs_frame, dataframe=pkgs_df,
                                    showtoolbar=False, showstatusbar=False)

            config.apply_options(self.options, pkgs_table)
            pt.show()

    def user_txt_search_event(self):
        """
        This method is used by the 'submit' button on the bottom of the sidebar within the gui
        When initialized it validates the data provided by the user.
        If there are no issues, the event to return the request data is initialized.
        If there is an issue, the user is shown an error message and can retry their input
        :return No return value:
        """
        if self.string_input_button:
            pkg_id_input = self.pkg_id_entry.get()
            time_input = self.time_entry.get()
            if (pkg_id_input.isdigit()
                    and re.match(r'(?i)(\d?\d):(\d\d)', time_input)
                    and int(pkg_id_input) in self.pkg_index):

                self.pkg_info_return_event(int(pkg_id_input), str(time_input))
            else:
                self.__error = self.ErrorCode.WRONG_ID
                self.raise_error()

    def pkg_info_return_event(self, pkg_id: int, time: str):  # Uses the get method in the PkgObjects class
        """
        This method is used to structure and display data requested by the user. It creates
        textboxes for the visualization then adds string text to it. It accesses the requested data
        directly from the Hashtable storing the package data using the built-in 'get' method
        :param pkg_id: int:
        :param time: str:
        :return No return value:
        """
        time = deadline_to_minutes(time)
        pkg = self.pkgs.get_bucket(pkg_id)
        txt_out = (f'Package ID: {pkg.pkg_id}; Address: {pkg.address} {pkg.city}, {pkg.state} {pkg.postal_code}; '
                   f'Weight: {pkg.weight}; Deadline: {pkg.promise_format()}; Status: {pkg.get_pkg_status(time)}')

        self.textbox.delete("0.0", "200.0")
        textbox = ctk.CTkTextbox(self, width=250, font=ctk.CTkFont(family='Arial', size=15, weight="bold"))
        textbox.grid(row=0, rowspan=3, column=1, columnspan=3, padx=(20, 20), pady=(20, 20), sticky="nsew")
        textbox.insert('0.0', txt_out)

    def truck_info_request_event(self):
        """
        Similar to the 'pkg_info_return_event' method, this method access the list storing the trucks
        used to delviver packages. It then creates a very simple visualization and displays the specified
        truck attributes stored in the truck objects.
        :return No return value:
        """
        textbox = ctk.CTkTextbox(self, width=250, font=ctk.CTkFont(family='Arial', size=22, weight="bold"))
        textbox.grid(row=0, rowspan=3, column=1, columnspan=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        for truck in self.trucks:
            truck_txt = f'Truck number {truck.truck} traveled a total of {truck.total_miles} miles.\n'
            textbox.insert('0.0', truck_txt)

    def pkg_status_request_event(self):
        """
        This method calls the 'pkg_data_refresh' method to ensure that it's using fresh data.
        It then provides a print out of all packages for a specified time. If no time is provided by the user
        then the current system time is used.
        :return No return value:
        """
        time = datetime.now()
        self.pkg_data_refresh()
        usr_time = self.time_entry_popup()
        if usr_time is not None:
            current_time = deadline_to_minutes(str(usr_time))
        else:
            current_time = deadline_to_minutes(str(time.strftime("%H:%M")))

        self.textbox.delete("0.0", "200.0")
        textbox = ctk.CTkTextbox(self, width=250, font=ctk.CTkFont(family='Arial', size=16),
                                 wrap=ctk.WORD)
        textbox.grid(row=0, rowspan=3, column=1, columnspan=3, padx=(20, 20), pady=(20, 20), sticky="nsew")
        textbox.configure(scrollbar_button_color="", scrollbar_button_hover_color="")

        for pkg in self.pkg_id_desc[::-1]:
            txt = f'{pkg[1].get_pkg_information(current_time)}.\n'
            txt = re.sub(r'\[\d+?;\d+?m', '', txt)
            textbox.insert('0.0', txt)


if __name__ == "__main__":
    app = App()
    app.mainloop()
