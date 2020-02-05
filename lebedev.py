import dotenv
import logging
from tjbot import TJbot
from mememaker import create_lebedev
import os
from time import sleep

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.DEBUG
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    dotenv.load_dotenv('auth.env')

    if os.environ.get("TJ_TOKEN") is None:
        raise RuntimeError("Osnova token not specified")

    bot = TJbot(os.environ.get("TJ_TOKEN"))

    # Main bot loop
    try:
        while True:

            for comment in bot.poll_mentions():

                msg_raw = comment['text']
                query = bot.parse_mention(msg_raw)

                if query:

                    msg = query.group(1)

                    if msg:
                        # Take only the last word
                        if len(msg.split(' ')) > 1:
                            msg = msg.split(' ')[-1]
                        meme = create_lebedev(msg)
                    else:
                        # If mention empty, post classical variant
                        meme = create_lebedev('умер')

                    # Attach and reply
                    try:
                        attach = bot.upload_image(meme)
                        bot.reply(comment, attach)
                    except RuntimeError:
                        logging.error("Skipping the response")
                        continue

            logging.debug("Sleeping")

            sleep(10)

    # Only for logging purposes
    except Exception as e:
        logging.critical(f"Bot crashed: {type(e).__name__} - {e}")
        raise e
