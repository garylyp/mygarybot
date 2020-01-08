from telegram.ext import *
import os, pprint, json
import datetime
from sheet_access import *

import logging
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                      level=logging.INFO)

ADD_EVENT_DESCRIPTION = "/add - Add a new event\n"
REMOVE_EVENT_DESCRIPTION = "/remove - Remove an existing event\n"
NEXT_EVENT_DESCRIPTION = "/next - Display the next few upcoming events\n"
SHOW_BIRTHDAYS_DESCRIPTION = "/show_birthdays - Display upcoming birthdays\n" + \
                            "/show_birthdays 3 - Display upcoming birthdays in the next 3 months\n"
VIEW_ATTENDANCE_DESCRIPTION = "/view_attendance - View the attendance taken for the next training\n" + \
                            "/view_attendance 30/01/2020 - View the attendance taken on the specified date in dd/mm/yyyy\n"
TAKE_ATTENDANCE_DESCRIPTION = "/take_attendance - Go into attendance-taking mode\n"
TAKE_ATTENDANCE_TOGGLE_MODE_DESCRIPTION = "/take_attendance_toggle_mode - Go into attendance-taking toggle mode\n"



GARY_BOT_TOKEN = "969707375:AAHFxeUbgV6crUysoahGFicOLLWmE8Pm4Xc"
GARY_BOT_NAME = "mygarybot"
PORT1 = int(os.environ.get('PORT', '8443'))


# TODO Implement OOP for BotController

class Bot():
    def __init__(self, token, name, port):
        self.token = token
        self.name = name
        self.port = port
        self.updater = Updater(token)
        self.dispatcher = self.updater.dispatcher
        self.is_dev_mode = False

    def add_handlers(self, handlers):
        for handler in handlers:
            self.dispatcher.add_handler(handler)
        

    def remove_handlers(self, handlers):
        for handler in handlers:
            self.dispatcher.remove_handler(handler)
        

    def setDevMode(self, is_dev):
        """
        If set to True, Bot will be detached from Heroku and will run on polling mode via command line
        """
        self.is_dev_mode = is_dev

    def deploy(self):
        if self.is_dev_mode:
            print("Starting poll...")
            self.updater.start_polling(clean=True)
            self.updater.idle()
            
        else:
            print("Starting webhook...")
            self.updater.start_webhook(listen="0.0.0.0",
                                port=self.port,
                                url_path=self.token)
            self.updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(self.name, self.token))
            self.updater.idle()



