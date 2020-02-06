import json
import logging
import os
import re
import sys

import dotenv
import requests
from PIL import Image

try:
    from . import picture_uploader
except ImportError:
    import picture_uploader


class ConfigFile():
    """Class for working with json config file
    """

    def __init__(self, name='config.json'):

        self.name = name

        if os.access(self.name, os.F_OK):
            self.load()
        else:
            self.json = {'last_id': 0}
            self.save()

    @property
    def last_id(self):
        """Last seen update ID

        Returns:
            int -- ID
        """

        loaded = self.json.get('last_id', 0)

        if type(loaded) != int:

            logging.warning("Invalid last_id value, overwriting with 0")
            self.last_id = 0
            return 0

        else:
            return loaded

    @last_id.setter
    def last_id(self, v: int):

        self.json['last_id'] = v
        self.save()

    def load(self):
        """Load configs from the file
        """

        with open(self.name, 'rt') as f:
            self.json = json.load(f)

    def save(self):
        """Dump configs into JSON file
        """

        with open(self.name, 'wt') as f:
            json.dump(self.json, f, indent=4)


# TODO put all requests in one method
class TJbot():
    """Main class for TJbot

    Raises:
        RuntimeError: something went wrong with API
    """

    base_url = 'https://api.tjournal.ru/v1.8'

    # TODO generate with account name and id
    regex = r'^\[\@293569\|БотЛебедев\]\,?\s*(.*)'

    def __init__(self, token: str):

        if token is None:
            raise RuntimeError("Token not provided")

        self.token = token
        self.config = ConfigFile()

        self.headers = {
            'X-Device-Token': self.token
        }

    # TODO osnova returns 400, using imgur workaround. fix?
    def upload_image(self, img: Image):
        """Upload picture to Osnova through imgur

        Arguments:
            img {Image} -- Image to upload

        Raises:
            RuntimeError: Failed API requests

        Returns:
            result -- Osnova magic json for attachment
        """

        url = picture_uploader.upload_picture_imgur(img)

        logging.debug("Uploaded to imgur, reuploading to Osnova")

        r = requests.post(
            self.base_url + '/uploader/extract',
            headers=self.headers,
            data={'url': url}
        )

        if r.status_code != 200:
            raise RuntimeError("Osnova broken: failed to upload image")

        logging.debug("Picture uploaded to Osnova")

        return r.json()['result']

    # TODO not working in Osnova?
    # This is here with the hope of fixed API
    def mark_notification_read(self, nid: int):
        """Marks notification as read. Not working for some reason.

        Arguments:
            nid {int} -- notification ID
        """

        requests.post(
            self.base_url + f'/user/me/updates/read/{nid}',
            headers=self.headers
        )

    def parse_mention(self, mention: str):
        """Parses the mention and removes the mention itself



        Arguments:
            mention {str} -- Message with the mention

        Returns:
            str -- Message without mention
        """

        query = re.match(self.regex, mention)

        return query

    def get_comment_url_contents(self, url: str):
        """Gets the comment in the url

        Arguments:
            url {str} -- URL to the comment

        Raises:
            RuntimeError: Error when querying API

        Returns:
            comment -- Comment object as dict
        """

        r = requests.get(
            self.base_url + '/locate',
            headers=self.headers,
            params={'url': url}
        )

        if r.status_code != 200:
            raise RuntimeError("Osnova is broken: cannot get comment")

        res = r.json()['result']

        if res['type'] != 'comment':
            raise RuntimeError("Weirdness from Osnova")

        return res['data']

    def reply(self, comment, attach):
        """Reply to specified comment with the specified image

        Arguments:
            comment {comment} -- Comment object from API
            attach {attachment} -- raw dict object from Osnova

        Raises:
            RuntimeError: API error
        """

        pid = comment['entry']['id']
        cid = comment['id']

        r = requests.post(
            self.base_url + '/comment/add',
            headers=self.headers,
            data={
                'id': pid,
                'text': '',
                'reply_to': cid,
                'attachments': json.dumps(attach)
            }
        )

        logging.debug(f"Reply API returned {r.status_code}")

        if r.status_code != 200:
            raise RuntimeError("Osnova broken: could not post comment")

    def poll_mentions(self):
        """Yields all mentions, if there are any

        Raises:
            RuntimeError: API query error

        Yields:
            mention -- A mention object
        """

        logging.debug("Geting notifications")

        r = requests.get(
            self.base_url + '/user/me/updates',
            headers=self.headers
        )

        logging.debug(f"Updates returned {r.status_code}")
        if r.status_code == 200:

            notifications = r.json().get('result')

            if notifications is None:
                raise RuntimeError('Osnova is broken: result is none')

            logging.debug(f"Got {len(notifications)} notifications")

            if self.config.last_id == 0:
                logging.info("Last id not recorded, doing a dry run")

            # Generator magic
            if len(notifications) == 0:
                return []

            # To be written into config
            new_last = 0

            for n in notifications:

                new_last = max(new_last, n['id'])

                # Magic number for mentions
                # Osnova last_id not working
                if n['type'] == 1024 and n['id'] > self.config.last_id:
                    logging.debug(f"Found mention from {n['users'][0]['name']}")
                    logging.debug(f"{n['id']} > {self.config.last_id}")

                    comment = self.get_comment_url_contents(n['url'])

                    if self.config.last_id != 0:
                        yield comment

                self.mark_notification_read(n['id'])

            self.config.last_id = new_last


if __name__ == "__main__":

    sys.path.append(os.path.abspath('../'))

    from liblebedev.mememaker import create_lebedev

    logging.basicConfig(
        level=logging.DEBUG
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    dotenv.load_dotenv('../auth.env')

    bot = TJbot(os.environ.get("TJ_TOKEN"))

    for comment in bot.poll_mentions():

        msg_raw = comment['text']
        query = bot.parse_mention(msg_raw)

        if query:
            msg = query.group(1)

            if msg:
                meme = create_lebedev(msg)
            else:
                meme = create_lebedev('умер')

            attach = bot.upload_image(meme)
            bot.reply(comment, attach)
