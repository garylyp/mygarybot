import requests, json
from time import sleep

def get_updates_json(request):
    url = request + "getUpdates"
    response = requests.get(url)
    return response.json()

def get_latest_update(data):
    if len(data['result']) == 0:
        print("No update available")
        return None
    results = data['result']
    return results[-1]

def pretty_print(data, indent=4):
    print(json.dumps(data, indent=indent))

def get_chat_id(update):
    chat_id = update['message']['chat']['id']
    return chat_id

def send_message_to_chat(request, chat_id, text):
    url = "{}sendMessage?chat_id={}&text={}".format(request, chat_id, text)
    response = requests.get(url)
    return response.json()


def get_updates_poll(url):
    latest_update = get_latest_update(get_updates_json(url))
    if (latest_update == None):
        return

    update_id = latest_update['update_id']
    while True:
        if (latest_update == None):
            continue

        if update_id == latest_update['update_id']:
            pretty_print(latest_update)
            echo_text = latest_update['message']['text']
            send_message_to_chat(url, get_chat_id(get_latest_update(get_updates_json(url))), echo_text)
            update_id += 1

        if "end" in echo_text or "stop" in echo_text:
            end_text = "Ending poll"
            send_message_to_chat(url, get_chat_id(get_latest_update(get_updates_json(url))), end_text)
            break

        sleep(1)

def main(): 
    token = "969707375:AAERFhml7PbV6NFzBA0r-5nHSCuXjBRHDmk"
    url = "https://api.telegram.org/bot"
    request_url = url + token + "/"
    get_updates_poll(request_url)
    # pretty_print(get_updates_json(request_url))

    

 
if __name__ == '__main__': 
    main()
 