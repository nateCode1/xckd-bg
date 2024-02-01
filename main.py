import requests
from bs4 import BeautifulSoup as bs
import ctypes
from PIL import Image, ImageDraw, ImageFilter
import os
from screeninfo import get_monitors

def getImage(image_path):
    r = requests.get('https://c.xkcd.com/random/comic/')

    soup = bs(r.content, features="lxml")
    images = soup.select('#comic img')
    images_url = images[0]['src']
    img_data = requests.get('https:' + images_url).content

    with open(image_path, 'wb') as handler:
        handler.write(img_data)


def resize_and_set(image_path, max_img_width_pct=0.9, max_img_height_pct=0.75):
    # Open the original image
    original_image = Image.open(image_path)

    #Get monitor size
    main_display = get_monitors()[0]
    target_width = main_display.width
    target_height = main_display.height

    # Resize the image to fit the specified dimensions
    image_target_width = target_width * max_img_width_pct
    image_target_height = target_height * max_img_height_pct

    image_scale_factor = min(image_target_width / original_image.width, image_target_height / original_image.height)

    resized_image = original_image.resize((round(original_image.width * image_scale_factor), round(original_image.height * image_scale_factor)), Image.LANCZOS)

    # Create a blank white image with the specified resolution
    background = Image.new('RGB', (target_width, target_height), (235, 235, 235))

    # Image offset on the background
    im_offset = ((target_width - resized_image.width) // 2, (target_height - resized_image.height) // 2)

    # Do shadow
    shadow_offset = 0
    shadow_opacity = 150
    blur_radius = 40

    shadow = Image.new('RGBA', background.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    draw.polygon([(shadow_offset + im_offset[0], shadow_offset + im_offset[1]),
                  (resized_image.width + im_offset[0] + shadow_offset, shadow_offset + im_offset[1]),
                  (resized_image.width + im_offset[0] + shadow_offset, resized_image.height + shadow_offset + im_offset[1]),
                  (shadow_offset + im_offset[0], resized_image.height + shadow_offset + im_offset[1])],
                 fill=(0, 0, 0, shadow_opacity))

    # for i in range(5):
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    background = Image.alpha_composite(background.convert('RGBA'), shadow)

    # Paste the resized & shadowed image onto the white background
    background.paste(resized_image, im_offset)

    # Save the combined image
    combined_image_path = "combined_wallpaper.png"
    background.save(combined_image_path)

    # --- SET BG
    SPI_SETDESKWALLPAPER = 0x0014

    # Set the system background
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, os.path.abspath(combined_image_path), 3)


if __name__ == "__main__":
    getImage("comic.png")

    resize_and_set("comic.png")