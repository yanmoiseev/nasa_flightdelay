''' provides an API for UI to access and display final result '''
from flask import Flask, request, url_for, jsonify
from flask_restful import Api, Resource, reqparse
import os, requests, json, xmltodict, geocoder
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
    location = geocoder.google("source") # location
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
    l = [{'source': source, 'destination': destination, 'flightno': flightno, 'time': time}]
    return jsonify({"response": l})


####################################
##### make other data available ####

# create list of dictionaries
ml = [{}]


##### handlers for get and put from other endpoints####
@app.route('/ml', methods=['GET', 'POST'])
def sendDataToML():
    return jsonify({'data': ml})


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
    return requests.get(base_url, params=params)


def xgetData(re):
    response_dict = xmltodict.parse(re.content)
    response_data = response_dict['dwml']['data']
    response_params = response_data['parameters']
    parsed_result = {}

    lat = response_data['location']['point']['@latitude']
    long = response_data['location']['point']['@longitude']
    parsed_result['location'] = (lat, long)

    def add_key_value(ordered_dict, target_dict):
        if 'name' in ordered_dict and 'value' in ordered_dict:
            target_dict[ordered_dict['name']] = ordered_dict['value']

    def loop_dict_list(list, target_dict):
        for l in list:
            if isinstance(l, OrderedDict):
                add_key_value(l, target_dict)
            else:
                loop_dict_list(l, target_dict)

    loop_dict_list(response_params, parsed_result)

    temp = response_params['temperature']
    dew_point = response_params['']

    parsed_result['location'] = (lat, long)
    parsed_result['time-layout'] = response_data['time-layout']['start-valid-time']
    parsed_result['temp'] = response_params
    parsed_result['temp'] = response_params['temperature'][0]['value']
    parsed_result['dew_temp'] = response_params['temperature'][1]['value']
    parsed_result['wind-speed'] = response_params['wind-speed']['value']
    parsed_result['cloud-amount'] = response_params['cloud-amount']['value']
    parsed_result['humidity'] = response_params['humidity']['value']


    return parsed_result

if __name__ == '__main__':
    app.run(debug=True)
