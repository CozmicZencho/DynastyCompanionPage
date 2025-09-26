# ui.py
import dearpygui.dearpygui as dpg
from callbacks import say_hello

def create_main_window():
    """Creates the main application window with UI elements."""
    with dpg.window(label="My Example App", width=400, height=200):
        dpg.add_text("Press the button to say hello:", tag="output_text")
        dpg.add_button(label="Click Me", callback=say_hello)
