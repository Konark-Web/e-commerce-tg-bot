import telebot
from django.db import connection

from .models import BotConfig


class TBot:
    def __init__(self):
        if 'tbot_botconfig' in connection.introspection.table_names()\
                and BotConfig.objects.filter(is_active=True):
            config = BotConfig.objects.get(is_active=True)
            self.server_url = config.server_url
            self.bot = telebot.TeleBot(config.token, parse_mode='HTML')
        else:
            self.bot = telebot.TeleBot('default_token')

    def get_bot(self):
        return self.bot

    def update(self, json_data):
        return telebot.types.Update.de_json(json_data)
