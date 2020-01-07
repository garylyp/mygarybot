from telegram.ext import *
import os, pprint, json
import datetime
from sheets.sheet_access import init_sheet, get_birthdays_from_sheet, get_recent_birthdays_reply

ADD_EVENT_GUIDE = "/add - Add a new event\n"
REMOVE_EVENT_GUIDE = "/remove - Remove an existing event\n"
NEXT_EVENT_GUIDE = "/next - Display the next few upcoming events\n"
SHOW_BIRTHDAYS_GUIDE = "/show_birthdays - Display the next few upcoming birthdays\n"
TAKE_ATTENDANCE_GUIDE = "/take_attendance - Go into attendance taking mode\n"

# Callbacks
def add(bot, update):
    command = "/add"
    text = update.message.text
    main_content = "".join(text.split(command))
    update.message.reply_text("Adding" + main_content, quote=False)

def help(bot, update):
    main_content = "To begin, type in the following commands:\n\n" \
        + SHOW_BIRTHDAYS_GUIDE \
        + TAKE_ATTENDANCE_GUIDE
    update.message.reply_text(main_content, quote=False)

def take_attendance(bot, update):
    reply = "Enter name: "
    update.message.reply_text(reply, quote=False)
    # TODO: For each name submitted, check against attendance sheet and reply whether it is successfully taken or not
    # TODO: for duplicate names like valerie chua, double confirm 
    # TODO: Undo command

def show_birthdays(bot, update):
    print("Callback called:", "show_birthdays")  
    args = parse_arguments(update.message.text)
    try:
        months_from_today = int(args[0])
    except:
        months_from_today = 1
    reply = get_recent_birthdays_reply(months_from_today)
    update.message.reply_text(reply, quote=False)


# For debugging purposes
def echo(bot, update):
    update.message.reply_text(update.message.text, quote=True)

def parse_arguments(text):
    for i in range(len(text)-1):
        if text[i] == " ":
            return text[i+1:].split(" ")
    return []


def init_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("show_birthdays", show_birthdays))
    dispatcher.add_handler(CommandHandler("take_attendance", take_attendance))
    # dispatcher.add_handler(MessageHandler(Filters.text, echo))

def main(): 
    DEV = False
    TOKEN = "969707375:AAHFxeUbgV6crUysoahGFicOLLWmE8Pm4Xc"
    NAME = "mygarybot"
    PORT = int(os.environ.get('PORT', '8443'))


    updater = Updater(TOKEN)
    # updater.bot.deleteWebhook() // Not needed
    init_handlers(updater.dispatcher)

    if DEV:
        print("Starting poll...")
        updater.start_polling(clean=True)
        updater.idle()
        
    else:
        print("Starting webhook...")
        updater.start_webhook(listen="0.0.0.0",
                            port=PORT,
                            url_path=TOKEN)
        updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))
        updater.idle()
    



 
if __name__ == '__main__': 
    main()
 