# main.py
import dearpygui.dearpygui as dpg
from ui import create_main_window

def main():
    dpg.create_context()
    create_main_window()

    dpg.create_viewport(title="My Dear PyGui App", width=500, height=300)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()
