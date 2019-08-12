from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Callbacks
def add(bot, update):
    command = "add"
    text = update.message.text
    main_content = text[text.index(command) + len(command) + 1:]
    update.message.reply_text("Adding " + main_content)

def help(bot, update):
    command = "help"
    text = update.message.text
    main_content = text[text.index(command) + len(command) + 1:]
    update.message.reply_text("A guide on " + main_content)

def echo(bot, update):
    update.message.reply_text(update.message.text)


def init_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help))
    # dispatcher.add_handler(MessageHandler(Filters.text, echo))

def main(): 
    TOKEN = "969707375:AAERFhml7PbV6NFzBA0r-5nHSCuXjBRHDmk"
    # base_url = "https://api.telegram.org/bot" + TOKEN + "/"
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    init_handlers(dp)
    
    updater.start_polling()
    updater.idle()


 
if __name__ == '__main__': 
    main()
 