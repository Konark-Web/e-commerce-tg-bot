import telebot
from django.db import models


class BotConfig(models.Model):
    title = models.CharField("Назва бота", max_length=80, blank=True,
                             default="")
    token = models.CharField("Токен бота", max_length=100, primary_key=True)
    server_url = models.CharField("Webhook Url", max_length=200, blank=True,
                                  default="")
    nova_poshta_api = models.CharField("Nova Poshta API", max_length=200,
                                       blank=True)
    is_active = models.BooleanField(default=True)

    def set_hook(self):
        bot = telebot.TeleBot(self.token)
        webhook_url = str(self.server_url) + "/get_hook/"
        bot.set_webhook(webhook_url)

    def set_active_config(self):
        if self.is_active:
            other_active_configs = BotConfig.objects.filter(is_active=True)
            for config in other_active_configs:
                if config.pk != self.pk:
                    config.is_active = False
                    config.save()

    def save(self, *args, **kwargs):
        self.set_hook()
        self.set_active_config()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.is_active:
            return f"Актуальні налаштування бота [{self.title}]"
        else:
            return f"Неактивні налаштування бота [{self.title}]"

    class Meta:
        verbose_name = "Налаштування"
        verbose_name_plural = "Налаштування бота"
