from PIL import Image, ImageDraw, ImageFont
import os


def create_lebedev(verb: str) -> Image:

    basedir = os.path.dirname(os.path.abspath(__file__)) + os.sep

    template_phrase = ((f'Ну {verb}'), (f'и {verb}'))

    base = Image.open(basedir + "img/lebedev_base.jpeg")

    if verb:

        # Magic setup
        draw = ImageDraw.Draw(base)
        font = ImageFont.truetype(basedir + "fonts/colibri.ttf", size=45)
        color = '#ffffff'

        y_offset = 30

        text = ' '.join(template_phrase)

        size = draw.multiline_textsize(text, font=font, spacing=4)

        # If picture cannot fit the text
        if size[0] > base.size[0]:
            # Make the text multiline
            text = '\n'.join(template_phrase)
            size = draw.multiline_textsize(text, font=font, spacing=8)

            # If still doesn't fit...
            if size[0] > base.size[0]:
                # Make Lebedev's eyes googly!
                googly_eyes = Image.open(basedir + "img/googly_eyes.png")
                base.paste(googly_eyes, (0, 0), mask=googly_eyes)

        # Calculate x coordinate, so that the
        # text is in the middle
        x_coord = (base.size[0] - size[0]) // 2

        coord = (x_coord, base.size[1] - size[1] - y_offset)

        # Draw text
        draw.multiline_text(coord, text, fill=color, font=font, spacing=8)

    return base


if __name__ == '__main__':

    out = create_lebedev("умер")
    out.save('img/meme.png')
