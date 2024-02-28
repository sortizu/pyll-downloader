from concurrent.futures import ProcessPoolExecutor
import threading
import time
import tkinter as tk
import customtkinter as ctk
from download import DownloadType
from download_manager import *

class Popup(ctk.CTkToplevel):
    """
    This class is a modal dialog that shows a message
    You can send the message as a parameter to the constructor
    """
    def __init__(self, message,*args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the position of the window to the center of the main window
        x = self.master.winfo_x() + self.master.winfo_width() // 2 - 75
        y = self.master.winfo_y() + self.master.winfo_height() // 2 - 57
        self.geometry("+{}+{}".format(x, y))
        self.resizable(False, False)
        # disable the main window
        self.transient(self.master)
        self.grab_set()
        self.focus_set()
        self.title("Alert")
        self.label = ctk.CTkLabel(self, text=message)
        self.label.pack(padx=20, pady=20)

class ErrorPopup(Popup):
    """
    This class is a modal dialog that shows an error message
    You can send the error message as a parameter to the constructor
    """
    def __init__(self, error_message,*args, **kwargs):
        super().__init__(error_message,*args, **kwargs)
        self.title("Error")
        self.button = ctk.CTkButton(self, text="OK", command=self.destroy)
        self.button.pack(pady=10,padx=10)




class DownloadItemGUI:
    """
    this class is a GUI representation of a download item, which contains the download control button, the filename label, the size label, the progress label and the progress bar
    """
    def __init__(self, download:Download, frame, index=0):
        self.download = download
        self.frame = frame
        self.index = index
        # Control button
        #self.control_button = ctk.CTkButton(self.frame, text="\u23F5", width=15, height=25,corner_radius=6)
        #self.control_button.grid(row=self.index, column=0, sticky="w", padx=5, pady=5)
        # Download type label
        self.download_type_label = ctk.CTkLabel(self.frame, text= str(download.download_type.name)[0:3],text_color="yellow")
        self.download_type_label.grid(row=self.index, column=0, sticky="w", padx=5, pady=5)
        # Filename label
        self.filename_label = ctk.CTkLabel(self.frame, text=download.file_name, width=50)
        self.filename_label.grid(row=self.index, column=1, sticky="ew", padx=(0,5), pady=5)
        # Size label
        self.size_label = ctk.CTkLabel(self.frame, text=download.get_formatted_total_size())
        self.size_label.grid(row=self.index, column=2, sticky="ew", padx=(10,15))
        str_progress = '%.1f' % download.get_progress()
        # Time label
        self.time_label = ctk.CTkLabel(self.frame, text="00:00:00",width=40)
        self.time_label.grid(row=self.index, column=3, sticky="e", padx=(0,5))
        # Progress label and progress bar
        self.progress_label = ctk.CTkLabel(self.frame, text=str_progress+"%",width=40)
        self.progress_label.grid(row=self.index, column=4, sticky="e")
        self.progress_bar = ctk.CTkProgressBar(self.frame, width=100,mode="determinate",orientation="horizontal")
        self.progress_bar.grid(row=self.index, column=5, sticky="ew", padx=(0,5))
        self.progress_bar.set(float(str_progress))
        # Delete and options buttons
        self.delete_button = ctk.CTkButton(self.frame, text="❌", width=15, height=25,corner_radius=6)
        self.delete_button.grid(row=self.index, column=6, sticky="e", padx=5, pady=5)
        #self.options_button = ctk.CTkButton(self.frame, text="⚙", width=15, height=25,corner_radius=6)
        #self.options_button.grid(row=self.index, column=6, sticky="e", padx=5, pady=5)
    def destroy(self):
        self.control_button.destroy()
        self.filename_label.destroy()
        self.size_label.destroy()
        self.progress_label.destroy()
        self.progress_bar.destroy()
        self.delete_button.destroy()
        self.options_button.destroy()

class App(ctk.CTk):
    """
    Main window of the application
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("PyllDownloader")
        self.geometry("600x325")
        self.resizable(False, False)
        
        self.main_frame = ctk.CTkFrame(self,fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.download_gui_list = []
        self.toplevel_window = None
        self.dw_list_lock = threading.Lock()
        self.main_thread_pool = ThreadPoolExecutor(max_workers=16)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.running=True
        # Download manager
        self.dm = DownloadManager(1)

        # URL widgets
        self.url_frame = ctk.CTkFrame(self.main_frame,fg_color="transparent")
        self.url_frame.grid(row=0, column=0, sticky="ew")
        self.url_frame.grid_columnconfigure(0, weight=1)
        self.url_entry = ctk.CTkEntry(self.url_frame, placeholder_text="Enter URL")
        self.url_entry.grid(row=0, column=0, columnspan=4, sticky="ew", padx=(0,5))
        self.url_add_button = ctk.CTkButton(self.url_frame, text="➕Add",width=30)
        self.perform_button = ctk.CTkButton(self.url_frame, text="🔍Perform",width=30)
        # Bind a lambda method that uses the thread pool to add the URL to the download manager
        self.url_add_button.configure(command=lambda: self.main_thread_pool.submit(self.add_url_cb))
        self.perform_button.configure(command=lambda: self.main_thread_pool.submit(self.perform_button_cb))
        self.url_add_button.grid(row=0, column=4, sticky="e", padx=(0,5))
        self.perform_button.grid(row=0, column=5)
        # Download buttons widgets
        self.buttons_frame = ctk.CTkFrame(self.main_frame,fg_color="transparent")
        self.buttons_frame.grid(row=1, column=0, sticky="ew", pady=(5,0))
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(1, weight=0)
        self.buttons_frame.grid_columnconfigure(2, weight=1)

        self.start_all_button = ctk.CTkButton(self.buttons_frame, text="▶ Start all",width=70,fg_color="green", command=self.download_all_cb)
        self.start_all_button.grid(row=0, column=0,sticky="e",padx=5)

        #self.pause_all_button = ctk.CTkButton(self.buttons_frame, text="⏸ Pause all",width=70, fg_color="orange")
        #self.pause_all_button.grid(row=0, column=1,padx=5)

        #self.cancel_all_button = ctk.CTkButton(self.buttons_frame, text="⏹ Stop all",width=70, fg_color="red")
        #self.cancel_all_button.grid(row=0, column=2,sticky="w",padx=5)
        # Download list widgets
        self.download_list_frame = ctk.CTkFrame(self.main_frame)
        self.download_list_frame.grid(row=2, column=0, sticky="nsew", pady=(5,0))
        self.download_list_frame.grid_columnconfigure(1, weight=1)
        # Start a thread to update the widgets
        self.main_thread_pool.submit(self.update_widgets)
        #thread = threading.Thread(target=self.update_widgets)
        #thread.start()
        #thread.join()

    def download_all_cb(self):
        """
        Callback for the start all button
        """
        self.dm.download_all()

    def add_url_cb(self):
        """
        Callback for the add URL button
        """
        url = self.url_entry.get()
        
        if not self.dm.is_valid_url(url):
            # Shows a modal dialog with the error message
            self.show_error_popup("Invalid URL")
            self.url_entry.delete(0, "end")
            return

        if self.dm.is_url_repeated(url):
            # Shows a modal dialog with the error message
            self.show_error_popup("URL already added")
            self.url_entry.delete(0, "end")
            return
        # Getting the index of the last download added
        self.show_popup("Adding download...")
        self.dm.add_download(url, "", "", DownloadType.SEQUENTIAL)
        self.add_download_item(self.dm.get_download_list()[-1])
        self.destroy_popup()

    def update_widgets(self):
        """
        Method to update the widgets in the main window
        This method is called using a different thread
        """
        while self.running:
            self.update_download_list()
            # Sleeps 120 times per second
            time.sleep(1/60)

    def update_download_list(self):
        """
        Updates the list of downloads in the GUI.
        This method is called by the update_widgets method (different thread)
        """
        if self.dw_list_lock.acquire(blocking=False):
            try:
                for download_item in self.download_gui_list:
                    #download_item.filename_label.config(text=download_item.download.file_name)
                    download_item.size_label.configure(text=download_item.download.get_formatted_total_size())
                    str_progress = '%.1f' % download_item.download.get_progress()
                    download_item.progress_label.configure(text=str_progress+"%")
                    download_item.progress_bar.set(float(str_progress)/100.0)
                    download_item.time_label.configure(text=download_item.download.get_formatted_download_time())
                    #download_item.control_button.config(command=download_item.download.toggle)
            except Exception as e:
                print(e)
            self.dw_list_lock.release()

    def show_error_popup(self, error_message:str):
        """
        Shows a modal dialog with an error message.
        The new modal dialog will grab focus and the input widgets will be disabled.
        This method uses top-level windows mentioned in the customtkinter documentation
        """
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ErrorPopup(error_message,self)  # create window if its None or destroyed
        else:
            self.toplevel_window.focus()  # if window exists focus it
    
    def show_popup(self, message:str):
        """
        Shows a modal dialog with a message.
        """
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = Popup(message,self)
        else:
            self.toplevel_window.focus()
    
    def destroy_popup(self):
        """
        Destroys the modal dialog
        """
        if self.toplevel_window is not None and self.toplevel_window.winfo_exists():
            self.toplevel_window.destroy()

    def delete_download_item(self, index):
        """
        Deletes a download item from the GUI and the download list in the download manager
        """
        self.dw_list_lock.acquire()
        self.download_gui_list[index].destroy()
        self.download_gui_list.pop(index)
        self.dm.get_download_list().pop(index)
        if len(self.download_gui_list)==0:
            self.dw_list_lock.release()
            return
        for i in range(index, len(self.download_gui_list)):
            self.download_gui_list[i].index = i
            self.download_gui_list[i].control_button.grid(row=i, column=0, sticky="w", padx=5, pady=5)
            self.download_gui_list[i].filename_label.grid(row=i, column=1, sticky="ew", padx=(0,5), pady=5)
            self.download_gui_list[i].size_label.grid(row=i, column=2, sticky="ew", padx=(10,15))
            self.download_gui_list[i].progress_label.grid(row=i, column=3, sticky="e")
            self.download_gui_list[i].progress_bar.grid(row=i, column=4, sticky="ew", padx=(0,5))
            self.download_gui_list[i].delete_button.grid(row=i, column=5, sticky="e", padx=5, pady=5)
            self.download_gui_list[i].delete_button.configure(command=lambda: self.main_thread_pool.submit(self.delete_download_item, self.download_gui_list[i].index))
            self.download_gui_list[i].options_button.grid(row=i, column=6, sticky="e", padx=5, pady=5)
        self.dw_list_lock.release()


    def perform_button_cb(self):
        """
        Callback for the perform button
        """
        
        url = self.url_entry.get()
        if not self.dm.is_valid_url(url):
            # Shows a modal dialog with the error message
            self.show_error_popup("Invalid URL")
            self.url_entry.delete(0, "end")
            return
        # if self.dm.is_url_repeated(url):
        #     # Shows a modal dialog with the error message
        #     self.show_error_popup("URL already added")
        #     self.url_entry.delete(0, "end")
        #     return
        num_evaluations = 3
        self.url_entry.delete(0, "end")
        for i in range(num_evaluations):
            self.dm.add_download(url, "", "", DownloadType.SEQUENTIAL)
            self.add_download_item(self.dm.get_download_list()[-1])
        for i in range(num_evaluations):
            self.dm.add_download(url, "", "", DownloadType.PARALLEL)
            self.add_download_item(self.dm.get_download_list()[-1])
        
        self.dm.download_all()
        # waits for all the downloads to finish
        while self.dm.get_download_list()[-1].status != Status.COMPLETED:
            time.sleep(1)
        self.show_metrics_popup(self.dm.get_metrics())


    def add_download_item(self, download:Download):
        """
        Adds a download item to the GUI
        """
        self.dw_list_lock.acquire()
        index = len(self.download_gui_list)
        download_item : DownloadItemGUI = DownloadItemGUI(download, self.download_list_frame, index)
        download_item.delete_button.configure(command=lambda: self.main_thread_pool.submit(self.delete_download_item, download_item.index))
        self.download_gui_list.append(download_item)
        self.dw_list_lock.release()

    def show_metrics_popup(self, metrics):
        """
        Shows a modal dialog with the metrics of the downloads
        """
        print(metrics)
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            average_sequential_time = f"Average sequential time: {metrics[0]:.2f}"
            average_parallel_time = f"Average parallel time: {metrics[1]:.2f}"
            speedup = f"Speedup: {metrics[2]:.2f}"
            efficiency = f"Efficiency: {metrics[3]:.2f}"
            metric_str = average_sequential_time + "\n\n" + average_parallel_time + "\n\n" + speedup + "\n\n" + efficiency
            self.toplevel_window = Popup(metric_str,self)
        else:
            self.toplevel_window.focus()

    def on_closing(self):
        """
        Method to be called when the main window is closed
        """
        self.destroy_popup()
        self.main_thread_pool.shutdown(wait=False)
        self.dm.terminate()
        self.destroy()
        self.running=False
        print("App closed")