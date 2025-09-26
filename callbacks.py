# callbacks.py
import dearpygui.dearpygui as dpg

def say_hello(sender, app_data, user_data):
    """Updates the text widget with a greeting message."""
    dpg.set_value("output_text", "Hello from Dear PyGui!")
