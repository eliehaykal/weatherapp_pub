import requests
import time
import datetime
from flask import Flask, render_template, url_for, request, escape
from requests.exceptions import HTTPError

app = Flask(__name__)


@app.route('/viewlog')
def view_the_log():
    # with open('vsearch.log') as log:
    #     contents = log.read()
    # return escape(contents)
    contents = []
    with open('vsearch.log') as log:
        for line in log:
            contents.append([])
            for item in line.split('|'):
                contents[-1].append(escape(item))
    print("Content List is:", contents)
    titles = ('Form Data', 'Remote_addr', 'User Agent', 'Lat/Long')
    # return str(contents)
    return render_template('viewlog.html',
                           the_title='View Log',
                           the_row_titles=titles,
                           the_data=contents,)


@app.route('/')
def index():
    return render_template('index.html')
    # return render_template('oops.html')


@app.route('/getweather', methods=["POST"])
def getweather():
    city = "none"
    longtitude = "none"
    latitude = "none"
    if(request.form['long'] != '' and request.form['lat'] != ''):
        longtitude = request.form['long']
        latitude = request.form['lat']

    print(latitude, longtitude, city)
####################################################
## Helper Functions ##

    def log_request(req, latitude, longtitude):
        with open('vsearch.log', 'a') as log:
            print(req.form, req.remote_addr, req.user_agent, latitude, longtitude,
                  file=log, sep='|')  # req attributes checked using print(str(dir(req)))

    def getCurrentDateDay(epochDate):
        # timeStr = time.strftime('%Y-%m-%d - %A', time.localtime(epochDate))
        timeStr = time.strftime('%a (%d/%m) %H:%M:%S',
                                time.localtime(epochDate))
        # Full Documentation: https://docs.python.org/2/library/time.html#time.strftime
        return timeStr

    def getCurrentDateOpenWeather(epochDate):
        # timeStr = time.strftime('%Y-%m-%d - %A', time.localtime(epochDate))
        timeStr = time.strftime('%a', time.localtime(epochDate)) + " -- " + time.strftime('%H:%M', time.localtime(epochDate))
        # Full Documentation: https://docs.python.org/2/library/time.html#time.strftime
        return timeStr    

    def getCurrentDateDayLineGraph(epochDate):
        # timeStr = time.strftime('%Y-%m-%d - %A', time.localtime(epochDate))
        timeStr = "-" + time.strftime('%a', time.localtime(epochDate)) + \
            " - " + time.strftime('%H:%M', time.localtime(epochDate))
        # Full Documentation: https://docs.python.org/2/library/time.html#time.strftime
        return timeStr

    def getTimeFromEpoch(epochDate):
        timeStr = time.strftime('%H:%M:%S', time.localtime(epochDate))
        return timeStr

    def roundNumbers(number):
        number = round(number)
        return number

    def averageDailyTemperature():
        averageDailyTemperatureValue = float(darkSky["currentTemperature"]) + float(
            weatherStack["wsFeelsLike"]) + float(climaCell["ccDay1FeelsLike"])
        averageDailyTemperatureValue = averageDailyTemperatureValue / 3
        return roundNumbers(averageDailyTemperatureValue)

    def averageDailyHumidity():
        averageDailyHumidityValue = float(darkSky["currentHumidity"]) + float(
            darkSky["dailyHumidity"]) + float(weatherStack['wsHumidity'])
        averageDailyHumidityValue = averageDailyHumidityValue / 3
        return roundNumbers(averageDailyHumidityValue)

    def averageChanceOfRain():
        averageChanceOfRainValue = float(
            darkSky['currentRainChance']) + float(darkSky['dailyRainChance'])
        averageChanceOfRainValue = averageChanceOfRainValue / 2
        return roundNumbers(averageChanceOfRainValue)

    def percentageValueFix(precipProbability):
        precipProbability = round(int(precipProbability * 100))
        return precipProbability


