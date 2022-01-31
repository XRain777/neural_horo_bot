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

vk_session_user = vk_api.VkApi(token=os.environ['VK_USER_TOKEN'])
vk_user = vk_session_user.get_api()
vk_session_bot = vk_api.VkApi(token=os.environ['VK_GROUP_TOKEN'])
vk_bot = vk_session_bot.get_api()

longpoll = VkBotLongPoll(vk_session_bot, os.environ['VK_GROUP_ID'])

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


for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        peer_id = event.object['message']['peer_id']
        message_text = event.object['message']['text']
        if peer_id not in peer_dates:
            peer_dates[peer_id] = datetime.today()
        if message_text in SIGNS:
            posts = vk_user.wall.get(owner_id=-193489972, count=100)

            for post in posts['items']:
                if 'is_pinned' in post:
                    continue
                if post['date'] < calendar.timegm(peer_dates[peer_id].date().timetuple()) or\
                   post['date'] > calendar.timegm((peer_dates[peer_id] + timedelta(days=1)).date().timetuple()):
                    continue

                text = re.search(re.compile("^" + message_text + '.*', re.MULTILINE), post['text']).group(0)
                text = text + "\n\n(" + datetime.fromtimestamp(post['date']).strftime("%d.%m.%Y") + ")"

                keyboard = build_keyboard(peer_id)

                vk_bot.messages.send(
                    peer_id=peer_id,
                    random_id=get_random_id(),
                    keyboard=keyboard.get_keyboard(),
                    message=text
                )
                break
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
