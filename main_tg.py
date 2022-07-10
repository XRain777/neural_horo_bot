# -*- coding: utf-8 -*-
import os
import re
import calendar
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import vk_api
from dotenv import load_dotenv

load_dotenv()

vk_user_session = vk_api.VkApi(token=os.environ['VK_USER_TOKEN'])
vk_user = vk_user_session.get_api()

SIGNS = [
    '♈️Овен',
    '♉️Телец',
    '♊️Близнецы',
    '♋️Рак',
    '♌️Лев',
    '♍️Дева',
    '♎️Весы',
    '♏️Скорпион',
    '♐️Стрелец',
    '♑️Козерог',
    '♒️Водолей',
    '♓️Рыбы'
]

ARROW_LEFT = "⬅️"
ARROW_RIGHT = "➡️"

peer_dates = {}


def build_keyboard(peer_id):
    result = []

    i = 0
    line = []
    for sign in SIGNS:
        i = i + 1
        line.append(InlineKeyboardButton(sign, callback_data=sign))
        if i % 3 == 0:
            result.append(line)
            line = []

    result.append([
        InlineKeyboardButton(ARROW_LEFT, callback_data=ARROW_LEFT),
        InlineKeyboardButton(peer_dates[peer_id].strftime("%d.%m.%Y"), callback_data="refresh"),
        InlineKeyboardButton(ARROW_RIGHT, callback_data=ARROW_RIGHT),
    ])

    return InlineKeyboardMarkup(result)


updater = Updater(token=os.environ["TG_BOT_TOKEN"])


def get_horoscope(update: Update, context: CallbackContext) -> None:
    if update.callback_query:
        peer_id = update.callback_query.from_user.id
        message_text = update.callback_query.data
    else:
        peer_id = update.message.from_user.id
        message_text = update.message.text

    if peer_id not in peer_dates:
        peer_dates[peer_id] = datetime.today()
    date_text = peer_dates[peer_id].date().strftime("%d.%m.%Y")
    if message_text in SIGNS:
        posts = vk_user.wall.get(owner_id=-193489972, count=100)

        post_found = False

        for post in posts['items']:
            if 'is_pinned' in post:
                continue
            if post['date'] < calendar.timegm(peer_dates[peer_id].date().timetuple()) or \
                    post['date'] > calendar.timegm((peer_dates[peer_id] + timedelta(days=1)).date().timetuple()):
                continue

            horoscope = re.search(re.compile("^" + message_text + '.*', re.MULTILINE), post['text']).group(0)

            horoscope_date_text = datetime.fromtimestamp(post['date']).strftime("%d.%m.%Y")

            horoscope_date_difference = (datetime.today().date() - datetime.fromtimestamp(post['date']).date()).days
            if horoscope_date_difference == 2:
                horoscope_date_difference_text = ", позавчера"
            elif horoscope_date_difference == 1:
                horoscope_date_difference_text = ", вчера"
            elif horoscope_date_difference == 0:
                horoscope_date_difference_text = ", сегодня"
            else:
                horoscope_date_difference_text = ""

            text = horoscope + "\n\n" + "(" + horoscope_date_text + horoscope_date_difference_text + ")"

            post_found = True
            reply_text = text
            break

        if not post_found:
            reply_text = f"Гороскоп на дату {date_text} не найден."
    elif message_text == ARROW_LEFT:
        peer_dates[peer_id] = peer_dates[peer_id] + timedelta(days=-1)
        reply_text = "Выбрана дата " + peer_dates[peer_id].strftime("%d.%m.%Y")
    elif message_text == ARROW_RIGHT:
        peer_dates[peer_id] = peer_dates[peer_id] + timedelta(days=1)
        reply_text = "Выбрана дата " + peer_dates[peer_id].strftime("%d.%m.%Y")
    else:
        reply_text = "Выбери знак зодиака."

    if update.callback_query:
        update.callback_query.edit_message_text(text=reply_text)
        update.callback_query.edit_message_reply_markup(reply_markup=build_keyboard(peer_id))
        update.callback_query.answer()
    else:
        update.message.reply_text("Выбери знак зодиака.", reply_markup=build_keyboard(peer_id))


dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler(Filters.text, get_horoscope))
dispatcher.add_handler(CallbackQueryHandler(get_horoscope))
updater.start_polling()
