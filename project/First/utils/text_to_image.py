import os.path
import textwrap
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from First.settings import BASE_DIR


def get_image_dimensions(text, font, border):
    lines = textwrap.wrap(text, width=40)
    image_height = 0
    image_width = 0
    for line in lines:
        line_width, line_height = font.getsize(line)
        image_width = max(image_width, line_width)
        image_height += line_height
    image_width += 2 * border
    image_height += 2 * border
    return image_width, image_height


def create_image_template(image_width, image_height, border):
    image = Image.new('RGB', (image_width, image_height), color=(220, 210, 200))
    draw = ImageDraw.Draw(image)
    draw.rectangle(((border / 5, border / 5), (image_width - border / 5, image_height - border / 5)),
                   fill=(40, 30, 20))
    draw.rectangle(((border / 3, border / 3), (image_width - border / 3, image_height - border / 3)),
                   fill=(220, 210, 200))
    return image


def text_to_image(text, saving_path, border=40):
    font = ImageFont.truetype(os.path.join(BASE_DIR, 'utils/fonts/Vazir.ttf'), 30)
    image_width, image_height = get_image_dimensions(text, font, border)
    image = create_image_template(image_width, image_height, border)
    lines = textwrap.wrap(text, width=40)
    draw = ImageDraw.Draw(image)
    y = border
    for line in lines:
        line_width, line_height = font.getsize(line)
        draw.text(((image_width - line_width) / 2, y), line, fill=(40, 30, 20), font=font)
        y += line_height
    image.save(saving_path)
