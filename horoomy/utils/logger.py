from django.utils.timezone import now
from telegram.bot import Bot
from io import BytesIO
from time import sleep
import sys


class AbsReporter:
    def __init__(self, logger):
        self.logger = logger

    def log(self, log):
        pass

    def report(self, title):
        pass


class ConsoleReporter(AbsReporter):
    def log(self, log):
        stream = sys.stderr if log['level'] == Logger.ERROR else sys.stdout
        print(log['text'], file=stream)


class TgReporter(AbsReporter):
    URL = 'https://api.telegram.org/bot{token}/{action}'
    TOKEN = '394409524:AAHkv2WTjrHig7RouUOQAAVdZ5TgVlQOgPs'
    CHAT_ID = -227813278
    BOT = Bot(TOKEN)
    MAX_RETRIES = 5

    @staticmethod
    def send_text(text):
        for _ in range(TgReporter.MAX_RETRIES):
            try:
                TgReporter.BOT.send_message(TgReporter.CHAT_ID, text)
            except:
                continue
            break

    @staticmethod
    def send_file(caption, name, file):
        if isinstance(file, bytes):
            file = BytesIO(file)
        for _ in range(TgReporter.MAX_RETRIES):
            try:
                TgReporter.BOT.send_document(TgReporter.CHAT_ID, file, filename=name, caption=caption)
            except:
                continue
            break

    def report(self, title=None):
        caption = ' Logs '
        if title: caption = ' ' + title + caption
        message_text = '{:=^35}'.format(caption) + '\n' + self.logger.text(threshold=Logger.STATUS)
        TgReporter.send_text(message_text)
        file_text = self.logger.text()
        TgReporter.send_file(caption, 'logs.txt', file_text.encode('utf-8'))


class Logger:
    FORMAT = '{time} [{name:^10}] {level}: {message}'
    TIME_FORMAT = '%H:%M:%S'

    DEFAULT_NAME = 'Logger'
    DEFAULT_REPORTERS = (ConsoleReporter, TgReporter)
    CHECK_KEY_MESSAGE = 'Key "{key}" not found'

    INFO, WARNING, ERROR, STATUS = range(4)
    LEVEL_NAMES = {
        INFO: 'INFO',
        WARNING: 'WARNING',
        ERROR: 'ERROR',
        STATUS: 'STATUS',
    }

    def __init__(self, parent=None, task=None):
        self.parent = parent
        self.name = Logger.DEFAULT_NAME
        self.reporters = [i(parent or self) for i in Logger.DEFAULT_REPORTERS]
        self.timestamps = {'started': now()}
        if self.parent is None:
            self.logs = []
            self.task = task
            self.status('Log session started on', now().strftime('%d.%m.%Y'))
        else:
            self.logs = parent.logs
            self.task = parent.task

    def channel(self, name):
        parent = self.parent or self
        channel = Logger(parent=parent)
        channel.name = name
        return channel

    def log(self, *objects, level=INFO):
        time = now().strftime(self.TIME_FORMAT)
        level_name = self.LEVEL_NAMES[level]
        message = ' '.join(map(str, objects))
        if '\n' in message:
            test_string = self.FORMAT.format(time=time, name=self.name, level=level_name, message='')
            shift = len(test_string) - 3
            message = ('\n...' + ' ' * shift).join(message.split('\n'))
        text = self.FORMAT.format(time=time, name=self.name, level=level_name, message=message)
        log = {'text': text, 'level': level}
        self.logs.append(log)
        for i in self.reporters: i.log(log)

    def check_keys(self, dict, *keys, level=WARNING):
        for key in keys:
            if key not in dict:
                self.log(self.CHECK_KEY_MESSAGE.format(key=key), level=level)

    def timestamp(self, key):
        if key in self.timestamps:
            delta = now() - self.timestamps[key]
            self.timestamps[key] = now()
            return delta
        self.timestamps[key] = now()

    def task_state(self, state, **kwargs):
        if self.task is None: return
        self.task.update_state(state=state, meta=kwargs)

    def text(self, threshold=INFO):
        logs = filter(lambda x: x['level'] >= threshold, self.logs)
        text = '\n'.join(i['text'] for i in logs)
        return text

    def report(self, title=None):
        for i in self.reporters:
            i.report(title)

    info = lambda self, *objects: self.log(*objects, level=self.INFO)
    warning = lambda self, *objects: self.log(*objects, level=self.WARNING)
    error = lambda self, *objects: self.log(*objects, level=self.ERROR)
    status = lambda self, *objects: self.log(*objects, level=self.STATUS)