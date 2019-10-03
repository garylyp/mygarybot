from __future__ import print_function
import pickle
import datetime
import os.path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


import json

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
BIRTHDAY_SHEET_ID ='1LuVv62bj1DD-whvJydT_maMMbe7h3yWQYXzB-PkKDJQ'
BIRTHDAY_RANGE = 'AY1920!A:J'
# TODO: Should test on a dummy attendance sheet first
ATTENDANCE_SHEET_ID = '1XfjN4aiK4wVaioNYep8Wsfqww3yVJQEfB47zekmMmOQ'
ATTENDANCE_RANGE = '1st Quarter!A:AF'

# TODO: Make this an object instead. Initialize a sheet object which you can constantly call upon
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
    # print(json.dumps(values, indent=4))
    filename = "./birthday_sheet_{}.txt".format(datetime.date.today().strftime("%d%m%y"))
    if not os.path.exists(filename):
        with open(filename, 'wb') as fp:
            pickle.dump(list_of_birthday, fp)
    return list_of_birthday

def get_recent_birthdays_reply(months_from_today):
    filename = "./birthday_sheet_{}.csv".format(datetime.date.today().strftime("%d%m%y"))
    if not os.path.exists(filename):
        list_of_birthday = get_birthdays_from_sheet(init_sheet())
    else:
        with open (filename, 'rb') as fp:
            list_of_birthday = pickle.load(fp)

    recent = get_recent_birthdays(list_of_birthday, months_from_today)
    output = "Birthdays in next {} month(s):\n".format(months_from_today)
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


def get_attendance_from_sheet(sheet):
    result = sheet.values().get(spreadsheetId=ATTENDANCE_SHEET_ID,
                                range=ATTENDANCE_RANGE).execute()
    
    full_attendance_sheet = result.get('values', [])
    # print(json.dumps(values, indent=4))
    for i in range(2,30):
        print("{}: {}", full_attendance_sheet[1], full_attendance_sheet[2])
    return full_attendance_sheet


print("11 month")
print(get_recent_birthdays_reply(2))

print("6 month")
print(get_recent_birthdays_reply(6))

print("12 month")
print(get_recent_birthdays_reply(12))

print("25 month")
print(get_recent_birthdays_reply(25))