####################################################
# OPENWEATHERMAP
    try:
        openweathermapURL_Coord = 'https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&appid=bbe70a05814d1c2af5d001cb57b44910&units=metric'
        openweatherRes = requests.get(
            openweathermapURL_Coord.format(latitude, longtitude))
        openweatherRes.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
        return render_template('oops.html')
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
        return render_template('oops.html')
    else:
        print('OpenWeather Success!')
        openweatherRes = openweatherRes.json()

    # print("OpenWeatherRes: ", openweatherRes)
    # Check for error in request
    # openweatherResText = str(openweatherRes)
    # print("OpenWeather Text: ", openweatherResText)

    openWeatherList = []

    class C_OpenWeatherMap:
        EpochDate = ""
        Temp = ""
        TempMin = ""
        TempMax = ""
        Humidity = ""
        Weather = ""
        WeatherDescription = ""

    # print("Number of items in OpenWeather List:", len(openweatherRes['list']))
    # if(skipAccuWeather == False and len(accuWeatherRes['DailyForecasts']) != 0):
    offSet = 0
    for number in range(len(openweatherRes['list'])):
        if(offSet < 40):  # 40 entries in list and need 10 items
            # print("offset:",offSet)
            OpenWeatherMapObject = C_OpenWeatherMap()
            OpenWeatherMapObject.EpochDate = getCurrentDateOpenWeather(
                openweatherRes['list'][offSet]['dt'])
            OpenWeatherMapObject.Temp = roundNumbers(
                openweatherRes['list'][offSet]['main']['temp'])
            OpenWeatherMapObject.MinTemp = roundNumbers(
                openweatherRes['list'][offSet]['main']['temp_min'])
            OpenWeatherMapObject.MaxTemp = roundNumbers(
                openweatherRes['list'][offSet]['main']['temp_max'])
            OpenWeatherMapObject.Humidity = roundNumbers(
                openweatherRes['list'][offSet]['main']['humidity'])
            OpenWeatherMapObject.Weather = openweatherRes['list'][offSet]['weather'][0]['main']
            OpenWeatherMapObject.WeatherDescription = openweatherRes[
                'list'][offSet]['weather'][0]['description']
            # print(OpenWeatherMapObject.Weather)
            offSet += 1
            # print("\nPrinting openweather object: ",OpenWeatherMapObject)

            openWeatherList.append(OpenWeatherMapObject)

    # Forecast
    openWeatherMap = {
        'day1Date': getCurrentDateDay(openweatherRes['list'][4]['dt']),
        'day1Temp': roundNumbers(openweatherRes['list'][4]['main']['temp']),
        'day1Min': roundNumbers(openweatherRes['list'][4]['main']['temp_min']),
        'day1Max': roundNumbers(openweatherRes['list'][4]['main']['temp_max']),
        'day1Humidity': roundNumbers(openweatherRes['list'][4]['main']['humidity']),
        'day1Weather': openweatherRes['list'][4]['weather'][0]['main'],
        'day1WeatherDescription': openweatherRes['list'][4]['weather'][0]['description'],
        'day2Date': getCurrentDateDay(openweatherRes['list'][6]['dt']),
        'day2Min': roundNumbers(openweatherRes['list'][6]['main']['temp_min']),
        'day2Max': roundNumbers(openweatherRes['list'][6]['main']['temp_max']),
        'day2Humidity': roundNumbers(openweatherRes['list'][6]['main']['humidity']),
        'day2Temp': roundNumbers(openweatherRes['list'][6]['main']['temp']),
        'day2Weather': openweatherRes['list'][6]['weather'][0]['main'],
        'day2WeatherDescription': openweatherRes['list'][6]['weather'][0]['description'],
        'day3Date': getCurrentDateDay(openweatherRes['list'][9]['dt']),
        'day3Min': roundNumbers(openweatherRes['list'][9]['main']['temp_min']),
        'day3Max': roundNumbers(openweatherRes['list'][9]['main']['temp_max']),
        'day3Humidity': roundNumbers(openweatherRes['list'][9]['main']['humidity']),
        'day3Temp': roundNumbers(openweatherRes['list'][9]['main']['temp']),
        'day3Weather': openweatherRes['list'][9]['weather'][0]['main'],
        'day3WeatherDescription': openweatherRes['list'][9]['weather'][0]['description'],
        'day4Date': getCurrentDateDay(openweatherRes['list'][13]['dt']),
        'day4Min': roundNumbers(openweatherRes['list'][13]['main']['temp_min']),
        'day4Max': roundNumbers(openweatherRes['list'][13]['main']['temp_max']),
        'day4Humidity': roundNumbers(openweatherRes['list'][13]['main']['humidity']),
        'day4Temp': roundNumbers(openweatherRes['list'][13]['main']['temp']),
        'day4Weather': openweatherRes['list'][13]['weather'][0]['main'],
        'day4WeatherDescription': openweatherRes['list'][13]['weather'][0]['description'],
        'day5Date': getCurrentDateDay(openweatherRes['list'][16]['dt']),
        'day5Min': roundNumbers(openweatherRes['list'][16]['main']['temp_min']),
        'day5Max': roundNumbers(openweatherRes['list'][16]['main']['temp_max']),
        'day5Humidity': roundNumbers(openweatherRes['list'][16]['main']['humidity']),
        'day5Temp': roundNumbers(openweatherRes['list'][16]['main']['temp']),
        'day5Weather': openweatherRes['list'][16]['weather'][0]['main'],
        'day5WeatherDescription': openweatherRes['list'][16]['weather'][0]['description'],
        'day6Date': getCurrentDateDay(openweatherRes['list'][20]['dt']),
        'day6Min': roundNumbers(openweatherRes['list'][20]['main']['temp_min']),
        'day6Max': roundNumbers(openweatherRes['list'][20]['main']['temp_max']),
        'day6Humidity': roundNumbers(openweatherRes['list'][20]['main']['humidity']),
        'day6Temp': roundNumbers(openweatherRes['list'][20]['main']['temp']),
        'day6Weather': openweatherRes['list'][20]['weather'][0]['main'],
        'day6WeatherDescription': openweatherRes['list'][20]['weather'][0]['description'],
        'day7Date': getCurrentDateDay(openweatherRes['list'][24]['dt']),
        'day7Min': roundNumbers(openweatherRes['list'][24]['main']['temp_min']),
        'day7Max': roundNumbers(openweatherRes['list'][24]['main']['temp_max']),
        'day7Humidity': roundNumbers(openweatherRes['list'][24]['main']['humidity']),
        'day7Temp': roundNumbers(openweatherRes['list'][24]['main']['temp']),
        'day7Weather': openweatherRes['list'][24]['weather'][0]['main'],
        'day7WeatherDescription': openweatherRes['list'][24]['weather'][0]['description']
    }
    # print('openweathermap object' , openWeatherMap)
