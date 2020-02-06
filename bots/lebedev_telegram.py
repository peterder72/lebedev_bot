import logging
import os

import dotenv
import requests
import telegram
from telegram import InlineQueryResultPhoto
from telegram.ext import InlineQueryHandler, Updater, CommandHandler

host_lebedev = 'https://temp.osetr.su'


def print_help(update, context):
    """Respond with help message
    """

    msg = '''Я - <b>Бот Лебедев</b>. 
Я умею создавать картинки по шаблону с Артемием Лебедевым.
Картинки можно запрашивать двумя способами:

<b>1.</b> Добавить бота в групповой чат и упомянуть его с нужной фразой (и выбрать картинку из меню, естесвенно):
"<i>@lebedev72_bot умер"</i> отправит картинку, прикрепленную ниже.

<b>2.</b> Отправить мне сообщение с необходимой фразой c командой <i>"/gen умер"</i>.

<b>Приватность:</b>

Бот сохраняет картинки в <b>кэше</b> в целях оптимизации. Картинка в кэше живёт <i>два дня</i>, после чего удаляется.
Бот не сохраняет <b>никаких</b> личных данных и <b>не имеет доступа</b> к сообщениям в чате кроме тех, где он отмечен.

По всем вопросам/предложениям/багрепортам прошу к @peterder72

И да,исходник бота лежит <a href="https://github.com/peterder72/lebedev_bot">здесь</a>

Приятного пользования!'''

    context.bot.send_message(text=msg, chat_id=update.effective_chat.id, parse_mode=telegram.ParseMode.HTML)

    # TODO change for github link
    context.bot.send_photo(chat_id=update.effective_chat.id, photo='https://leonardo.osnova.io/9bdaf559-6a1a-1347-9592-b7a8a5663122/')


def standalone_lebedev(update, context):
    """Return lebedev picture as a message, not inline
    """

    query = " ".join(context.args)
    
    pic_hash = requests.post(
        host_lebedev + '/generate',
        json={'phrase': query}
    ).text

    full_url = host_lebedev + '/img/' + pic_hash + '.jpeg'

    context.bot.send_photo(chat_id=update.effective_chat.id, photo=full_url)


def inline_lebedev(update, context):
    """Return lebedev picture inline
    """

    # Phrase is stored here
    query = update.inline_query.query

    results = []

    # Getting picture hash from the server
    # More error handling?
    pic_hash = requests.post(
        host_lebedev + '/generate',
        json={'phrase': query}
    ).text

    # URLs for inline
    full_url = host_lebedev + '/img/' + pic_hash + '.jpeg'
    thumb_url = host_lebedev + '/img/' + pic_hash + '.thm'

    results.append(
        InlineQueryResultPhoto(
            id=0,
            photo_url=full_url,
            thumb_url=thumb_url
        )
    )

    update.inline_query.answer(results)


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.WARNING
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    dotenv.load_dotenv('../auth.env')

    # For docker
    dotenv.load_dotenv('auth.env')

    if os.environ.get("TG_TOKEN") is None:
        raise RuntimeError("Telegram token not specified")
    
    # Bot setup process

    updater = Updater(token=os.getenv('TG_TOKEN'), use_context=True)
    dispatcher = updater.dispatcher

    # Inline handler
    lebedev_handler = InlineQueryHandler(inline_lebedev)
    dispatcher.add_handler(lebedev_handler)

    # Command handlers
    start_handler = CommandHandler('start', print_help)
    help_handler = CommandHandler('help', print_help)
    meme_handler = CommandHandler('gen', standalone_lebedev)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(meme_handler)

    # Blocking infinite loop
    updater.start_polling()
    updater.idle()
