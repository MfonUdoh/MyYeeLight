import requests
from bs4 import BeautifulSoup
from yeelight import *
import datetime
bulb = Bulb(discover_bulbs()[0]['ip'])


def grab_location_data():
  """Gets the weather and astrological data for your location from BBC Weather"""

  # print ('Enter the first half of your post code') #Just hard coded my location to make testing easier
  post_code = 'b24'
  url = 'https://www.bbc.co.uk/weather/' + post_code
  r = requests.get(url)
  soup = BeautifulSoup(r.text, 'html.parser')
  
  def sun_data(soup):
    """Collect sunrise and sunset data"""
    astro = soup.find_all(
      'span', class_='wr-c-astro-data__time'
      )
    sun = []
  
    for tag in range(len(astro)):
      sun.append(astro[tag].getText())
    return sun

  def weather_data(soup):
    """Collect the weather condition for each time slot of the day"""
    timeslots = soup.find_all(class_="wr-time-slot wr-js-time-slot")
    weather_today = {} 

    for timeslot in timeslots:
      for tag in timeslot.find_all('span', class_='wr-time-slot-primary__hours'):
        time = (tag.getText())
      for tag in timeslot.find_all('div', class_='wr-weather-type__icon'):
        weathertype = tag.get('title')
      
      #Organises the weather at each time into a dictionary
      weather_today.update({
        time    :   weathertype
        })

    return weather_today
  
  #Collects the data from the two functions
  sun = sun_data(soup)
  weather = weather_data(soup)

  return [sun, weather]

#Stores the data so website is only needs one scrapping
(sun, weather) = grab_location_data()

def YeeState(offset, sun, weather):
  """Searches the data and returns the time and weather state given a time offset (hours) from the present (0 = current weather and timestate) for example YeeState(1, sun, weather) might return Clear Sky, Eve"""
  now = datetime.datetime.now()
  
  (h, m) = sun[0].split(":")
  sunrise = int(h) * 3600 + int(m) * 60
  (h, m) = sun[1].split(":")
  sunset = int(h) * 3600 + int(m) * 60
  timenow = (1 + now.hour) * 3600 + now.minute * 60 + now.second
  
  time = timenow + offset*3600

  if sunrise < time < sunset:
    TimeState = "Day"
  elif sunset < time < (23*3600):
    TimeState = "Eve"
  else:
    TimeState = "Night"

  if 10 <= int(time / 3600) < 24:
    nicetime = str(int(time / 3600))
  elif 24 <=  int(time / 3600):
    nicetime = str(0) + str(int(time / 3600) - 24)
  else:
    nicetime = str(0) + str(int(time / 3600))

  
  WeatherState = weather[nicetime]

  return (WeatherState, TimeState)


##### Maybe I can figure out how to nest functions in a dicitonary rather than using an if tree, might make the code look better #####

# ModeDefine = {
#   0 : bulb.turn_off(),
#   1 : (bulb.set_brightness(10), bulb.set_color_temp(3600)),
#   2 : (bulb.set_brightness(40), bulb.set_color_temp(3200)),
#   3 : (bulb.set_brightness(60), bulb.set_color_temp(3200)),
#   4 : (bulb.set_brightness(70), bulb.set_color_temp(3100))
# }


def CreateFlowTransitions():
  """This uses the the time and weather states to write a transition list"""
  transition =[]
  
  # Defines the YeeLight mode based on the time and weather conditions
  ModeSelect = {
  "Day" : {
    "Light Cloud"         : 2,
    "Partly Cloudy"       : 2,
    "Light Rain Showers"  : 2,
    "Light Rain"          : 2,
    "Heavy Rain"          : 3,
    "Rain"                : 3,
    "Sunny Intervals"     : 1,
    "Clear Sky"           : 0,
    "Sunny"               : 0
    },
    "Eve" : {
    "Light Cloud"         : 4,
    "Light Rain Showers"  : 4,
    "Light Rain"          : 4,
    "Heavy Rain"          : 4,
    "Partly Cloudy"       : 4,
    "Rain"                : 4,
    "Sunny Intervals"     : 4,
    "Clear Sky"           : 4,
    "Sunny"               : 4
    },
    "Night" : {
    "Light Cloud"         : 0,
    "Light Rain Showers"  : 0,
    "Light Rain"          : 0,
    "Heavy Rain"          : 0,
    "Partly Cloudy"       : 0,
    "Rain"                : 0,
    "Sunny Intervals"     : 0,
    "Clear Sky"           : 0,
    "Sunny"               : 0
    }
  }
  print("Today's Forecast:")

  if (29 - datetime.datetime.now().hour) < 9:
    runtime = 29 - datetime.datetime.now().hour
  else:
    runtime = 9

  for timeperiod in range(runtime):
    # Asks YeeState for the Time and Weather states for the next few hours, then uses those states to figure out which mode the YeeLight should be in and then writes a transition for this.

    (WeatherState, TimeState) = YeeState(timeperiod, sun, weather)
    print (WeatherState, TimeState)
    ModeDefine = ModeSelect[TimeState][WeatherState]

    #Defines which action the YeeLight should take based on each mode
    if ModeDefine == 0:
      transition.append(TemperatureTransition(3700, duration=(3600000), brightness=10))
    elif ModeDefine == 1:
      transition.append(TemperatureTransition(3600, duration=(3600000), brightness=10))
    elif ModeDefine == 2:
      transition.append(TemperatureTransition(3200, duration=(3600000), brightness=40))
    elif ModeDefine == 3:
      transition.append(TemperatureTransition(3600, duration=(3600000), brightness=60))
    else:
      transition.append(TemperatureTransition(3200, duration=(3600000), brightness=70))
  return transition

transition = CreateFlowTransitions()

              ####Activate when testing####
bulb.turn_on()
flow = Flow(
    count=1,
    action=Flow.actions.off,
    transitions = transition
)
# bulb.set_brightness(100)
bulb.start_flow(flow)
print (bulb.get_properties())
print (transition)