####################################################


####################################################
    # Darksky: xxxxxx
    # 33.875558399999996, 35.5237888
    # Documentation: https://darksky.net/dev/docs#forecast-request

    # epochTime = int(time.time())
    # darkskyURL = "https://api.darksky.net/forecast/xxxxxx/33.875558399999996,35.5237888,{}?units=si"
    # darkskyURL = "https://api.darksky.net/forecast/xxxxxx/{},{},{}?units=si"
    # darkskyRes = requests.get(darkskyURL.format(latitude,longtitude,epochTime)).json()
    # print("Darksky URL: ", darkskyURL.format(latitude,longtitude,epochTime))
    # print("############################")
    # print("Darksky Response: ", darkskyRes)

    try:
        epochTime = int(time.time())
        darkskyURL = "https://api.darksky.net/forecast/xxxxxx/{},{},{}?units=si"
        darkskyRes = requests.get(darkskyURL.format(
            latitude, longtitude, epochTime))
        darkskyRes.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
        return render_template('oops.html')
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
        return render_template('oops.html')
    else:
        print('DarkSky Success!')
        darkskyRes = darkskyRes.json()
        # print("Darksky Response: ", darkskyRes)

    darkSky = {
        "currentSummary": darkskyRes['currently']['summary'],
        "currentTemperature": roundNumbers(darkskyRes['currently']['temperature']),
        "currentHumidity": roundNumbers(percentageValueFix(darkskyRes['currently']['humidity'])),
        "currentWindSpeed": darkskyRes['currently']['windSpeed'],
        "currentWindGust": darkskyRes['currently']['windGust'],
        "currentuvIndex": darkskyRes['currently']['uvIndex'],
        "currentRainChance": roundNumbers(percentageValueFix(darkskyRes['currently']['precipProbability'])),
        "currentCloudCover": roundNumbers(percentageValueFix(darkskyRes['currently']['cloudCover'])),
        # "currentRainType":darkskyRes['currently']['precipType'],
        "hourlySummaryH1": darkskyRes['hourly']['data'][5]['summary'],
        "hourlyRainChanceH1": percentageValueFix(darkskyRes['hourly']['data'][5]['precipProbability']),
        "hourlyTemperatureH1": roundNumbers(darkskyRes['hourly']['data'][5]['temperature']),
        "hourlyHumidityH1": percentageValueFix(darkskyRes['hourly']['data'][5]['humidity']),
        "hourlyWindSpeedH1": darkskyRes['hourly']['data'][5]['windSpeed'],
        "hourlyWindGustH1": darkskyRes['hourly']['data'][5]['windGust'],
        "hourlyuvIndexH1": darkskyRes['hourly']['data'][5]['uvIndex'],
        "hourlySummaryH2": darkskyRes['hourly']['data'][9]['summary'],
        "hourlyRainChanceH2": percentageValueFix(darkskyRes['hourly']['data'][9]['precipProbability']),
        "hourlyTemperatureH2": roundNumbers(darkskyRes['hourly']['data'][9]['temperature']),
        "hourlyHumidityH2": percentageValueFix(darkskyRes['hourly']['data'][9]['humidity']),
        "hourlyWindSpeedH2": darkskyRes['hourly']['data'][9]['windSpeed'],
        "hourlyWindGustH2": darkskyRes['hourly']['data'][9]['windGust'],
        "hourlyuvIndexH2": darkskyRes['hourly']['data'][9]['uvIndex'],
        "hourlySummaryH3": darkskyRes['hourly']['data'][15]['summary'],
        "hourlyRainChanceH3": percentageValueFix(darkskyRes['hourly']['data'][15]['precipProbability']),
        "hourlyTemperatureH3": roundNumbers(darkskyRes['hourly']['data'][15]['temperature']),
        "hourlyHumidityH3": percentageValueFix(darkskyRes['hourly']['data'][15]['humidity']),
        "hourlyWindSpeedH3": darkskyRes['hourly']['data'][15]['windSpeed'],
        "hourlyWindGustH3": darkskyRes['hourly']['data'][15]['windGust'],
        "hourlyuvIndexH3": darkskyRes['hourly']['data'][15]['uvIndex'],
        "hourlySummaryH4": darkskyRes['hourly']['data'][20]['summary'],
        "hourlyRainChanceH4": percentageValueFix(darkskyRes['hourly']['data'][20]['precipProbability']),
        "hourlyTemperatureH4": roundNumbers(darkskyRes['hourly']['data'][20]['temperature']),
        "hourlyHumidityH4": percentageValueFix(darkskyRes['hourly']['data'][20]['humidity']),
        "hourlyWindSpeedH4": darkskyRes['hourly']['data'][20]['windSpeed'],
        "hourlyWindGustH4": darkskyRes['hourly']['data'][20]['windGust'],
        "hourlyuvIndexH4": darkskyRes['hourly']['data'][20]['uvIndex'],
        "dailySummary": darkskyRes['daily']['data'][0]['summary'],
        "dailyTempHigh": roundNumbers(darkskyRes['daily']['data'][0]['temperatureHigh']),
        "dailyTempLow": roundNumbers(darkskyRes['daily']['data'][0]['temperatureLow']),
        "dailyRainChance": roundNumbers(percentageValueFix(darkskyRes['daily']['data'][0]['precipProbability'])),
        # "dailyRainType":darkskyRes['daily']['data'][0]['precipType'],
        "dailyHumidity": roundNumbers(percentageValueFix(darkskyRes['daily']['data'][0]['humidity'])),
        "dailyDewPoint": roundNumbers(darkskyRes['daily']['data'][0]['dewPoint']),
        "dailyWindSpeed": roundNumbers(darkskyRes['daily']['data'][0]['windSpeed']),
        "dailyWindGust": roundNumbers(darkskyRes['daily']['data'][0]['windGust']),
        "dailyCloudCover": roundNumbers(percentageValueFix(darkskyRes['daily']['data'][0]['cloudCover'])),
        "dailyMoonPhase": darkskyRes['daily']['data'][0]['moonPhase'],
        "dailySunrise": getTimeFromEpoch(darkskyRes['daily']['data'][0]['sunriseTime']),
        "dailySunset": getTimeFromEpoch(darkskyRes['daily']['data'][0]['sunsetTime'])
    }
    # print('Darksky object', darkSky)

