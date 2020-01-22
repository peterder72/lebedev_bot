from PIL import Image, ImageDraw, ImageFont


def create_lebedev(verb: str) -> Image:

    template_phrase = ((f'Ну {verb}'), (f'и {verb}'))

    base = Image.open("img/lebedev_base.jpeg")

    draw = ImageDraw.Draw(base)
    font = ImageFont.truetype("fonts/colibri.ttf", size=45)
    color = '#ffffff'

    y_offset = 30

    text = ' '.join(template_phrase)

    size = draw.multiline_textsize(text, font=font, spacing=4)

    if size[0] > base.size[0]:
        text = '\n'.join(template_phrase)
        size = draw.multiline_textsize(text, font=font, spacing=8)

        if size[0] > base.size[0]:
            googly_eyes = Image.open("img/googly_eyes.png")
            base.paste(googly_eyes, (0, 0), mask=googly_eyes)

    x_coord = (base.size[0] - size[0]) // 2

    coord = (x_coord, base.size[1] - size[1] - y_offset)

    draw.multiline_text(coord, text, fill=color, font=font, spacing=8)

    return base


if __name__ == '__main__':

    out = create_lebedev("умер")
    out.save('img/meme.png')
