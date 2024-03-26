from pyrogram import Client, filters
import requests
import json

def send_message(message, text):
    message.reply_text(text)


@Client.on_message(filters.command("phone"))
def check_phone(client, message):
    try:
        args = message.text.split(None, 1)
        information = args[1]
        number = information
        key = "f66950368a61ebad3cba9b5924b4532d"
        api = (
            "http://apilayer.net/api/validate?access_key="
            + key
            + "&number="
            + number
            + "&country_code=&format=1"
        )
        output = requests.get(api)
        content = output.text
        obj = json.loads(content)
        country_code = obj["country_code"]
        country_name = obj["country_name"]
        location = obj["location"]
        carrier = obj["carrier"]
        line_type = obj["line_type"]
        validornot = obj["valid"]
        aa = "Valid: " + str(validornot)
        a = "Phone number: " + str(number)
        b = "Country: " + str(country_code)
        c = "Country Name: " + str(country_name)
        d = "Location: " + str(location)
        e = "Carrier: " + str(carrier)
        f = "Device: " + str(line_type)
        g = f"{aa}\n{a}\n{b}\n{c}\n{d}\n{e}\n{f}"
        send_message(message, g)
    except Exception as e:
        send_message(message, f"Error: {str(e)}")