##################WEATHERSTACK##################################

    # Weatherstack: xxxxxx (FREE PLAN: only current weather)
    # Documentation: https://weatherstack.com/documentation#query_parameter
    # weatherstackURL = "http://api.weatherstack.com/current?access_key=xxxxxx&&query=33.875558399999996,35.5237888&forecast_days=0&hourly=0&units=m"
    # weatherStackRes = requests.get(weatherstackURL).json()

    try:
        weatherstackURL = "http://api.weatherstack.com/current?access_key=xxxxxx&&query={},{}&units=m"
        weatherStackRes = requests.get(
            weatherstackURL.format(latitude, longtitude))
        weatherStackRes.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
        return render_template('oops.html')
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
        return render_template('oops.html')
    else:
        print('WeatherStack Success!')
        weatherStackRes = weatherStackRes.json()

    # weatherstackURL = "http://api.weatherstack.com/current?access_key=xxxxxx&&query={},{}&forecast_days=5&hourly=0&units=m"
    weatherstackURL = "http://api.weatherstack.com/current?access_key=xxxxxx&&query={},{}&units=m"
    weatherStackRes = requests.get(
        weatherstackURL.format(latitude, longtitude)).json()
    # print("############################")
    # print("WeatherStack: ", weatherStackRes)
    weatherStack = {
        "wsTemperature": '-',
        "wsFeelsLike": '-',
        "wsWeatherIcon": '-',
        "wsWeatherDescription": '-',
        "wsWindSpeed": '-',
        "wsWindDirection": '-',
        "wsPrecipitation": '-',
        "wsHumidity": '-',
        "wsPressure": '-',
        "wsCloudCover": '-',
        "wsVisibility": '-',
        "wsUVIndex": '-',
        "wsGeoName": '-',
        "wsGeoCountry": '-',
        "wsGeoRegion": '-'
    }
    weatherStack = {
        "wsTemperature": weatherStackRes['current']['temperature'],
        "wsFeelsLike": weatherStackRes['current']['feelslike'],
        "wsWeatherIcon": weatherStackRes['current']['weather_icons'][0],
        "wsWeatherDescription": weatherStackRes['current']['weather_descriptions'][0],
        "wsWindSpeed": weatherStackRes['current']['wind_speed'],
        "wsWindDirection": weatherStackRes['current']['wind_dir'],
        "wsPrecipitation": weatherStackRes['current']['precip'],
        "wsHumidity": weatherStackRes['current']['humidity'],
        "wsPressure": weatherStackRes['current']['pressure'],
        "wsCloudCover": weatherStackRes['current']['cloudcover'],
        "wsVisibility": weatherStackRes['current']['visibility'],
        "wsUVIndex": weatherStackRes['current']['uv_index'],
        "wsGeoName": weatherStackRes['location']['name'],
        "wsGeoCountry": weatherStackRes['location']['country'],
        "wsGeoRegion": weatherStackRes['location']['region'],
    }
    # print("############################")
    # print("WeatherStack Object\n", weatherStack)

