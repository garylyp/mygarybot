import os, glob

import urllib.request, json
import datetime
from pprint import pprint



def sendQuery(token, method, arguments = ""):
    url = "https://api.telegram.org/bot{}/{}{}".format(
        token, method, "?" + arguments)
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    return data

def getMostRecentUpdate():
    cwd = os.getcwd()
    update_files = os.path.join(cwd,'updates','*.json')
    update = glob.glob(update_files)
    if (update==[]):
        return None
    else:
        update = update[0]

    with open(update, 'r') as f:
        data = json.loads(f.read())
        return data["result"][-1]

def getUpdates():
    token = "849022219:AAGiMuA93McYGilGhuHJ9-HELGsElqxQZ14"
    data = sendQuery(token, "getUpdates")
    update_id = data["result"][-1]["update_id"]
    recent_id=0;
    most_recent = getMostRecentUpdate()
    if (most_recent != None):
        recent_id = most_recent["update_id"]
        if (update_id == recent_id):
            print('Already up to date. ID = {}'.format(update_id))
            return

    cwd = os.getcwd()
    dt = datetime.datetime.now()
    path = "\\updates\\update_{id}_{0:02d}{1:02d}{2}_{3:02d}{4:02d}{5:02d}.json".format(
        dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, id=update_id)
    filename = cwd + path
    with open(filename, 'w') as f:
            json.dump(data, f)
            print('New update: .{}'.format(path))   





def getChatID():
    update = getMostRecentUpdate()
    print(update["message"]["chat"]["id"])

getUpdates()
getChatID()

# def echo():
    