from __future__ import print_function
import pickle
import datetime
import os.path
import glob
import csv
import difflib
import numpy as np

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


import json

# If modifying these scopes, delete the file token.pickle.
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
# SCOPES = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
SCOPES = ['https://www.googleapis.com/auth/drive']

# The ID and range of a sample spreadsheet.
BIRTHDAY_SHEET_ID ='1LuVv62bj1DD-whvJydT_maMMbe7h3yWQYXzB-PkKDJQ'
BIRTHDAY_RANGE = 'AY1920!A:J'
ATTENDANCE_SHEET_ID = '1XfjN4aiK4wVaioNYep8Wsfqww3yVJQEfB47zekmMmOQ'
if datetime.date.today() < datetime.date(2020, 3, 17):
    ATTENDANCE_SHEET_NAME = '2nd Quarter'
else:
    ATTENDANCE_SHEET_NAME = '3rd Quarter'
ATTENDANCE_SHEET_RANGE = 'A:AG'
ATTENDANCE_RANGE = ATTENDANCE_SHEET_NAME + '!' + ATTENDANCE_SHEET_RANGE

DATE_FORMATTER = "%d/%m/%Y"
DATETIME_FORMATTER = "%d/%m/%Y %H%M%S"

def init_sheet():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()

    return sheet



def get_birthdays_from_sheet(sheet):
    result = sheet.values().get(spreadsheetId=BIRTHDAY_SHEET_ID,
                                range=BIRTHDAY_RANGE).execute()
    
    list_of_birthday = result.get('values', [])
    # print(json.dumps(list_of_birthday, indent=4))
    return list_of_birthday