######################CLIMACELL##############################

    endDate = datetime.date.today() + datetime.timedelta(days=5)
    # print("End Date is: ", endDate)

    try:
        # Daily
        climacellDailyURL = "https://api.climacell.co/v3/weather/forecast/daily"
        querystringDaily = {"unit_system": "si", "start_time": "now", "end_time": endDate,
                            "fields": "temp,precipitation,feels_like,wind_speed,moon_phase,weather_code",
                            "apikey": "xxxxxx", "lat": latitude, "lon": longtitude}
        climaCellRes = requests.request(
            "GET", climacellDailyURL, params=querystringDaily)
        climaCellRes.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
        return render_template('oops.html')
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
        return render_template('oops.html')
    else:
        print('ClimaCell Daily Success!')
        climaCellRes = climaCellRes.json()
        # print("ClimacellRes: ", climaCellRes)

    try:
        # Realtime
        climacellRealtimeURL = "https://api.climacell.co/v3/weather/realtime"
        querystringRealtime = {"unit_system": "si", "apikey": "xxxxxx", "lat": latitude, "lon": longtitude,
                               "fields": "temp,feels_like,dewpoint,humidity,wind_speed,precipitation,precipitation_type,epa_primary_pollutant,epa_aqi,pollen_tree,epa_health_concern,moon_phase,weather_code"}
        climaCellRealTimeRes = requests.request(
            "GET", climacellRealtimeURL, params=querystringRealtime)
        climaCellRealTimeRes.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
        return render_template('oops.html')
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
        return render_template('oops.html')
    else:
        print('ClimaCell Realtime Success!')
        climaCellRealTimeRes = climaCellRealTimeRes.json()
        # print("climaCellRealTimeRes: ", climaCellRealTimeRes)

    # Daily
    # climacellDailyURL = "https://api.climacell.co/v3/weather/forecast/daily"
    # querystringDaily = {"unit_system":"si","start_time":"now","end_time":endDate,
    # "fields":"temp,precipitation,feels_like,wind_speed,moon_phase,weather_code",
    # "apikey":"xxxxxx", "lat":latitude, "lon":longtitude}
    # climaCellRes = requests.request("GET", climacellDailyURL, params=querystringDaily).json()
    # print("ClimaCell Daily:",climaCellRes)

    # Realtime
    climacellRealtimeURL = "https://api.climacell.co/v3/weather/realtime"
    querystringRealtime = {"unit_system": "si", "apikey": "xxxxxx", "lat": latitude, "lon": longtitude,
                           "fields": "temp,feels_like,dewpoint,humidity,wind_speed,precipitation,precipitation_type,epa_primary_pollutant,epa_aqi,pollen_tree,epa_health_concern,moon_phase,weather_code"}
    climaCellRealTimeRes = requests.request(
        "GET", climacellRealtimeURL, params=querystringRealtime).json()

    # print("CCRES Realtime" , climaCellRealTimeRes)

    climaCell = {
        "ccDay1ObservationTime": climaCellRes[0]['temp'][0]['observation_time'],
        "ccDay1MinTemp": roundNumbers(climaCellRes[0]['temp'][0]['min']['value']),
        "ccDay1MaxTemp": roundNumbers(climaCellRes[0]['temp'][1]['max']['value']),
        "ccDay1Precip": roundNumbers(climaCellRes[0]['precipitation'][0]['max']['value']),
        "ccDay1FeelsLike": roundNumbers(climaCellRes[0]['feels_like'][0]['min']['value']),
        "ccDay1WindSpeed": roundNumbers(climaCellRes[0]['wind_speed'][1]['max']['value']),
        "ccDay1MoonPhase": climaCellRes[0]['moon_phase']['value'],
        "ccDay2ObservationTime": climaCellRes[1]['temp'][0]['observation_time'],
        "ccDay2MinTemp": roundNumbers(climaCellRes[1]['temp'][0]['min']['value']),
        "ccDay2MaxTemp": roundNumbers(climaCellRes[1]['temp'][1]['max']['value']),
        "ccDay2Precip": roundNumbers(climaCellRes[1]['precipitation'][0]['max']['value']),
        "ccDay2FeelsLike": roundNumbers(climaCellRes[1]['feels_like'][0]['min']['value']),
        "ccDay2WindSpeed": roundNumbers(climaCellRes[1]['wind_speed'][1]['max']['value']),
        "ccDay2MoonPhase": climaCellRes[1]['moon_phase']['value'],
        "ccDay3ObservationTime": climaCellRes[2]['temp'][0]['observation_time'],
        "ccDay3MinTemp": roundNumbers(climaCellRes[2]['temp'][0]['min']['value']),
        "ccDay3MaxTemp": roundNumbers(climaCellRes[2]['temp'][1]['max']['value']),
        "ccDay3Precip": roundNumbers(climaCellRes[2]['precipitation'][0]['max']['value']),
        "ccDay3FeelsLike": roundNumbers(climaCellRes[2]['feels_like'][0]['min']['value']),
        "ccDay3WindSpeed": roundNumbers(climaCellRes[2]['wind_speed'][1]['max']['value']),
        "ccDay3MoonPhase": climaCellRes[2]['moon_phase']['value'],
        "ccDay4ObservationTime": climaCellRes[3]['temp'][0]['observation_time'],
        "ccDay4MinTemp": roundNumbers(climaCellRes[3]['temp'][0]['min']['value']),
        "ccDay4MaxTemp": roundNumbers(climaCellRes[3]['temp'][1]['max']['value']),
        "ccDay4Precip": roundNumbers(climaCellRes[3]['precipitation'][0]['max']['value']),
        "ccDay4FeelsLike": roundNumbers(climaCellRes[3]['feels_like'][0]['min']['value']),
        "ccDay4WindSpeed": roundNumbers(climaCellRes[3]['wind_speed'][1]['max']['value']),
        "ccDay4MoonPhase": climaCellRes[3]['moon_phase']['value'],
        "ccDay5ObservationTime": climaCellRes[4]['temp'][0]['observation_time'],
        "ccDay5MinTemp": roundNumbers(climaCellRes[4]['temp'][0]['min']['value']),
        "ccDay5MaxTemp": roundNumbers(climaCellRes[4]['temp'][1]['max']['value']),
        "ccDay5Precip": roundNumbers(climaCellRes[4]['precipitation'][0]['max']['value']),
        "ccDay5FeelsLike": roundNumbers(climaCellRes[4]['feels_like'][0]['min']['value']),
        "ccDay5WindSpeed": roundNumbers(climaCellRes[4]['wind_speed'][1]['max']['value']),
        "ccDay5MoonPhase": climaCellRes[4]['moon_phase']['value'],
        "ccDay6ObservationTime": climaCellRes[5]['temp'][0]['observation_time'],
        "ccDay6MinTemp": roundNumbers(climaCellRes[5]['temp'][0]['min']['value']),
        "ccDay6MaxTemp": roundNumbers(climaCellRes[5]['temp'][1]['max']['value']),
        "ccDay6Precip": roundNumbers(climaCellRes[5]['precipitation'][0]['max']['value']),
        "ccDay6FeelsLike": roundNumbers(climaCellRes[5]['feels_like'][0]['min']['value']),
        "ccDay6WindSpeed": roundNumbers(climaCellRes[5]['wind_speed'][1]['max']['value']),
        "ccDay6MoonPhase": climaCellRes[5]['moon_phase']['value'],
        "ccRealtimeTemp": roundNumbers(climaCellRealTimeRes['temp']['value']),
        "ccRealtimeFeelsLike": roundNumbers(climaCellRealTimeRes['feels_like']['value']),
        "ccRealtimeWindSpeed": climaCellRealTimeRes['wind_speed']['value'],
        "ccRealtimeHumidity": roundNumbers(climaCellRealTimeRes['humidity']['value']),
        "ccRealtimeDewPoint": climaCellRealTimeRes['dewpoint']['value'],
        "ccRealtimePrecipitation": climaCellRealTimeRes['precipitation']['value'],
        "ccRealtimeEpaValue": climaCellRealTimeRes['epa_aqi']['value'],
        "ccRealtimeHealthConcern": climaCellRealTimeRes['epa_health_concern']['value'],
        "ccRealtimeMoonPhase": climaCellRealTimeRes['moon_phase']['value'],
        "ccRealtimeWeatherCode": climaCellRealTimeRes['weather_code']['value']
        # "ccRealtimeArea":climaCellRealTimeRes['Getting Accuweather City']['AdministrativeArea']['LocalizedName'],
        # "ccRealtimeCountryID":climaCellRealTimeRes['Getting Accuweather City']['AdministrativeArea']['CountryID'],
        # "ccRealtimeTimeZone":climaCellRealTimeRes['Getting Accuweather City']['AdministrativeArea']['GmtOffset'],
        # "ccRealtimeElevation":climaCellRealTimeRes['Getting Accuweather City']['GeoPosition']['Elevation']['Metric']['Value']
    }
    # print("############################")
    # print(climaCell)
    # print("#MoonPhase is ------------ ", climaCell["ccRealtimeMoonPhase"])


