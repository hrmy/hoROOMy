import sys
import json
import requests
from traceback import format_tb


# ---------------------------------------TELEGRAM BOT UTIL----------------------------------------------
class Bot:
    full_link = ""

    def __init__(self, chat_id):
        self.full_link = "https://api.telegram.org/bot332143024:AAFXvkc397uXcvN3HgbiKQ0GTaNXKf-H-zs/%s?chat_id="+chat_id

    def sendMessage(self, text):
        requests.post(self.full_link % 'sendMessage', data={'text': text})

# since we use only one bot, here are its params
ERROR_CHAT_ID = '273633310'
alertBot = Bot(ERROR_CHAT_ID)


# alerting an exception occured with the bot
def alertExc():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    Bot(ERROR_CHAT_ID).sendMessage(str(format_tb(exc_traceback)) + str(exc_value) + str(exc_type))

#------------------------------------------------------------------------------------------------------