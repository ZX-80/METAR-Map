import board
import busio
i2c = busio.I2C(board.SCL, board.SDA)
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
ads = ADS.ADS1115(i2c)
chan = AnalogIn(ads, ADS.P0) #chan.value, chan.voltage
max_chan_value = 32752.0
print(chan.value, chan.voltage)

import digitalio
button = digitalio.DigitalInOut(board.D4)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

import neopixel
import urllib.request
import xml.etree.ElementTree as ET
#from gpiozero import Button
from time import sleep
import configparser

led_count = 100
config = configparser.ConfigParser()
config.read('metar.ini')
mode_index = config.getint("STATE", "mode")
print("CM:"+str(mode_index))

pixels = neopixel.NeoPixel(board.D18, led_count, brightness = chan.value/max_chan_value, pixel_order = neopixel.GRB, auto_write=False)

def save_ini():
    global mode_index
    print("saving")
    config.set("STATE", "brightness",str(0))
    config.set("STATE", "mode",str(mode_index))
    with open('metar.ini', 'w') as configfile:
        config.write(configfile)

fp = open("/home/pi/airports")
airports = fp.read().split('\n')
fp.close()


url = "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=5&mostRecentForEachStation=true&stationString=" + ",".join([item for item in airports if item != "NULL"])
content = urllib.request.urlopen(url).read()
root = ET.fromstring(content)
stations = {"station_id":"flight_category"}
for metar in root.iter('METAR'):
    station_id = metar.find('station_id').text
    print(station_id+':',end='')
    if metar.find('flight_category')==None:
        print("----",end=' ')
    else:
        stations[station_id] = metar.find('flight_category').text
        print(stations[station_id].ljust(4),end=' ')
print()

weather_was_displayed = False
def display_weather():
    global weather_was_displayed
    if weather_was_displayed: return
    for i, station_id in enumerate(airports):
        if i>=led_count: break
        pixels[i] = {"VFR":(255,0,0),"MVFR":(0,0,255),"IFR":(0,255,0),"LIFR":(0,125,125)}.get(stations.get(station_id, None),(0,0,0))
    weather_was_displayed = True

sins = [127,129,131,134,136,138,140,143,145,147,149,151,154,156,158,160,162,164,166,169,171,173,175,177,179,181,183,185,187,189,191,193,195,196,198,200,202,204,205,207,209,211,212,214,216,217,219,220,222,223,225,226,227,229,230,231,233,234,235,236,237,239,240,241,242,243,243,244,245,246,247,248,248,249,250,250,251,251,252,252,253,253,253,254,254,254,254,254,254,254,255,254,254,254,254,254,254,254,253,253,253,252,252,251,251,250,250,249,248,248,247,246,245,244,243,243,242,241,240,239,237,236,235,234,233,231,230,229,227,226,225,223,222,220,219,217,216,214,212,211,209,207,205,204,202,200,198,196,195,193,191,189,187,185,183,181,179,177,175,173,171,169,166,164,162,160,158,156,154,151,149,147,145,143,140,138,136,134,131,129,127,125,123,120,118,116,114,111,109,107,105,103,100,98,96,94,92,90,88,85,83,81,79,77,75,73,71,69,67,65,63,61,59,58,56,54,52,50,49,47,45,43,42,40,38,37,35,34,32,31,29,28,27,25,24,23,21,20,19,18,17,15,14,13,12,11,11,10,9,8,7,6,6,5,4,4,3,3,2,2,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,2,2,3,3,4,4,5,6,6,7,8,9,10,11,11,12,13,14,15,17,18,19,20,21,23,24,25,27,28,29,31,32,34,35,37,38,40,42,43,45,47,49,50,52,54,56,58,59,61,63,65,67,69,71,73,75,77,79,81,83,85,88,90,92,94,96,98,100,103,105,107,109,111,114,116,118,120,123,125]
mode = ["WEATHER","TEST","KNIGHTRIDER"]
was_released = True
first_run = True
while True:
    pixels.brightness = chan.value/max_chan_value
    #print(chan.value,chan.voltage,pixels.brightness)
    sleep(0.01)
    if (not button.value) and was_released: 
        mode_index = (mode_index+1)%len(mode)
        save_ini()
        was_released = False
    elif (not button.value)==False:
        was_released = True
    if mode[mode_index]=="WEATHER":
        display_weather()
    elif mode[mode_index]=="TEST":
        if weather_was_displayed:
            weather_was_displayed = False
        for i in range(360):
            pixels.brightness = chan.value/max_chan_value
            if (not button.value) and was_released: 
                break
            elif (not button.value)==False:
                was_released = True     
            pixels.fill((sins[i],sins[(i+120)%360],sins[(i+240)%360]))
    elif mode[mode_index]=="KNIGHTRIDER":
        if weather_was_displayed:
            weather_was_displayed = False
        demo_light = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [255, 0, 0], [255, 0, 0], [0, 255, 0], [255, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [255, 0, 0], [255, 0, 0], [0, 255, 0], [255, 0, 0], [0, 0, 0], [255, 0, 0], [0, 0, 0], [255, 0, 0], [0, 0, 0], [0, 0, 255], [0, 0, 0], [0, 0, 0], [0, 0, 255], [0, 0, 0], [0, 255, 0], [0, 0, 0], [0, 255, 0], [0, 0, 0], [0, 255, 0], [0, 255, 0], [0, 0, 0], [0, 255, 0], [0, 0, 0], [255, 0, 0], [255, 0, 0], [255, 0, 0], [255, 0, 0], [255, 0, 0], [255, 0, 0], [255, 0, 0], [0, 0, 0], [255, 0, 0], [255, 0, 0], [0, 0, 0], [255, 0, 0], [0, 0, 0], [255, 0, 0], [255, 0, 0], [255, 0, 0], [0, 0, 0], [255, 0, 0], [255, 0, 0], [0, 0, 255], [0, 0, 0], [255, 0, 0], [0, 0, 0], [255, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [255, 0, 0], [255, 0, 0], [0, 0, 0], [255, 0, 0], [255, 0, 0], [255, 0, 0], [255, 0, 0], [255, 0, 0], [255, 0, 0], [255, 0, 0], [255, 0, 0], [0, 0, 0], [0, 255, 0], [0, 255, 0], [255, 0, 0], [255, 0, 0], [0, 255, 255], [0, 255, 0], [0, 255, 0], [255, 0, 0], [255, 0, 0], [0, 0, 0], [255, 0, 0], [0, 0, 255], [0, 0, 0], [255, 0, 0]]
        for i, light in enumerate(demo_light): pixels[i] = light
    if first_run:
        pixels.show()
        pixels.auto_write=True
        first_run = False