# ACCUWEATHER###############################accuweather: xxxxxx

    try:
        cityURL = "http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=xxxxxx&q={}%2C{}"
        accuweatherURL = "http://dataservice.accuweather.com/forecasts/v1/daily/5day/{}?apikey=xxxxxx&metric=true"
        getCity = requests.get(cityURL.format(latitude, longtitude)).json()
        # print("Getting Accuweather City:", getCity)
        getCityText = str(getCity)
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
        return render_template('oops.html')
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
        return render_template('oops.html')
    else:
        skipAccuWeather = False

        # Code': 'ServiceUnavailable', 'Message': 'The allowed number of requests has been exceeded.', '
        # Reference': '/locations/v1/cities/geoposition/search?apikey=xxxxxx&q=33.893791300000004%2C35.5017767'}
        if('exceeded' not in getCityText):
            accuCityInfo = {
                'accuCityName': getCity['LocalizedName'],
                'accuCountryName': getCity['Country']['LocalizedName'],
                'accuAdministrativeArea': getCity['AdministrativeArea']['LocalizedName'],
                'accuTimeZone': getCity['TimeZone']['GmtOffset'],
                'accuGeoPositionLat': getCity['GeoPosition']['Latitude'],
                'accuGeoPositionLong': getCity['GeoPosition']['Longitude'],
                'accuGeoPositionElevation': getCity['GeoPosition']['Elevation']['Metric']['Value']
            }
            accuWeatherRes = requests.get(
                accuweatherURL.format(getCity)).json()
            # accuWeatherResText = requests.get(accuweatherURL.format(getCity)).text
            accuWeatherResText = str(accuWeatherRes)
            # print("PRINTING ACCUWEATHER #####", accuWeatherRes)
            # print("PRINTING accuWeatherResText #####", accuWeatherResText)
            # Check if api calls are exceeded
            if("exceeded" in accuWeatherResText or "failed" in accuWeatherResText):
                skipAccuWeather = True

            # Error Message
            # {'Code': 'ServiceUnavailable', 'Message': 'The allowed number of requests has been exceeded.',
            # 'Reference': '/locations/v1/cities/geoposition/search?apikey=xxxxxx&q=33.893791300000004%2C35.5017767'}

            # accuWeatherHeadline = {
            #     "accuHeadlineText": accuWeatherRes['Headline']['Text'],
            #     "accuHeadlineCategory": accuWeatherRes['Headline']['Category']
            # }
            accuWeatherList = ['']
            accuWeatherValid = False

            class AccuweatherObject:
                EpochDate = ""
                TempMin = ""
                TempMax = ""
                DaySummary = ""
                NightSummary = ""
                DayHasPrecipitation = ""
                DayPrecipitationType = ""
                DayPrecipitationIntensity = ""
                NightHasPrecipitation = ""
                NightPrecipitationType = ""
                NightPrecipitationIntensity = ""

            # print("SkipAccuWeather?", skipAccuWeather)
            # print("dailyForecast", len(accuWeatherRes['DailyForecasts']))
            # check if we have one item
            if(skipAccuWeather == False and len(accuWeatherRes['DailyForecasts']) != 0):
                for day in range(len(accuWeatherRes['DailyForecasts'])):
                    dayObj = AccuweatherObject()  # Init Object
                    dayObj.EpochDate = getCurrentDateDay(
                        accuWeatherRes['DailyForecasts'][day]['EpochDate'])
                    dayObj.TempMin = accuWeatherRes['DailyForecasts'][day]['Temperature']['Minimum']['Value']
                    dayObj.TempMax = accuWeatherRes['DailyForecasts'][day]['Temperature']['Maximum']['Value']
                    dayObj.DaySummary = accuWeatherRes['DailyForecasts'][day]['Day']['IconPhrase']
                    dayObj.NightSummary = accuWeatherRes['DailyForecasts'][day]['Night']['IconPhrase']
                    dayObj.DayHasPrecipitation = accuWeatherRes[
                        'DailyForecasts'][day]['Day']['HasPrecipitation']

                    # Checking Day Precipitation
                    dayObj.DayHasPrecipitation = accuWeatherRes[
                        'DailyForecasts'][day]['Day']['HasPrecipitation']
                    if accuWeatherRes['DailyForecasts'][day]['Day']['HasPrecipitation'] == True:
                        dayObj.DayPrecipitationType = accuWeatherRes[
                            'DailyForecasts'][day]['Day']['PrecipitationType']
                        dayObj.DayPrecipitationIntensity = accuWeatherRes[
                            'DailyForecasts'][day]['Day']['PrecipitationIntensity']

                    # Checking Night Precipitation
                    dayObj.NightHasPrecipitation = accuWeatherRes[
                        'DailyForecasts'][day]['Night']['HasPrecipitation']
                    if accuWeatherRes['DailyForecasts'][day]['Night']['HasPrecipitation'] == True:
                        dayObj.NightPrecipitationType = accuWeatherRes[
                            'DailyForecasts'][day]['Night']['PrecipitationType']
                        dayObj.NightPrecipitationIntensity = accuWeatherRes[
                            'DailyForecasts'][day]['Night']['PrecipitationIntensity']

                    # Append Object
                    accuWeatherList.append(dayObj)
                    accuWeatherValid = True

                # print(type(accuWeatherList), accuWeatherList, accuWeatherList[0].TempMax)
        else:
            skipAccuWeatherCity = True
            skipAccuWeather = True
            accuCityInfo = {}
            accuWeatherList = ['']
            accuWeatherValid = False


