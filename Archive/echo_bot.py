import os, glob

import urllib.request, json
import datetime

import telebot

bot = telebot.TeleBot("849022219:AAGiMuA93McYGilGhuHJ9-HELGsElqxQZ14")

@bot.message_handler(commands=['add', 'done', 'remove'])
def add_task(message):
    bot.reply_to(message, "Insert subject")


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, message.text)

bot.polling()