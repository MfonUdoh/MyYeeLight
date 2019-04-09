import requests
from bs4 import BeautifulSoup
from yeelight import *
import datetime
bulb = Bulb("192.168.0.16")


def grab_location_data():
  """Gets the weather and astrological data for your location from BBC Weather"""

  print ('Enter the first half of your post code')
  post_code = 'b24'
  url = 'https://www.bbc.co.uk/weather/' + post_code
  r = requests.get(url)
  soup = BeautifulSoup(r.text, 'html.parser')
  
  def sun_data(self):
    #Collect sunrise and sunset data
    astro = soup.find_all(
      'span', class_='wr-c-astro-data__time'
      )
    sun = []
  
    for tag in range(len(astro)):
      sun.append(astro[tag].getText())
    return sun

  def weather_data(soup):
    #Collect the weather condition for each time slot of the day
    timeslots = soup.find_all(class_="wr-time-slot wr-js-time-slot")
    weather_today = {} 

    for timeslot in timeslots:
      for tag in timeslot.find_all('span', class_='wr-time-slot-primary__hours'):
        time = (tag.getText())
      for tag in timeslot.find_all('div', class_='wr-weather-type__icon'):
        weathertype = tag.get('title')
      weather_today.update({
        time    :   weathertype
        })
    return weather_today
  sun = sun_data(soup)
  weather = weather_data(soup)
  return [sun, weather]
  
  


Mode = {
  "Day"   :   0,
  "Eve"   :   1,
  "Night" :   2
}

Condition = {
  "Sunny"           :   0,
  "Sunny Intervals" :   1,
  "Light Cloud"     :   2,
}

def Current_YeeState():
  now = datetime.datetime.now()
  (sun, weather) = grab_location_data()
  (h, m) = sun[0].split(":")
  sunrise = int(h) * 3600 + int(m) * 60
  (h, m) = sun[1].split(":")
  sunset = int(h) * 3600 + int(m) * 60
  timenow = now.hour * 3600 + now.minute * 60 + now.second
  
  if timenow < sunrise or (23*3600) < timenow:
    modestate = Mode["Night"]
  elif timenow < sunset:
    modestate = Mode["Day"]
  else:
    modestate = Mode["Eve"]

  if now.hour < 22:
    nicetime = str(now.hour - 2)
  else:
    nicetime = str(0) + str(now.hour - 22)

  weatherstate = weather[nicetime]

  if modestate == 0:
    bulb.turn_on()
    bulb.set_color_temp(3600)
    if weatherstate == 'Light Cloud':
      bulb.set_brightness(70)
    if weatherstate == 'Sunny Intervals':
      bulb.set_brightness(40)
    if weatherstate == 'Sunny':
      bulb.set_brightness(10)
  elif modestate == 1:
    bulb.turn_on()
    bulb.set_brightness(60)
    bulb.set_color_temp(3200)
  else:
    bulb.turn_off()


# Current_YeeState()
bulb.turn_on()
transitions = [
    TemperatureTransition(3200, duration=1000),

]

flow = Flow(
    count=1,
    action=Flow.actions.stay,
    transitions=transitions
)
bulb.start_flow(flow)

#need to creat a function that computes the yeelight state for each time
#funtion that takes previous function and writes a yeelight flow based on that data
#tell yeelight to use that flow

# So the basic idea is to use the astro data and weather data to figure out what state the light should be in at any given time of the day and then creat a flow schedule that will be uploaded to the light and configure it for the coming week. 
# For example, in the middle of the day when it is sunny outside the light should be off, if it is sunny intermittently it should be on low brightness, if it is cloudy then the light should be on but on medium brightness, if it is night time then it should come on fully.

#{'06:24': '19:55', '06:22': '19:57', '06:20': '19:58', '06:17': '20:00', '06:15': '20:02', '06:13': '20:04', '06:10': '20:05', '06:08': '20:07', '06:06': '20:09', '06:04': '20:11', '06:02': '20:12', '06:00': '20:14', '05:57': '20:16', '05:55': '20:18'}
#{'12': 'Light Cloud', '13': 'Light Cloud', '14': 'Light Cloud', '15': 'Light Cloud', '16': 'Sunny Intervals', '17': 'Sunny Intervals', '18': 'Sunny Intervals', '19': 'Sunny Intervals', '20': 'Partly Cloudy', '21': 'Partly Cloudy', '22': 'Partly Cloudy', '23': 'Light Cloud', '00': 'Light Cloud', '01': 'Light Cloud', '02': 'Partly Cloudy', '03': 'Partly Cloudy', '04': 'Partly Cloudy', '05': 'Partly Cloudy'}
