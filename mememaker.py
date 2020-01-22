from PIL import Image, ImageDraw, ImageFont


def create_lebedev(verb: str) -> Image:

    template = f'Ну {verb} и {verb}'

    base = Image.open("img/lebedev_base.jpeg")

    draw = ImageDraw.Draw(base)
    font = ImageFont.truetype("fonts/colibri.ttf", size=45)
    color = '#ffffff'

    y_offset = 30

    size = draw.multiline_textsize(template, font=font, spacing=4)

    if size[0] > base.size[0]:
        template = '\n'.join(
            [
                ' '.join(template.split(' ')[:2]),
                ' '.join(template.split(' ')[2:])
            ]
        )
        size = draw.multiline_textsize(template, font=font, spacing=8)

    x_coord = (base.size[0] - size[0]) // 2

    coord = (x_coord, base.size[1] - size[1] - y_offset)

    draw.multiline_text(coord, template, fill=color, font=font, spacing=4)

    return base


if __name__ == '__main__':

    out = create_lebedev("умер")
    out.save('img/meme.png')
