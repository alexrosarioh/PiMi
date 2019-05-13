import requests
from datetime import datetime
from newsapi import NewsApiClient
from time import sleep
from websocket_server import WebsocketServer
import json
import time
import RPi.GPIO as GPIO
import dht11

#A lot of imports, yes. If you're not using any sensors, it's OK to get rid of the RPi.GPIO,
#dht11 imports.

#Init websocket server
server = WebsocketServer(9001)

#Working on the DHT11 sensor.
#If not using the sensor this entire section can be removed.
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

#initializing GPIO for LEDs
RED = 27
GREEN = 23
BLUE = 22
GPIO.setup(27,GPIO.OUT)
GPIO.output(27,GPIO.LOW)
GPIO.setup(23,GPIO.OUT)
GPIO.output(23,GPIO.LOW)
GPIO.setup(22,GPIO.OUT)
GPIO.output(22,GPIO.LOW)

#Read data using GPIO17
instance = dht11.DHT11(pin=7)

#News API call
newsapi = NewsApiClient(api_key='fa739f913c7145f38f1a8f38a8bc38fd')

# API call for OpenWeatherMap
url2 = ('https://api.openweathermap.org/data/2.5/weather?'
        'id=4568138&'
        'appid=181d056f91807f0c91ad51461270cba6&'
        'units=imperial')

wx_response = requests.get(url2)

wx_dict = dict(wx_response.json())
news_dict = newsapi.get_top_headlines(language='en',
                                      country='us')
def run():
    while True:
        result = instance.read()
        if result.is_valid():
            room_temp = "Current: %d F" % ((result.temperature * 9/5)+32)
            room_hum = "Current: %d F" % result.humidity

        wx_city = "Current weather in " + wx_dict["name"]
        wx_desc = wx_dict["weather"][0]["description"]
        wx_desc = wx_desc.capitalize()
        act_wx = str(wx_dict["main"]["temp"]) + " degrees Fahrenheit."
        wx_max_temp = "High: " + str(wx_dict["main"]["temp_max"]) + "degF."
        wx_min_temp = "Low: " + str(wx_dict["main"]["temp_min"]) + "degF."

        current_time = datetime.now()
        current_time = current_time.strftime('%d %b %Y  %H:%M')

        #Turn on LEDs

        GPIO.output(27, GPIO.HIGH)
        GPIO.output(23, GPIO.HIGH)
        GPIO.output(22, GPIO.HIGH)

        news_titles = ['0', '0', '0']

        for x in range(0,3):
            news_titles[x] = news_dict["articles"][x]["title"]

        data = {"wx_city": wx_city,
                "wx_desc": wx_desc,
                "act_wx": act_wx,
                "wx_max_temp": wx_max_temp,
                "wx_min_temp": wx_min_temp,
                "current_time": current_time,
                "news_titles": news_titles,
                "room_temp" : room_temp,
                "room_hum": room_hum}
        server.send_message_to_all(json.dumps(data))
        print("hi")
        sleep(60)

def new_client(client, server):
    run()

server.set_fn_new_client(new_client)
server.run_forever()
GPIO.output(27, GPIO.LOW)
GPIO.output(23, GPIO.LOW)
GPIO.output(22, GPIO.LOW)