###########################################################
    # Calculate Global Average Values which are displayed at the top of the page
    globalTemp = averageDailyTemperature()
    globalHumidity = averageDailyHumidity()
    globalRainChance = averageChanceOfRain()

    # print("Printing openweatherlist: ",openWeatherList , '## count:', len(openWeatherList))
###########################################################
    # return ""
    # return render_template('weather.html', openWeatherMap=openWeatherMap, darksky=darkSky, weatherStack=weatherStack, climaCell=climaCell, lenAccuWeather = len(accuWeatherList) ,accuWeatherList=accuWeatherList, accuWeatherValid=accuWeatherValid)

    # Generate logs
    log_request(request, latitude, longtitude)

    return render_template(
        'weather.html', openWeatherMap=openWeatherMap, darksky=darkSky,
        weatherStack=weatherStack, climaCell=climaCell, globalTemp=globalTemp,
        globalHumidity=globalHumidity, globalRainChance=globalRainChance,
        lenAccuWeather=len(accuWeatherList), accuWeatherList=accuWeatherList,
        lenOpenWeather=len(openWeatherList), openWeatherList=openWeatherList,
        accuWeatherValid=accuWeatherValid, accuCityInfo=accuCityInfo
    )


if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0', port='8080',ssl_context='adhoc') #turn on debug for compiling changes on the fly
    app.run(debug=True)  # turn on debug for compiling changes on the fly