class MyGaryBot(Bot):

    PROMPT_FOR_NAMES = "Enter the next name to continue. To end, enter \"end\"."
    TAKE_ATTENDANCE_TOGGLE_MODE_GUIDE = "You have entered attendance-taking TOGGLE mode. " + \
        "Enter names to toggle their state between PRESENT and ABSENT."
    TAKE_ATTENDANCE_GUIDE = "You have entered attendance-taking mode. " + \
        "Enter names to mark them as PRESENT."

    def __init__(self):
        Bot.__init__(self, GARY_BOT_TOKEN, GARY_BOT_NAME, PORT1)
        

        self.commands = [
            CommandHandler("help", self.help),
            CommandHandler("show_birthdays", self.show_birthdays),
            CommandHandler("view_attendance", self.view_attendance),
            CommandHandler("take_attendance", self.take_attendance),
            CommandHandler("take_attendance_toggle_mode", self.take_attendance_toggle_mode),
        ]

        # If you face the issue of the bot not responding to text messages in group chats,
        # look for BotFather and set the privacy mode of MyGaryBot to Disable
        self.attendance_handlers = [
            MessageHandler(Filters.text, self.mark_names)
        ]

        self.verification_handlers = [
            MessageHandler(Filters.text, self.verify_names)
        ]

        self.add_handlers(self.commands)

        self.attendance_manager = None

    # Callbacks
    def add(self, bot, update):
        command = "/add"
        text = update.message.text
        main_content = "".join(text.split(command))
        update.message.reply_text("Adding" + main_content, quote=False)

    def help(self, bot, update):
        print("Callback called:", "help")  
        main_content = "To begin, type in the following commands:\n\n" \
            + SHOW_BIRTHDAYS_DESCRIPTION \
            + VIEW_ATTENDANCE_DESCRIPTION \
            + TAKE_ATTENDANCE_DESCRIPTION \
            + TAKE_ATTENDANCE_TOGGLE_MODE_DESCRIPTION
        update.message.reply_text(main_content, quote=False)

    def view_attendance(self, bot, update):
        print("Callback called:", "view_attendance") 
        if self.attendance_manager is None:
            self.attendance_manager = AttendanceSheetManager()
        
        output = self.attendance_manager.display_attendance_by_date()
        update.message.reply_text(output, quote=False)

    def take_attendance(self, bot, update):
        print("Callback called:", "take_attendance")  
        self.is_toggle_mode = False

        self.remove_handlers(self.commands)
        self.add_handlers(self.attendance_handlers)
        if self.attendance_manager is None:
            self.attendance_manager = AttendanceSheetManager()

        update.message.reply_text(MyGaryBot.TAKE_ATTENDANCE_GUIDE, quote=False)
        output = MyGaryBot.PROMPT_FOR_NAMES
        update.message.reply_text(output, quote=False)

        
    def take_attendance_toggle_mode(self, bot, update):
        print("Callback called:", "take_attendance_toggle_mode")  
        self.is_toggle_mode = True

        self.remove_handlers(self.commands)
        self.add_handlers(self.attendance_handlers)
        if self.attendance_manager is None:
            self.attendance_manager = AttendanceSheetManager()

        update.message.reply_text(MyGaryBot.TAKE_ATTENDANCE_TOGGLE_MODE_GUIDE, quote=False)
        output = MyGaryBot.PROMPT_FOR_NAMES
        update.message.reply_text(output, quote=False)

    def mark_names(self, bot, update):
        """
        Callback function that is executed when a member's names is entered.
        """
        print("Callback called:", "mark_names")  
        input_name = update.message.text

        if input_name.lower() == "end":
            self.remove_handlers(self.attendance_handlers)
            self.add_handlers(self.commands)
            update.message.reply_text("Session ended.", quote=False)

            output = self.attendance_manager.display_attendance_by_date()
            update.message.reply_text(output, quote=False)

        else:
            if self.is_toggle_mode:
                output, self.options = self.attendance_manager.submit_name_to_mark_toggle(input_name)
            else:
                output, self.options = self.attendance_manager.submit_name_to_mark_present(input_name)
            if self.options:
                self.remove_handlers(self.attendance_handlers)
                self.add_handlers(self.verification_handlers)
            update.message.reply_text(output, quote=False)

    def verify_names(self, bot, update):
        print("Callback called:", "verify_names")
        option = update.message.text.strip()
        if option == '1':
            output, _ = self.attendance_manager.submit_name_to_mark_present(self.options[0])
        elif option == '2':
            output, _ = self.attendance_manager.submit_name_to_mark_present(self.options[1])
        elif option == '3':
            output, _ = self.attendance_manager.submit_name_to_mark_present(self.options[2])
        
        if option in ['1', '2', '3']:
            update.message.reply_text(output, quote=False)
        elif option == '4':
            output = MyGaryBot.PROMPT_FOR_NAMES
            update.message.reply_text(output, quote=False)
        else:
            output = "Invalid option. " + MyGaryBot.PROMPT_FOR_NAMES
            update.message.reply_text(output, quote=True)


        self.remove_handlers(self.verification_handlers)
        self.add_handlers(self.attendance_handlers)



    def show_birthdays(self, bot, update):
        print("Callback called:", "show_birthdays")  
        args = parse_arguments(update.message.text)
        try:
            months_from_today = int(args[0])
        except:
            months_from_today = 1
        output = get_recent_birthdays_reply(months_from_today)
        update.message.reply_text(output, quote=False)


    # For debugging purposes
    def echo(self, bot, update):
        update.message.reply_text(update.message.text, quote=True)

def parse_arguments(text):
    for i in range(len(text)-1):
        if text[i] == " ":
            return text[i+1:].split(" ")
    return []


def main(): 
    garybot = MyGaryBot()
    # garybot.setDevMode(True)
    garybot.deploy()


 
if __name__ == '__main__': 
    main()
 