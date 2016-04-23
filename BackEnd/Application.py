''' provides an API for UI to access and display final result '''
from flask import Flask, request, url_for, jsonify
from flask_restful import Api, Resource, reqparse
import os, requests, json, xmltodict, geocoder
import pytz
from dateutil import parser
import datetime
from collections import OrderedDict

app = Flask(__name__)
api = Api(app)

################################
#### to send output to ui ######

# prob = os.path.join("toui.txt")  # info to ui
# outstr = ''
#
# def readData():
#     with open(prob, 'r') as fd:
#         outstr = fd.read()
#     return outstr
#
# l = [{'result': readData()}]

def latlng(place): #convert text location to latitude and longitude
    location = geocoder.google(place) # location
    latitude = location.lat
    longitude = location.lng
    return (latitude,longitude)

#### get and post handler to send data to UI ####

@app.route('/ui', methods=['GET', 'POST'])  # replying to POST,GET
def sendDataToUI():
    return jsonify({'data': 'asdsa'})

source_key ='source'
destination_key = 'destination'
flightno_key = 'flightno'
time_key = 'time'

@app.route('/find', methods=['GET', 'POST'])  # to accquire source and destination info
def getDetails():
    if request.method == 'POST':
        source = request.form[source_key]
        destination = request.form[destination_key]
        flightno = request.form[flightno_key]
        time = request.form[time_key]
    else:
        print request.args
        source = request.args.get(source_key)
        destination = request.args.get(destination_key)
        flightno = request.args.get(flightno_key)
        time = request.args.get(time_key)

    coordinate = latlng(source)
    begin = parse_date_time_utc(time)
    end = begin + datetime.timedelta(seconds=1)

    begin = begin.isoformat().split('+')[0]
    end = end.isoformat().split('+')[0]

    print '!!!!!!!!!SOURCE: {} COORD: {} BEGIN: {} END: {}'.format(source, coordinate, begin, end)
    result = get_forecast_weather(coordinate[0], coordinate[1], begin, end)
    print result
    # l = [{'source': source, 'destination': destination, 'flightno': flightno, 'time': time}]
    return jsonify(result)


####################################
##### make other data available ####

# create list of dictionaries
ml = [{}]


##### handlers for get and put from other endpoints####
@app.route('/ml', methods=['GET', 'POST'])
def sendDataToML():
    return jsonify({'data': ml})


def parse_date_time_utc(date_str):
    dt = parser.parse(date_str)
    utc = dt.replace(tzinfo=pytz.utc) + dt.tzinfo._offset

    return utc

####################################
### to fetch data from external sources ###

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


def parse_xml_to_flat_dict(re):
    response_dict = xmltodict.parse(re.content)
    print re.content
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
    app.run(debug=True)
