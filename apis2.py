''' provides an API for UI to access and display final result '''
from flask import Flask,request,url_for,jsonify
from flask_restful import Api,Resource,reqparse
import os,requests,json,xmltodict
from collections import OrderedDict

app = Flask(__name__)
api = Api(app)

################################
#### to send output to ui ######

prob = os.path.join("toui.txt") # info to ui
outstr=''

def readData():
    with open (prob,'r') as fd:
        outstr = fd.read()
    return outstr
l = [{'result':readData()}]

#### get and post handler to send data to UI ####

@app.route('/ToUI',methods=['GET','POST']) # replying to POST,GET
def sendDataToUI():
    return jsonify({'data':l})

@app.route('/Find',methods=['GET','POST']) # to accquire source and destination info
def getDetails():
    if request.method == 'POST':
        source = request.form['source']
        destination = request.form['destination']
        flightno = request.form['flightno']
        time = request.form['time']

    return (source,destination)

####################################
##### make other data available ####

#create list of dictionaries
ml =[{}]

##### handlers for get and put from other endpoints####
@app.route('/MI',methods=['GET','POST']) 
def sendDataToML():
    return jsonify({'data':ml})

####################################
### to fetch data from external sources ###

#def getData():
#	url_list=[]
#	req = requests.get("http://api.openweathermap.org/data/2.5/weather?zip=94040,us&APPID=75b19517f102504815a3449ebbbf979")
#    #api.openweathermap.org/data/2.5/forecat/city?id=12345&APPID=75b19517f102504815a3449ebbbf979
#    res = requests.get("http://api.openweathermap.org/data/2.5/forecast/city?id=524901&APPID=75b19517f1f02504815a3449ebbbf979")
#    return res.content
    
    
def xgetData():
	#req =  requests.get("http://graphical.weather.gov/xml/SOAP_server/ndfdXMLclient.php?whichClient=NDFDgen&lat=38.99&lon=-77.01&listLatLon=&lat1=&lon1=&lat2=&lon2=&resolutionSub=&listLat1=&listLon1=&listLat2=&listLon2=&resolutionList=&endPoint1Lat=&endPoint1Lon=&endPoint2Lat=&endPoint2Lon=&listEndPoint1Lat=&listEndPoint1Lon=&listEndPoint2Lat=&listEndPoint2Lon=&zipCodeList=&listZipCodeList=&centerPointLat=&centerPointLon=&distanceLat=&distanceLon=&resolutionSquare=&listCenterPointLat=&listCenterPointLon=&listDistanceLat=&listDistanceLon=&listResolutionSquare=&citiesLevel=&listCitiesLevel=&sector=&gmlListLatLon=&featureType=&requestedTime=&startTime=&endTime=&compType=&propertyName=&product=time-series&begin=2004-01-01T00%3A00%3A00&end=2020-04-23T00%3A00%3A00&Unit=e&maxt=maxt&Submit=Submit")
	#re = requests.get("http://graphical.weather.gov/xml/SOAP_server/ndfdXMLclient.php?whichClient=NDFDgen&lat=38.99&lon=-77.01&listLatLon=&lat1=&lon1=&lat2=&lon2=&resolutionSub=&listLat1=&listLon1=&listLat2=&listLon2=&resolutionList=&endPoint1Lat=&endPoint1Lon=&endPoint2Lat=&endPoint2Lon=&listEndPoint1Lat=&listEndPoint1Lon=&listEndPoint2Lat=&listEndPoint2Lon=&zipCodeList=&listZipCodeList=&centerPointLat=&centerPointLon=&distanceLat=&distanceLon=&resolutionSquare=&listCenterPointLat=&listCenterPointLon=&listDistanceLat=&listDistanceLon=&listResolutionSquare=&citiesLevel=&listCitiesLevel=&sector=&gmlListLatLon=&featureType=&requestedTime=&startTime=&endTime=&compType=&propertyName=&product=time-series&begin=2004-01-01T00%3A00%3A00&end=2020-04-23T00%3A00%3A00&Unit=e&maxt=maxt&Submit=Submit")
	re = requests.get("http://graphical.weather.gov/xml/SOAP_server/ndfdXMLclient.php?whichClient=NDFDgen&lat=38.99&lon=-77.01&listLatLon=&lat1=&lon1=&lat2=&lon2=&resolutionSub=&listLat1=&listLon1=&listLat2=&listLon2=&resolutionList=&endPoint1Lat=&endPoint1Lon=&endPoint2Lat=&endPoint2Lon=&listEndPoint1Lat=&listEndPoint1Lon=&listEndPoint2Lat=&listEndPoint2Lon=&zipCodeList=&listZipCodeList=&centerPointLat=&centerPointLon=&distanceLat=&distanceLon=&resolutionSquare=&listCenterPointLat=&listCenterPointLon=&listDistanceLat=&listDistanceLon=&listResolutionSquare=&citiesLevel=&listCitiesLevel=&sector=&gmlListLatLon=&featureType=&requestedTime=&startTime=&endTime=&compType=&propertyName=&product=time-series&begin=2016-04-25T00%3A00%3A00&end=2016-04-25T00%3A10%3A00&Unit=m&temp=temp&dew=dew&wspd=wspd&wdir=wdir&sky=sky&wx=wx&rh=rh&appt=appt&precipa_r=precipa_r&Submit=Submit")
	xdata = xmltodict.parse(re.content)
	print xdata
	xdatad= {}
	xdatad['location'] = (xdata['dwml']['data']['location']['point']['@latitude'],xdata['dwml']['data']['location']['point']['@longitude'])
	#xdatad['moreWeatherInformation'] = xdata['dwml']['data']['moreWeatherInformation']
	xdatad['time-layout'] = xdata['dwml']['data']['time-layout']['start-valid-time']
	xdatad['temp'] = xdata['dwml']['data']['parameters']
	#print xdatad['temp']
	xdatad['temp'] = xdata['dwml']['data']['parameters']['temperature'][0]['value']
	xdatad['dew_temp'] = xdata['dwml']['data']['parameters']['temperature'][1]['value']
	xdatad['wind-speed'] = xdata['dwml']['data']['parameters']['wind-speed']['value']	
	xdatad['cloud-amount'] = xdata['dwml']['data']['parameters']['cloud-amount']['value']
	xdatad['humidity'] = xdata['dwml']['data']['parameters']['humidity']['value']

	#for para in parameterst:
	#	xdatad[para['name']] = parameterst[para]['value']
	#	print xdatad

	return xdatad

print xgetData()

if __name__ == '__main__':
    app.run(debug=True)

        
