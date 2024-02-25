import dearpygui.dearpygui as dpg
from download_manager import *

dm = DownloadManager(4)

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
            dpg.add_table_column(width_stretch=False)
            # Add the updated download list
            index=0
            for download in download_list:
                index+=1
                with dpg.table_row():
                    if download.status == Status.NOT_STARTED:
                        dpg.add_button(label="Start",width=50)
                    elif download.status == Status.DOWNLOADING:
                        dpg.add_button(label="Pause",width=50)
                    dpg.add_text(tag="filename-"+str(index),default_value=download.file_name)
                    dpg.add_text(tag="size-"+str(index),default_value=download.get_formatted_total_size())
                    str_progress = '%.1f' % download.get_progress()
                    dpg.add_progress_bar(overlay=str_progress, width=100, height=20, default_value=float(str_progress))
                    with dpg.tooltip(parent="filename-"+str(index)):
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
# Song
# https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3
# Public video
# http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4
# Public document
# https://sample-videos.com/doc/Sample-doc-file-100kb.doc

