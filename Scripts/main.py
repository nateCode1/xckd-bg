import textwrap
import requests
from bs4 import BeautifulSoup as bs
import ctypes
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import os
from screeninfo import get_monitors
import json
import schedule
import time

def add_tuples(tup1, tup2):
    return tuple([tup1[i] + tup2[i] for i in range(len(tup1))])


def draw_text(text, size, ypos, fill_color, background, align_right=False):
    # Create a drawing object
    draw = ImageDraw.Draw(background)

    # Load a font
    font = ImageFont.truetype("../Fonts/LucidaSansDemiBold.ttf", size)

    # Determine the characters per line
    letter_size = draw.textbbox((0, 0), 'A', font)
    max_line_length = background.width // (letter_size[2] * 0.9)

    wrapped_text = textwrap.fill(text, width=max_line_length)

    # Calculate the width and height of the text
    text_size = draw.textbbox((0, 0), wrapped_text, font)

    # Calculate the position to center the text
    x = 8 if align_right else (background.width - text_size[0]) // 2 - text_size[2] // 2
    y = ypos  # (background.height - text_size[1]) // 2

    # Add text to the image
    # draw.text((x, y), text, font=font, fill=(0, 0, 0), align="center")
    draw.multiline_text((x, y), wrapped_text, font=font, fill=fill_color, align="center")


def color_from_hex(hex_string):
    hex_string = hex_string.lstrip('#')

    # Use int function with base 16 to convert hex to integer
    r = int(hex_string[0:2], 16)
    g = int(hex_string[2:4], 16)
    b = int(hex_string[4:6], 16)

    # Return the 3-tuple of integers
    return r, g, b


def get_image():
    with open("../Data/config.json", 'r') as file:
        config = json.load(file)

    image_path = "../Images/comic.png"
    url = "https://xkcd.com/" if config['mode'] == 'Latest' else 'https://c.xkcd.com/random/comic/'
    r = requests.get(url)

    soup = bs(r.content, features="lxml")

    # Image
    images = soup.select('#comic img')
    images_url = images[0]['src']
    img_data = requests.get('https:' + images_url).content

    with open(image_path, 'wb') as handler:
        handler.write(img_data)

    # Metadata
    title = soup.select('#ctitle')[0].get_text()
    alt_text = images[0]['title']

    image_data = {
        'title': title,
        'alt_text': alt_text
    }

    with open("../Data/image_meta.json", 'w') as file:
        json.dump(image_data, file, indent=2)


def composite_image(max_img_width_pct=0.9, max_img_height_pct=0.7):
    image_path = "../Images/comic.png"

    with open("../Data/config.json", 'r') as file:
        config = json.load(file)

    # Open the original image
    original_image = Image.open(image_path)

    # Get monitor size
    target_size = get_monitors()[0]  # gets primary display

    # Resize the image to fit the specified dimensions
    image_target_size = (target_size.width * max_img_width_pct, target_size.height * max_img_height_pct)

    image_scale_factor = min(image_target_size[0] / original_image.width, image_target_size[1] / original_image.height)

    resized_image = original_image.resize((round(original_image.width * image_scale_factor), round(original_image.height * image_scale_factor)), Image.LANCZOS)

    # Create a blank white image with the specified resolution
    background = Image.new('RGBA', (target_size.width, target_size.height), color_from_hex(config["color"]))

    # Image offset on the background
    im_offset = ((target_size.width - resized_image.width) // 2,
                 (target_size.height - resized_image.height) // 2 + 50)

    # Do shadow
    if config['shadow']:
        shadow_offset = (0, 15)
        shadow_opacity = 150
        blur_radius = 25

        shadow = Image.new('RGBA', background.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(shadow)

        # Update the shadow offset to be in the right positon on the bg
        shadow_offset = add_tuples(shadow_offset, im_offset)
        draw.polygon([shadow_offset,
                      (resized_image.width + shadow_offset[0], shadow_offset[1]),
                      (resized_image.width + shadow_offset[0], resized_image.height + shadow_offset[1]),
                      (shadow_offset[0], resized_image.height + shadow_offset[1])],
                     fill=color_from_hex(config["text_color"]) + (shadow_opacity, ))

        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        background = Image.alpha_composite(background, shadow)

    # Write Attribution
    draw_text("Randall Munroe - xkcd.com", 20, 8, color_from_hex(config["text_color"]), background, align_right=True)

    # Write image metadata
    if config["alt_text"] or config["title"]:
        # Load the JSON data from the file
        with open("../Data/image_meta.json", 'r') as file:
            image_meta = json.load(file)

        if config["title"]:
            draw_text(image_meta["title"], 80, 25, color_from_hex(config["text_color"]), background)

        if config["alt_text"] and not image_meta["title"] == image_meta["alt_text"]:
            draw_text(image_meta["alt_text"], 20, 125, color_from_hex(config["text_color"]), background)

    # Paste the resized image onto the white background
    background.paste(resized_image, im_offset)

    # Save the combined image
    background.save("../Images/combined_wallpaper.png")

def set_background():
    # --- SET BG
    SPI_SETDESKWALLPAPER = 0x0014

    # Set the system background
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, os.path.abspath(
        "../Images/combined_wallpaper.png"), 3)


def update():
    print("Starting...")
    get_image()
    print("Image retrieved")
    composite_image()
    print("Background generated")
    set_background()
    print("Done.")


if __name__ == "__main__":
    update()

    # schedule.every(5).seconds.do(update)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)