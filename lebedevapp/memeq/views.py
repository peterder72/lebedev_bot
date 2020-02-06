import hashlib
import os

from flask import abort, request, send_file
from PIL import Image

from liblebedev.mememaker import create_lebedev

from . import memeq


@memeq.route('/img/<filename>')
def pic(filename):
    """Serve picture by the filename
    
    Arguments:
        filename {str} -- Picture name
    """

    # Security measure. Only gets filename.
    # Though I wasn't able to exploit path traversing without this,
    # it's still a good practice.
    path = os.path.abspath('cache' + os.sep + filename)
    filename_san = path.split(os.sep)[-1]

    if not os.access('cache' + os.sep + filename_san, os.F_OK):
        abort(404)

    return send_file(os.getcwd() + os.sep + 'cache' + os.sep + filename_san)


@memeq.route("/generate", methods=['POST'])
def generate_new():
    """Generate new picture
    """

    if not request.json:
        abort(400)

    phrase = request.json.get('phrase')

    if phrase is None:
        abort(400)

    phrase_hash = hashlib.md5(phrase.encode())

    # Use cache if possible
    if not os.access('cache' + os.sep + phrase_hash.hexdigest() + '.jpeg', os.F_OK):
        meme = create_lebedev(phrase)

        # Generate thumbnail with a black frame for TG.
        # Couldn't see Telegram actually using this thumbnail,
        # but since it's required in the API call, I believe
        # that one day it will be used
        size = (max(meme.size) // 2, max(meme.size) // 2)

        thumbnail = meme.copy()
        thumbnail.thumbnail((meme.size[0] // 2, meme.size[1] // 2), Image.ANTIALIAS)
        background = Image.new('RGB', size, (0, 0, 0))
        
        # Paste picure to the middle
        background.paste(
            thumbnail, (0, (size[1] - thumbnail.size[1]) // 2)
        )

        # Save everything to the cache
        meme.save('cache/{}.jpeg'.format(phrase_hash.hexdigest()), 'JPEG')
        background.save('cache/{}.thm'.format(phrase_hash.hexdigest()), 'JPEG')

    return phrase_hash.hexdigest()
