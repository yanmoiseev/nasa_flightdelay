from flask import Flask, request, url_for, jsonify, render_template, redirect, flash
from flask_restful import Api
import requests, xmltodict, geocoder, pytz, geopy, pickle
from MI import calculate
from dateutil import parser
import datetime
from collections import OrderedDict

# pickle_file = open("lingreg.p",'rb')
# rreg = pickle.load(pickle_file)

app = Flask(__name__)
api = Api(app)


# app.secret_key = 'something'

# region utility
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


# end region

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
@app.route('/find/<probability>')  # to display final delay probability
def find():
    if request.method == 'POST':
        source = request.form.get(source_key, None)
        destination = request.form.get(destination_key, None)
        flightno = request.form.get(flightno_key, None)
        airline = request.form.get(airline_key, None)
        departdate = request.form.get(deptdate_key, None)
        arrivaldate = request.form.get(arvdate_key, None)
        departtime = request.form.get(depttime_key, None)
        arrivetime = request.form.get(arvtime_key, None)
    else:
        return redirect(url_for('index'))

    source_coordinate = latlng(source)
    dest_coordinate = latlng(destination)
    departure_full_time = '{} {}'.format(departdate, departtime)
    arrive_full_time = '{} {}'.format(arrivaldate, arrivetime)

    departure_begin = parse_date_time_utc(departure_full_time)
    departure_end = departure_begin + datetime.timedelta(seconds=1)
    dt = departure_begin
    print 'source: {} coord: {}'.format(source, source_coordinate)
    departure_begin = departure_begin.isoformat().split('+')[0]
    departure_end = departure_end.isoformat().split('+')[0]

    arrival_begin = parse_date_time_utc(arrive_full_time)
    arrival_end = arrival_begin + datetime.timedelta(seconds=1)
    arrival_begin = arrival_begin.isoformat().split('+')[0]
    arrival_end = arrival_end.isoformat().split('+')[0]

    departure_result = get_forecast_weather(source_coordinate[0], source_coordinate[1], departure_begin, departure_end,
                                            dt)
    # probability = rreg.predict([])
    probability = calculate(departure_result)
    return render_template('prediction.html', probability=probability)

    # arrival_result = get_forecast_weather(dest_coordinate[0], dest_coordinate[1], arrival_begin, arrival_end)
    # return jsonify(departure_result)


####################################
##### make other data available ####
##### handlers for get and post####

# this one is forming url to get weather data from http://graphical.weather.gov/xml/SOAP_server/ndfdXMLclient.php?
def get_forecast_weather(lat=None, lon=None,
                         begin=None, end=None, datetime=None):
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
    # params['ptornado'] = 'ptornado'
    # params['phail'] = 'phail'
    # params['pxtornado'] = 'pxtornado'
    # params['pxhail'] = 'pxhail'
    # params['ptotsvrtstm'] = 'ptotsvrtstm'
    # params['pxtotsvrtstm'] = 'pxtotsvrtstm'
    params['wwa'] = 'wwa'
    params['maxrh'] = 'maxrh'
    params['Submit'] = 'Submit'
    return parse_xml_to_flat_dict(requests.get(base_url, params=params), datetime, lat, lon)


def parse_xml_to_flat_dict(request, datetime, lat, lon):
    response_dict = xmltodict.parse(request.content)

    parsed_result = {}
    parsed_list = ['location_lat', 'location_long', 'temperature', 'dew_point', 'wind_speed', 'wind_direction', 'cloud_cover_amount',
                   'snow_amount', 'humidity']

    for para in parsed_list:
        parsed_result.setdefault(para, 0)

    parsed_result['day'] = datetime.weekday()
    parsed_result['location_lat'] = lat
    parsed_result['location_long'] = lon

    try:
        response_data = response_dict['dwml']['data']
        response_params = response_data['parameters']
    except KeyError:
        print 'Exception {}'.format(parsed_result)
        return parsed_result

    def check_if_value_exists(dict):
        return 'value' in dict

    try:
        if 'temperature' in response_params:
            t = response_params['temperature']
            if t[0] and check_if_value_exists(t[0]):
                parsed_result['temperature'] = response_params['temperature'][0]['value']
            if t[1] and check_if_value_exists(t[1]):
                parsed_result['dew_point'] = response_params['temperature'][1]['value']
    except:
        pass

    if 'wind-speed' in response_params and check_if_value_exists(response_params['wind-speed']):
        parsed_result['wind_speed'] = response_params['wind-speed']['value']

    if 'direction' in response_params and check_if_value_exists(response_params['direction']):
        parsed_result['wind_direction'] = response_params['direction']['value']

    if 'cloud-amount' in response_params and check_if_value_exists(response_params['cloud-amount']):
        parsed_result['cloud_cover_amount'] = response_params['cloud-amount']['value']

    if 'precipitation' in response_params and check_if_value_exists(response_params['precipitation']):
        parsed_result['snow_amount'] = response_params['precipitation']['value']

    # if 'convective-hazard' in response_params:
    #     ch = response_params['convective-hazard']
    #     if ch[0] and ch[0]['severe-component'] and check_if_value_exists(ch[0]['severe-component']):
    #         parsed_result['probability_severe_thunderstorm'] = response_params['convective-hazard'][0]['severe-component']['value']
    #     if ch[1] and ch[1]['severe-component'] and check_if_value_exists(ch[1]['severe-component']):
    #         parsed_result['probability_extreme_severe_thunderstorm'] = response_params['convective-hazard'][1]['severe-component'][
    #             'value']

    if 'humidity' in response_params and check_if_value_exists(response_params['humidity']):
        parsed_result['humidity'] = response_params['humidity']['value']

    print parsed_result
    return parsed_result


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
