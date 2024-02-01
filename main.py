import requests
from bs4 import BeautifulSoup as bs
import ctypes
from PIL import Image, ImageDraw, ImageFilter
import os
from screeninfo import get_monitors


def add_tuples(tup1, tup2):
    return tuple([tup1[i] + tup2[i] for i in range(len(tup1))])


def get_image(image_path):
    r = requests.get('https://c.xkcd.com/random/comic/')

    soup = bs(r.content, features="lxml")
    images = soup.select('#comic img')
    images_url = images[0]['src']
    img_data = requests.get('https:' + images_url).content

    with open(image_path, 'wb') as handler:
        handler.write(img_data)


def composite_image(image_path, max_img_width_pct=0.9, max_img_height_pct=0.75):
    # Open the original image
    original_image = Image.open(image_path)

    # Get monitor size
    target_size = get_monitors()[0] #gets primary display

    # Resize the image to fit the specified dimensions
    image_target_size = (target_size.width * max_img_width_pct, target_size.height * max_img_height_pct)

    image_scale_factor = min(image_target_size[0] / original_image.width, image_target_size[1] / original_image.height)

    resized_image = original_image.resize((round(original_image.width * image_scale_factor), round(original_image.height * image_scale_factor)), Image.LANCZOS)

    # Create a blank white image with the specified resolution
    background = Image.new('RGB', (target_size.width, target_size.height), (235, 235, 235))

    # Image offset on the background
    im_offset = ((target_size.width - resized_image.width) // 2, (target_size.height - resized_image.height) // 2)

    # Do shadow
    shadow_offset = (0,15)
    shadow_opacity = 150
    blur_radius = 40

    shadow = Image.new('RGBA', background.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    #update the shadow offset to be in the right positon on the bg
    shadow_offset = add_tuples(shadow_offset, im_offset)
    draw.polygon([shadow_offset,
                  (resized_image.width + shadow_offset[0], shadow_offset[1]),
                  (resized_image.width + shadow_offset[0], resized_image.height + shadow_offset[1]),
                  (shadow_offset[0], resized_image.height + shadow_offset[1])],
                 fill=(1, 0, 2, shadow_opacity))

    # for i in range(5):
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    background = Image.alpha_composite(background.convert('RGBA'), shadow)

    # Paste the resized & shadowed image onto the white background
    background.paste(resized_image, im_offset)

    # Save the combined image
    combined_image_path = "combined_wallpaper.png"
    background.save(combined_image_path)

def set_background():
    # --- SET BG
    SPI_SETDESKWALLPAPER = 0x0014

    # Set the system background
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, os.path.abspath(combined_image_path), 3)


if __name__ == "__main__":
    get_image("comic.png")

    composite_image("comic.png")
    set_background()