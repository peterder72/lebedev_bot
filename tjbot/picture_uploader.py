import io
import os
import logging

import dotenv
import requests
from PIL import Image


def upload_picture_imgur(img: Image):

    dotenv.load_dotenv('auth.env')

    client_imgur = os.environ.get('IMGUR_CLIENT')

    if client_imgur is None:
        raise RuntimeError("No imgur token specified")

    with io.BytesIO() as output:
        img.save(output, format="JPEG")
        img_bin = output.getvalue()

    logging.debug("Uploading picture to imgur")
    r = requests.post(
        'https://api.imgur.com/3/upload',
        headers={
            'Authorization': f'Client-ID {client_imgur}'
        },
        data={
            'image': img_bin,
            'type': 'file'
        }
    )

    if r.status_code != 200:
        raise RuntimeError("Failed to upload to imgur")

    return r.json()['data']['link']
