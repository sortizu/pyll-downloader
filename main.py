import dearpygui.dearpygui as dpg

dpg.create_context()

with dpg.window(label="Example Window"):
    dpg.add_input_text(label="URL FILE", default_value="Quick brown fox")

dpg.create_viewport(title='Custom Title', width=600, height=200)
dpg.setup_dearpygui()

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()