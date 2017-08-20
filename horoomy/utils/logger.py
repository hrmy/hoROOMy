from django.utils.timezone import now
from io import StringIO
from sys import stdout
import requests
import re


class TgBot:
    URL = 'https://api.telegram.org/bot{token}/sendMessage'
    TOKEN = '394409524:AAHkv2WTjrHig7RouUOQAAVdZ5TgVlQOgPs'
    CHAT_ID = -227813278

    @staticmethod
    def send(text):
        url = TgBot.URL.format(token=TgBot.TOKEN)
        return requests.post(url, data={'chat_id': TgBot.CHAT_ID, 'text': text})


class Logger:
    FORMAT = '{time} [{name:^10}] {level}: {message}'
    TIME_FORMAT = '%H:%M:%S'
    INFO, WARNING, ERROR = range(3)
    LEVEL_NAMES = {
        INFO: 'INFO',
        WARNING: 'WARNING',
        ERROR: 'ERROR',
    }
    DEFAULT_NAME = 'Logger'
    CHECK_MESSAGE = 'Check "{name}" failed'
    CHECK_KEY_MESSAGE = 'Key "{key}" not found in "{name}"'
    EXTRA_STREAMS = (stdout,)

    def __init__(self, *streams):
        self.streams = [StringIO()]
        self.streams.extend(self.EXTRA_STREAMS)
        self.streams.extend(streams)
        self.name = self.DEFAULT_NAME
        self.timestamps = {}
        self.timestamp('started')
        self.log('Log session started on {}'.format(now().strftime('%d.%m.%Y')))

    def log(self, *objects, name=None, level=INFO):
        name = name or self.name
        time = now().strftime(self.TIME_FORMAT)
        level = self.LEVEL_NAMES[level]
        message = ' '.join(map(str, objects))
        if '\n' in message:
            test_string = self.FORMAT.format(time=time, name=name, level=level, message='')
            shift = len(test_string) - 3
            message = ('\n...' + ' ' * shift).join(message.split('\n'))
        string = self.FORMAT.format(time=time, name=name, level=level, message=message)
        for s in self.streams: print(string, file=s)

    def check(self, expression, level=WARNING, name='unnamed check'):
        if not expression:
            self.log(self.CHECK_MESSAGE.format(name=name), level=level)
        return expression

    def check_keys(self, dict, *keys, level=WARNING, name='unnamed dict'):
        for key in keys:
            if key not in dict:
                self.log(self.CHECK_KEY_MESSAGE.format(key=key, name=name), level=level)

    def timestamp(self, key):
        if key in self.timestamps:
            delta = now() - self.timestamps[key]
            self.timestamps[key] = now()
            return delta
        self.timestamps[key] = now()

    get_text = lambda self: self.streams[0].getvalue()
    close = lambda self: self.streams[0].close()
    info = lambda self, *objects, name=None: self.log(*objects, name=name, level=self.INFO)
    warning = lambda self, *objects, name=None: self.log(*objects, name=name, level=self.WARNING)
    error = lambda self, *objects, name=None: self.log(*objects, name=name, level=self.ERROR)