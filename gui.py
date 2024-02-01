import tkinter as tk
from tkinter import ttk, colorchooser
from tkinter import *
import json
from screeninfo import get_monitors
from PIL import Image, ImageTk
from main import composite_image

class XKCDBackgroundTool:
    def __init__(self, master):
        self.target_preview_size = (0,0)
        self.master = master
        self.master.title("XKCD Background Tool")

        # Set styles
        large_font_bold = ('Lucida', 18)
        large_font = ('Lucida', 18, 'bold')

        style = ttk.Style()

        # Apply styles to all widgets
        style.configure("TLabel", font=large_font_bold)
        style.configure("TButton", font=large_font_bold)
        style.configure("TCheckbutton", font=large_font_bold)
        style.configure("TRadiobutton", font=('Lucida', 14, 'bold'))

        # Mode selection (Radio buttons)
        self.mode_label = ttk.Label(master, text="Select Mode:")
        self.mode_var = tk.StringVar(value="Random")
        self.random_radio = ttk.Radiobutton(master, text="Random", variable=self.mode_var, value="Random")
        self.latest_radio = ttk.Radiobutton(master, text="Latest", variable=self.mode_var, value="Latest")

        # Run option selection (Radio buttons)
        self.run_label = ttk.Label(master, text="Select Run Option:")
        self.run_var = tk.StringVar(value="Run on Startup")
        self.startup_radio = ttk.Radiobutton(master, text="Run on Startup", variable=self.run_var,
                                             value="Run on Startup")
        self.everyday_radio = ttk.Radiobutton(master, text="Run Every Day", variable=self.run_var,
                                              value="Run Every Day")

        # Background color selection
        self.color_label = ttk.Label(master, text="Select Background Color:")
        self.color_var = tk.StringVar(value="#FFFFFF")
        self.color_button = ttk.Button(master, text="Choose Color", command=self.choose_color)

        # Toggle drop shadow
        self.shadow_var = tk.BooleanVar(value=False)
        self.shadow_checkbox = ttk.Checkbutton(master, text="Enable Drop Shadow?", variable=self.shadow_var)

        # Toggle for displaying alt text
        self.alt_text_var = tk.BooleanVar(value=True)
        self.alt_text_checkbox = ttk.Checkbutton(master, text="Display Alt Text", variable=self.alt_text_var)

        # Toggle for displaying title
        self.title_var = tk.BooleanVar(value=True)
        self.title_checkbox = ttk.Checkbutton(master, text="Display Title", variable=self.title_var)

        # Regenerate the preview
        self.update_image()

        # Preview section
        self.preview_label = tk.Label(master, text="Preview:", font=large_font)
        self.image_path = "preview.png"  # Replace with the actual path to your image
        self.image = tk.PhotoImage(file=self.image_path)
        self.preview_image = tk.Label(master, image=self.image, relief="solid", width=self.target_preview_size[0], height=self.target_preview_size[1])

        # Create and place widgets on the grid
        self.mode_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.random_radio.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.latest_radio.grid(row=0, column=2, padx=10, pady=5, sticky="w")

        self.run_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.startup_radio.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.everyday_radio.grid(row=1, column=2, padx=10, pady=5, sticky="w")

        self.color_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.color_button.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.shadow_checkbox.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        self.alt_text_checkbox.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        self.title_checkbox.grid(row=3, column=2, padx=10, pady=5, sticky="w")

        self.preview_label.grid(row=4, column=0, columnspan=3, padx=10, pady=5, sticky="w")
        self.preview_image.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

        # Add traces to variables to call the update function on change
        self.mode_var.trace_add("write", self.update)
        self.run_var.trace_add("write", self.update)
        self.color_var.trace_add("write", self.update)
        self.shadow_var.trace_add("write", self.update)
        self.alt_text_var.trace_add("write", self.update)
        self.title_var.trace_add("write", self.update)

    def choose_color(self):
        color_code = colorchooser.askcolor()[1]
        if color_code:
            self.color_var.set(color_code)

    def update_image(self):
        # Re-render
        composite_image("comic.png",)

        # Scale the image to fit in the preview
        res = get_monitors()[0]
        res = res.height / res.width
        pw = 500
        self.target_preview_size = (pw, round(pw * res))

        original_image = Image.open("combined_wallpaper.png")
        resized_image = original_image.resize(self.target_preview_size, Image.LANCZOS)
        resized_image.save("preview.png")

    def update(self, *args):
        config_data = {
            "mode": self.mode_var.get(),
            "run": self.run_var.get(),
            "color": self.color_var.get(),
            "shadow": self.shadow_var.get(),
            "alt_text": self.alt_text_var.get(),
            "title": self.title_var.get()
        }

        # Save results
        with open("config.json", "w") as json_file:
            json.dump(config_data, json_file)

if __name__ == "__main__":
    root = tk.Tk()
    app = XKCDBackgroundTool(root)
    root.mainloop()