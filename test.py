from pyowm import OWM

owm = OWM('123.123.123.123')

while True:
    try:
        place = input('What city do you want to know the weather in? Enter correct city name: ')
        monitoring = owm.weather_manager().weather_at_place(place)
        weather = monitoring.weather
        status = weather.detailed_status
        print(f'It is {status} in {place} now.')
        break
    except:
        pass