def get_recent_birthdays_reply(months_from_today):
    filename = "./birthday_sheet_{}.csv".format(datetime.date.today().strftime("%m%y"))
    
    # Load contents from new sheet if file does not exist
    if not os.path.exists(filename):
        list_of_birthday = get_birthdays_from_sheet(init_sheet())

        all_files = glob.glob("./birthday_sheet*")
        for f in all_files:
            os.remove(f)
        with open(filename, 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(list_of_birthday)
    
    # Read from existing file if file exists
    else:
        with open (filename, 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            list_of_birthday = csv_reader_to_list(csv_reader)


    recent = get_recent_birthdays(list_of_birthday, months_from_today)
    output = "Upcoming Birthdays:\n"
    for row in recent[1:]:
        full_name = row[0]
        full_name_capitalized = " ".join([word.capitalize() for word in full_name.split(" ")])
        output += "{} : {}\n".format(row[2], full_name_capitalized)
    return output


def get_recent_birthdays(list_of_birthday, months_from_today):
    if not list_of_birthday:
        print('No data found.')
    else:
        # print('Recent Birthdays:')
        # recent = []
        # today = int(list_of_birthday[0][4])
        curr_month = int(list_of_birthday[0][5])
        filtered_list = [row for row in list_of_birthday if is_recent(int(row[5]), curr_month, months_from_today)]
        filtered_list.sort(key = lambda row : int(row[5]) if int(row[5]) >= curr_month else int(row[5]) + 12)
    return filtered_list

def is_recent(birth_month, curr_month, months_from_today):
    if months_from_today >= 0:
        end_month = curr_month + months_from_today
        if birth_month < curr_month: 
            birth_month += 12
        return end_month >= birth_month
    else:
        return False


def csv_reader_to_list(csv_reader):
    ls = []
    for row in csv_reader:
        # To filter out rows with incomplete data
        if len(row) < 8: 
            continue
        ls.append(row)
    return ls 

# print("2 month")
# print(get_recent_birthdays_reply(2))

# print("6 month")
# print(get_recent_birthdays_reply(6))

# print("12 month")
# print(get_recent_birthdays_reply(12))

# print("25 month")
# print(get_recent_birthdays_reply(25))

class AttendanceSheetManager():

    SUCCESS_MESSAGE = "Yay! {} is marked {} on {}"
    FAILURE_MESSAGE = "Too bad...No close match with \"{}\".\nSelect ONE of the options:\n" + \
        "(1) {}\n" + \
        "(2) {}\n" + \
        "(3) {}\n" + \
        "(4) None of the above."

    def __init__(self):
        

        self.sheet = init_sheet()
        self.attendance_sheet = self.get_attendance_from_sheet()
        self.date_row = 1
        self.date_col_start = 2
        self.date_col_end = len(self.attendance_sheet[1])
        self.curr_year = int(self.attendance_sheet[0][0])
        self.today = datetime.datetime.strptime(self.attendance_sheet[0][1] + "/" + str(self.curr_year), DATE_FORMATTER)
        self.name_row_start = 2
        self.name_row_end = len(self.attendance_sheet)
        self.name_col = 1

        self.dates = self.get_training_dates()
        self.names = self.get_names()

        print("You have created an AttendanceManager")

        

    def get_attendance_from_sheet(self):
        # Allows Sheet ID and Attendance Range to be decided by user input
        result = self.sheet.values().get(spreadsheetId=ATTENDANCE_SHEET_ID,
                                    range=ATTENDANCE_RANGE).execute()
        
        full_attendance_sheet = result.get('values', [])
        # print(json.dumps(full_attendance_sheet, indent=4))
        return full_attendance_sheet


    def get_training_dates(self):
        """
        Returns the full list of training days specified in the selected sheet of the spreadsheet.
        """
        dates_string = self.attendance_sheet[self.date_row][self.date_col_start:self.date_col_end]
        earliest_month = int(dates_string[0].split('/')[1])
        latest_month = int(dates_string[-1].split('/')[1])
        dates = [self.process_dates(ds, self.curr_year, earliest_month, latest_month) for ds in dates_string]
        return dates

    def process_dates(self, date_string, curr_year, earliest_month, latest_month):
        """
        Process the dates by ending the respective YEAR to the dd/mm entries taken from the spreadsheet.
        """       
        given_month = int(date_string.split("/")[1])
        if earliest_month % 12 <= given_month <= latest_month:
            standard_date = "/" + str(curr_year) + " 235959"
            return datetime.datetime.strptime(date_string + standard_date, DATETIME_FORMATTER)
        else:
            standard_date = "/" + str(curr_year - 1) + " 235959"
            return datetime.datetime.strptime(date_string + standard_date, DATETIME_FORMATTER)


    
    def get_names(self):
        return [self.attendance_sheet[row][self.name_col] for row in range(self.name_row_start, self.name_row_end)]
        


    def get_next_date(self):
        """
        Returns the next upcoming training date from today.
        """
        TODAY = datetime.datetime.now()
        for d in self.dates:
            if TODAY <= d:
                return d
        return datetime.datetime.min


    def get_col_idx(self, next_date):
        if next_date == datetime.datetime.min:
            return -1
        else:
            return self.dates.index(next_date) + self.date_col_start

    def get_row_idx(self, name):
        idx = self.names.index(name)
        return idx + self.name_row_start 

    def get_close_match(self, input_name):
        num = 3
        WEIGHT = [0.5, 0.2, 0.3]
        IS_JUNK = lambda x: x in "-',"

        names = [n.lower() for n in self.names]
        test = input_name.lower()

        score = [0 for i in range(len(names))]
        for i in range(len(names)):
            name = names[i]

            # Exact Match
            if name == test:
                return [self.names[i]] * 3, 1

            # Partial Match
            test_split = test.split(" ")
            name_split = name.split(" ")
            for t in test_split:
                for n in name_split:
                    if t == n:
                        score[i] += 1
            
            score[i] *= (WEIGHT[0])
            
            # Current Attendance
            percentage = self.get_attendance_for_member(self.names[i]) / self.get_attendance_for_member('TOTAL')
            score[i] += percentage * WEIGHT[1]
                

            # Similar sequence
            a = difflib.SequenceMatcher(IS_JUNK, name, test).ratio()
            b = difflib.SequenceMatcher(IS_JUNK, test, name).ratio()
            score[i] += WEIGHT[2] * (a + b) / 2

            if name in "total":
                score[i] = 0


        sorted_score = sorted(score, reverse=True)[:num]
        idx = [score.index(s) for s in sorted_score]
        
        closest_match = [self.names[i] for i in idx]
        # diff = min(sorted_score[0] - sorted_score[1], sorted_score[0] - sorted_score[2])
        diff = sorted_score[0] - sorted_score[1]
        # for i in range(3):
        #     print(sorted_score[i], closest_match[i])
        # print(diff)
        return closest_match, diff
    

    def get_attendance_for_member(self, name):
        row_idx = self.get_row_idx(name)
        attendance = sum([int(n) for n in self.attendance_sheet[row_idx][self.date_col_start:self.date_col_end] if n != ''])
        return attendance

    def get_range(self, name, date):
        col_idx = self.get_col_idx(date) 
        row_idx = self.get_row_idx(name) + 1 # Because excel starts from index 1
        if col_idx < 0:
            raise ValueError("Spreadsheet outdated. Provide the URL to the new spreadsheet")
        if row_idx < 0:
            raise ValueError("Name not found.")

        if col_idx < 26:
            col_range= chr(ord('A') + col_idx % 26)
        else:
            col_range = chr(ord('A') + col_idx // 26 - 1) + chr(ord('A') + col_idx % 26)
        
        range = ATTENDANCE_SHEET_NAME + '!' + str(col_range) + str(row_idx)
        return range

    def mark_present(self, name, date):
        range = self.get_range(name, date)
        print(range)
        self.sheet.values().update(
            spreadsheetId=ATTENDANCE_SHEET_ID,
            range=range,
            valueInputOption='USER_ENTERED',
            body={'values':[[1]]}
        ).execute()

    def mark_absent(self, name, date):
        range = self.get_range(name, date)
        self.sheet.values().update(
            spreadsheetId=ATTENDANCE_SHEET_ID,
            range=range,
            valueInputOption='USER_ENTERED',
            body={'values':[[""]]}
        ).execute()

    def mark_toggle(self, name, date):
        range = self.get_range(name, date)
        curr_value = self.sheet.values() \
                                .get(spreadsheetId=ATTENDANCE_SHEET_ID, range=range) \
                                .execute() \
                                .get('values', [])
        if curr_value == []:
            self.mark_present(name, date)
            isMarkPresent = True
            return isMarkPresent
        elif curr_value == [['1']]:
            self.mark_absent(name, date)
            isMarkPresent = False
            return isMarkPresent

    def resolve_date(self, input_date):
        """
        A method to validate the date string provided by user. 
        """
        if input_date is None:
            date = self.get_next_date()
        else:
            date = datetime.datetime.strptime(input_date, DATE_FORMATTER)   
        return date

    # Telegram Bot Entry Point
    def submit_name_to_mark_present(self, input_name, input_date=None):

        names, diff = self.get_close_match(input_name)
        date = self.resolve_date(input_date)
        if diff > 0.15:
            self.mark_present(names[0], date)
            return AttendanceSheetManager.SUCCESS_MESSAGE.format(self.prettify_name(names[0]), 
                "PRESENT", 
                date.strftime(DATE_FORMATTER)), []
        else:
            return AttendanceSheetManager.FAILURE_MESSAGE.format(input_name, names[0], names[1], names[2]), names

    def submit_name_to_mark_absent(self, input_name, input_date=None):

        names, diff = self.get_close_match(input_name)
        date = self.resolve_date(input_date)
        if diff > 0.15:
            self.mark_absent(names[0], date)
            return AttendanceSheetManager.SUCCESS_MESSAGE.format(self.prettify_name(names[0]), 
                "ABSENT", 
                date.strftime(DATE_FORMATTER)), []
        else:
            return AttendanceSheetManager.FAILURE_MESSAGE.format(input_name, names[0], names[1], names[2]), names

    def submit_name_to_mark_toggle(self, input_name, input_date=None):

        names, diff = self.get_close_match(input_name)
        date = self.resolve_date(input_date)
        if diff > 0.15:
            isMarkPresent = self.mark_toggle(names[0], date)
            state = "PRESENT" if isMarkPresent else "ABSENT"
            return AttendanceSheetManager.SUCCESS_MESSAGE.format(self.prettify_name(names[0]), 
                state, 
                date.strftime(DATE_FORMATTER)), []
        else:
            return AttendanceSheetManager.FAILURE_MESSAGE.format(input_name, names[0], names[1], names[2]), names
        
    def display_attendance_by_date(self, input_date=None):
        self.attendance_sheet = self.get_attendance_from_sheet()

        date = self.resolve_date(input_date)

        col_idx = self.get_col_idx(date)
        output_names = []
        for i in range(len(self.names)):
            if len(self.attendance_sheet[i+self.name_row_start]) <= col_idx:
                continue

            if self.names[i] == "TOTAL":
                continue
            
            elif self.attendance_sheet[i+self.name_row_start][col_idx] == "1":
                output_names += [self.names[i]]
        
        output = "Date: {}\n".format(date.strftime(DATE_FORMATTER))
        if len(output_names) == 0:
            output = output + "Nobody present."
        else:
            for i in range(len(output_names)):
                output = output + "{}. {}\n".format(i+1, output_names[i])
        return output


    def prettify_name(self, input_name):
        if "Jian Hui" in input_name:
            return "Jian Hui the Captain"

        elif "Jasmine" in input_name:
            return "Plessidun"

        elif "Le Rae" in input_name:
            return "Le Rae the fatass"

        elif "ChuQiao" in input_name:
            return "lousy chuqiao"

        elif "Mindy" in input_name:
            return "time-to-wake-up-mindy"

        elif "Jeremy" in input_name:
            return "Minister Mentor Ho"

        elif "Julia" in input_name:
            return "Joolyer"

        elif "Chua Kai En" in input_name:
            return "Chua 🐷"

        elif "Chua Qi Shan" in input_name:
            return "Chua 🙈"

        else:
            return input_name
    

# def main():
    # attendance_sheet_manager = AttendanceSheetManager()
    # print(attendance_sheet_manager.display_attendance_by_date())
    # print(attendance_sheet_manager.submit_name_to_mark_toggle("Gary"))
    # print(attendance_sheet_manager.display_attendance_by_date())
    # print(attendance_sheet_manager.submit_name_to_mark_toggle("Gary"))
    # print(attendance_sheet_manager.display_attendance_by_date())
    # print(attendance_sheet_manager.submit_name_to_mark_toggle("zaw"))
    # print(attendance_sheet_manager.submit_name_to_mark_toggle("lim"))
    # print(attendance_sheet_manager.submit_name_to_mark_toggle("chua"))
    # print(attendance_sheet_manager.submit_name_to_mark_toggle("jian hui"))
    # print(attendance_sheet_manager.submit_name_to_mark_toggle("valerie"))
    # print(attendance_sheet_manager.submit_name_to_mark_toggle("julia"))


# if __name__ == '__main__':
#     main()

