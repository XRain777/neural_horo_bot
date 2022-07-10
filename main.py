# -*- coding: utf-8 -*-
import os
import re
import calendar
from datetime import datetime, timedelta
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from dotenv import load_dotenv

load_dotenv()

vk_user_session = vk_api.VkApi(token=os.environ['VK_USER_TOKEN'])
vk_user = vk_user_session.get_api()
vk_bot_session = vk_api.VkApi(token=os.environ['VK_BOT_TOKEN'])
vk_bot = vk_bot_session.get_api()

vk_bot_longpoll = VkBotLongPoll(vk_bot_session, os.environ['VK_BOT_GROUP_ID'])

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
    result = VkKeyboard(one_time=False)

    i = 0
    for sign in SIGNS:
        i = i + 1
        result.add_button(sign, color=VkKeyboardColor.PRIMARY)
        if i % 3 == 0:
            result.add_line()

    result.add_button(ARROW_LEFT, color=VkKeyboardColor.POSITIVE)
    result.add_button(peer_dates[peer_id].strftime("%d.%m.%Y"), color=VkKeyboardColor.SECONDARY)
    result.add_button(ARROW_RIGHT, color=VkKeyboardColor.POSITIVE)

    return result


vk_bot.messages.send(
    peer_id=os.environ['VK_ADMIN_ID'],
    random_id=get_random_id(),
    message="Бот запущен."
)


for event in vk_bot_longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        peer_id = event.object['message']['peer_id']
        message_text = event.object['message']['text']
        if peer_id not in peer_dates:
            peer_dates[peer_id] = datetime.today()
        date_text = peer_dates[peer_id].date().strftime("%d.%m.%Y")
        if message_text in SIGNS:
            keyboard = build_keyboard(peer_id)
            posts = vk_user.wall.get(owner_id=-193489972, count=100)

            post_found = False

            for post in posts['items']:
                if 'is_pinned' in post:
                    continue
                if post['date'] < calendar.timegm(peer_dates[peer_id].date().timetuple()) or\
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
                vk_bot.messages.send(
                    peer_id=peer_id,
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard(),
                    message=text
                )
                break

            if not post_found:
                vk_bot.messages.send(
                    peer_id=peer_id,
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard(),
                    message=f"Гороскоп на дату {date_text} не найден."
                )
        elif message_text == ARROW_LEFT:
            peer_dates[peer_id] = peer_dates[peer_id] + timedelta(days=-1)
            keyboard = build_keyboard(peer_id)

            vk_bot.messages.send(
                peer_id=peer_id,
                random_id=get_random_id(),
                keyboard=keyboard.get_keyboard(),
                message="Выбрана дата " + peer_dates[peer_id].strftime("%d.%m.%Y")
            )
        elif message_text == ARROW_RIGHT:
            peer_dates[peer_id] = peer_dates[peer_id] + timedelta(days=1)
            keyboard = build_keyboard(peer_id)

            vk_bot.messages.send(
                peer_id=peer_id,
                random_id=get_random_id(),
                keyboard=keyboard.get_keyboard(),
                message="Выбрана дата " + peer_dates[peer_id].strftime("%d.%m.%Y")
            )
        else:
            keyboard = build_keyboard(peer_id)
            vk_bot.messages.send(
                peer_id=event.object['message']['peer_id'],
                random_id=get_random_id(),
                keyboard=keyboard.get_keyboard(),
                message="Выбери знак зодиака."
            )
    else:
        print(event.type)
        print()
