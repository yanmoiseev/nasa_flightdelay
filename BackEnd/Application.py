from flask import Flask, request, url_for, jsonify, render_template, redirect
from flask_restful import Api
import requests, xmltodict, geocoder, pytz, geopy
from dateutil import parser
import datetime
from collections import OrderedDict

app = Flask(__name__)
api = Api(app)

#region utility
def latlng(place):  # convert text location to latitude and longitude
    location = geocoder.google(place)  # location
    latitude = location.lat
    longitude = location.lng
    return (latitude, longitude)


def parse_date_time_utc(date_str):
    dt = parser.parse(date_str)

    if dt.tzinfo:
        # convert to utc
        dt = dt.replace(tzinfo=pytz.utc) + dt.tzinfo._offset

    return dt

def get_timezone(place):
   g = geopy.geocoders.GoogleV3()
   return g.timezone(geocoder.google(place).latlng)
#endregion

source_key = 'origin'
destination_key = 'destination'
flightno_key = 'flightno'
airline_key = 'airline'
deptdate_key = 'departuredate'
arvdate_key = 'arrivaldate'
depttime_key = 'departuretime'
arvtime_key = 'arrivaltime'

@app.route('/', methods=['GET'])
def index():
	return render_template('index.html')


@app.route('/find', methods=['GET', 'POST'])  # to accquire source and destination info
def find():
    if request.method == 'POST':
        source = request.form.get(source_key,None)
        destination = request.form.get(destination_key,None)
        flightno = request.form.get(flightno_key,None)
        airline = request.form.get(airline_key,None)
        departdate = request.form.get(deptdate_key,None)
        arrivaldate = request.form.get(arvdate_key,None)
        departtime = request.form.get(depttime_key,None)
        arrivetime = request.form.get(arvtime_key,None)
    else:
        return redirect(url_for('index'))

    source_coordinate = latlng(source)
    dest_coordinate = latlng(destination)
    departure_full_time = '{} {}'.format(departdate, departtime)
    arrive_full_time = '{} {}'.format(arrivaldate, arrivetime)

    departure_begin = parse_date_time_utc(departure_full_time)
    departure_end = departure_begin + datetime.timedelta(seconds=1)
    departure_begin = departure_begin.isoformat().split('+')[0]
    departure_end = departure_end.isoformat().split('+')[0]

    arrival_begin = parse_date_time_utc(arrive_full_time)
    arrival_end = arrival_begin + datetime.timedelta(seconds=1)
    arrival_begin = arrival_begin.isoformat().split('+')[0]
    arrival_end = arrival_end.isoformat().split('+')[0]

    departure_result = get_forecast_weather(source_coordinate[0], source_coordinate[1], departure_begin, departure_end)
    return jsonify(departure_result)
    # arrival_result = get_forecast_weather(dest_coordinate[0], dest_coordinate[1], arrival_begin, arrival_end)
    # return jsonify([departure_result, arrival_result])


####################################
##### make other data available ####
##### handlers for get and put from other endpoints####
@app.route('/ml', methods=['GET', 'POST'])
def sendDataToML():
    ml = [{}]
    return jsonify({'data': ml})



# this one is forming url to get weather data from http://graphical.weather.gov/xml/SOAP_server/ndfdXMLclient.php?
def get_forecast_weather(lat=None, lon=None,
                         begin=None, end=None):
    base_url = 'http://graphical.weather.gov/xml/SOAP_server/ndfdXMLclient.php'
    params = {}
    params['whichClient'] = 'NDFDgen'
    params['lat'] = lat
    params['lon'] = lon
    params['product'] = 'time-series'
    params['begin'] = begin
    params['end'] = end
    params['Unit'] = 'm'
    params['temp'] = 'temp'
    params['snow'] = 'snow'
    params['dew'] = 'dew'
    params['wspd'] = 'wspd'
    params['wdir'] = 'wdir'
    params['sky'] = 'sky'
    params['wx'] = 'wx'
    params['ptornado'] = 'ptornado'
    params['phail'] = 'phail'
    params['pxtornado'] = 'pxtornado'
    params['pxhail'] = 'pxhail'
    params['ptotsvrtstm'] = 'ptotsvrtstm'
    params['pxtotsvrtstm'] = 'pxtotsvrtstm'
    params['wwa'] = 'wwa'
    params['wgust'] = 'wgust'
    params['maxrh'] = 'maxrh'
    params['Submit'] = 'Submit'

    # call the url, and gives request to function to process xml result
    return parse_xml_to_flat_dict(requests.get(base_url, params=params))


def parse_xml_to_flat_dict(request):
    print request.url
    response_dict = xmltodict.parse(request.content)
    print request.content
    response_data = response_dict['dwml']['data']
    response_params = response_data['parameters']
    parsed_result = {}

    lat = response_data['location']['point']['@latitude']
    long = response_data['location']['point']['@longitude']
    parsed_result['location'] = (lat, long)

    temperature = response_params['temperature'][0]['value']
    dew_point = response_params['temperature'][1]['value']
    wind_speed = response_params['wind-speed'][0]['value']
    wind_direction = response_params['direction']['value']
    cloud_cover_amount = response_params['cloud-amount']['value']
    snow_amount = response_params['precipitation']['value']

    probability_severe_thunderstorm = response_params['convective-hazard'][0]['severe-component']['value']
    probability_extreme_severe_thunderstorm = response_params['convective-hazard'][1]['severe-component']['value']

    wind_gust = response_params['wind-speed'][1]['value']
    humidity = response_params['humidity']['value']

    parsed_result['location'] = (lat, long)
    parsed_result['temperature'] = temperature
    parsed_result['dew_point'] = dew_point

    parsed_result['wind_speed'] = wind_speed
    parsed_result['wind_direction'] = wind_direction
    parsed_result['cloud_cover_amount'] = cloud_cover_amount
    parsed_result['snow_amount'] = snow_amount
    parsed_result['probability_severe_thunderstorm'] = probability_severe_thunderstorm
    parsed_result['probability_extreme_severe_thunderstorm'] = probability_extreme_severe_thunderstorm
    parsed_result['wind_gust'] = wind_gust
    parsed_result['humidity'] = humidity

    return parsed_result


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
