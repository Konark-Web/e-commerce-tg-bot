import re

from tbot.models import BotConfig


def get_nova_poshta_api():
    return BotConfig.objects.filter(is_active=True).first().nova_poshta_api


def validate_phone_number(message):
    string = message
    match1 = re.fullmatch(r'\+\d{12}', string)
    match2 = re.fullmatch(r'\+\d{3}\s\d{2}\s\d{3}\s\d{2}\s\d{2}', string)
    match3 = re.fullmatch(r'\d\s\d{2}\s\d{3}\s\d{2}\s\d{2}', string)
    match4 = re.fullmatch(r'\d{10}', string)
    match5 = re.fullmatch(r'\d{3}\s\d{2}\s\d{3}\s\d{2}\s\d{2}', string)
    match6 = re.fullmatch(r'\d{12}', string)
    match7 = re.fullmatch(r'\d{11}', string)

    return any([match1, match2, match3, match4, match5, match6, match7])