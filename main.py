import dearpygui.dearpygui as dpg
import download_manager as dwm

dm = dwm.DownloadManager(4)

def download_all(sender):
    dm.download_all()

# This method is called when the user clicks the "Add" button
def add_url(sender):
    url = dpg.get_value("url")
    # Create a new download object and add it to the download list
    if url != '':
        dm.add_download(url, "", "")
        dpg.set_value("url", "")

def update_download_list(sender, app_data):
    # Clear the table
    dpg.delete_item("download-list", children_only=True)
    download_list = dm.get_download_list()
    if len(download_list) > 0:
        with dpg.table(header_row=False,parent="download-list"):
            dpg.add_table_column(width_stretch=False)
            dpg.add_table_column(width_stretch=True)
            dpg.add_table_column(width_stretch=False)
            # Add the updated download list
            index=0
            for download in download_list:
                index+=1
                with dpg.table_row():
                    if download.status == dwn.Status.NOT_STARTED:
                        dpg.add_button(label="Start",width=100)
                    elif download.status == dwn.Status.DOWNLOADING:
                        dpg.add_button(label="Pause",width=100)
                    dpg.add_text(tag="url-"+str(index),default_value=download.url)
                    dpg.add_progress_bar(overlay=f"{download.progress}%", width=100)
                    with dpg.tooltip(parent="url-"+str(index)):
                        dpg.add_text(download.url)


dpg.create_context()

with dpg.window(tag="Primary Window", no_resize=True):
    with dpg.group(tag="url-group",horizontal=True):
        dpg.add_input_text(tag="url", hint="URL del archivo", width=285)
        dpg.add_button(tag="add-url", label="+ Agregar", width=75, callback=add_url)
    # Add a group of buttons to manage all downloads, both buttons centered
    with dpg.group(tag="manage-group",horizontal=True):
        dpg.add_dummy(width=50)  # Add this line
        dpg.add_button(tag="start-all", label="Iniciar todos", width=120, callback=download_all)
        dpg.add_button(tag="pause-all", label="Pausar todos", width=120)
        dpg.add_dummy(width=50)  # Add this line
    # Add a child window to contain the download list
    with dpg.child(tag="download-list",width=-1, height=-1):
        pass



dpg.create_viewport(title='PyllDownloader', width=400, height=300, resizable=False)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
while dpg.is_dearpygui_running():
    update_download_list(None, None)
    dpg.render_dearpygui_frame()
dpg.destroy_context()

# Different urls to test the program
# PDF file
# https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf
# Google logo
# https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png
# Public song
# https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3

