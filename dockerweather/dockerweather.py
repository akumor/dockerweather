from flask import Flask, request, jsonify, render_template
from datetime import datetime
import logging
import os
import subprocess
import json
import requests
import ConfigParser

app = Flask(__name__)

# Configuration file
CONFIG = ConfigParser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dockerweather.ini'))

# Configure logging
file_handler = logging.FileHandler(os.path.dirname(os.path.realpath(__file__)) + '/dockerweather.log')
app.logger.addHandler(file_handler)
try:
    log_level_string = CONFIG.get('dockerweather', 'log_level')
except:
    log_level_string = 'INFO'
if log_level_string == 'INFO':
    app.logger.setLevel(logging.INFO)
    app.logger.info('Log level set to INFO.')
else:
    app.logger.setLevel(logging.DEBUG)
    app.logger.info('Log level set to DEBUG.')

# Get configuration for API key
OWM_API_KEY = CONFIG.get('open weather map', 'api_key')


def retrieve_weather(zip_code):
    """
    Retrieves weather information from an API
    :param zip_code: zip code to obtain the weather for
    :return: dictionary containing weather information
    """
    app.logger.debug('Obtaining weather based on zip code...')
    try:
        open_weather_map_url = 'http://api.openweathermap.org/data/2.5/weather'
        payload = {'zip': zip_code, 'APPID': OWM_API_KEY}
        app.logger.debug('Open Weather Map API request URL and payload:\n{0}\n{1}'.format(open_weather_map_url,
                                                                                          str(payload)))
        resp2 = requests.get(open_weather_map_url, params=payload)
        status = resp2.status_code
        if str(status) == '200' or str(status) == '304':
            weather_dict = json.loads(resp2.text)
            app.logger.debug('weather_dict = ' + str(weather_dict))
        else:
            app.logger.error(
                'Bad response from api.openweathermap.org while obtaining weather based on zip code {0}'.format(
                    zip_code))
            return None
    except:
        app.logger.error('Exception occurred while obtaining weather based on zip code {0}.'.format(geo_dict['zip_code']))
        return None

    # Update units/format of weather dictionary
    app.logger.debug('Updating units/format of the retrieved weather information.')
    try:
        # # Kelvin -> Fahrenheit
        weather_dict['main']['temp'] = (((weather_dict['main']['temp'] - 273) * 1.8) + 32)
        app.logger.debug("weather_dict['main']['temp'] = {0}".format(weather_dict['main']['temp']))
        weather_dict['main']['temp_max'] = (((weather_dict['main']['temp_max'] - 273) * 1.8) + 32)
        app.logger.debug("weather_dict['main']['temp_max'] = {0}".format(weather_dict['main']['temp_max']))
        weather_dict['main']['temp_min'] = (((weather_dict['main']['temp_min'] - 273) * 1.8) + 32)
        app.logger.debug("weather_dict['main']['temp_min'] = {0}".format(weather_dict['main']['temp_min']))
        # # Unix time -> date format
        weather_dict['sys']['sunrise'] = datetime.fromtimestamp(weather_dict['sys']['sunrise']).strftime(
            '%Y-%m-%d %H:%M:%S.%f')
        app.logger.debug("weather_dict['sys']['sunrise'] = {0}".format(weather_dict['sys']['sunrise']))
        weather_dict['sys']['sunset'] = datetime.fromtimestamp(weather_dict['sys']['sunset']).strftime(
            '%Y-%m-%d %H:%M:%S.%f')
        app.logger.debug("weather_dict['sys']['sunset'] = {0}".format(weather_dict['sys']['sunset']))
        weather_dict['dt'] = datetime.fromtimestamp(weather_dict['dt']).strftime(
            '%Y-%m-%d %H:%M:%S.%f')
        app.logger.debug("weather_dict['dt'] = {0}".format(weather_dict['dt']))
    except:
        app.logger.error('Unable to convert or format units for weather.')
        return None

    return weather_dict


@app.errorhandler(404)
def not_found(error=None):
    """
    Returns a JSON message notifying the client that the endpoint was not found.
    :param error:
    """
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp


@app.route('/', methods=['GET'])
def index():
    """
    Returns a page containing the weather for the IP address of the client.
    :return:
    """
    # Different way to get the caller ip
    app.logger.debug('Obtaining caller IP...')
    caller_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

    # Get location based on IP
    app.logger.debug('Obtaining location based on caller IP...')
    try:
        resp = requests.get('http://freegeoip.net/json/{0}'.format(caller_ip))
        status = resp.status_code
        if str(status) == '200' or str(status) == '304':
            geo_dict = json.loads(resp.text)
            app.logger.debug('geo_dict = ' + str(geo_dict))
        else:
            app.logger.error('Bad response from freegeoip.net while obtaining location based on caller IP.')
            return not_found()
    except:
        app.logger.error('Exception occurred while obtaining location based on caller IP.')
        return not_found()

    # Default to Los Angeles zip code if API request failed to retrieve one
    # TODO default to something else?
    if geo_dict['zip_code'] == '':
        geo_dict['zip_code'] = '90045'

    # Get weather based on location
    weather_dict = retrieve_weather(geo_dict['zip_code'])
    if weather_dict is None:
        return not_found()

    app.logger.debug('Obtaining node IP from bash command...')
    node_ip = subprocess.check_output(['bash', '-c', "hostname -I"]).decode('utf-8').strip().split(' ')[0]
    app.logger.debug('node_ip = ' + node_ip)
    app.logger.debug('Obtaining precise timestamp from datetime module...')
    precise_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    app.logger.debug('precise_timestamp = ' + precise_timestamp)

    app.logger.debug('Returning response for /')
    return render_template('index.html',
                           caller_ip=caller_ip,
                           node_ip=node_ip,
                           precise_timestamp=precise_timestamp,
                           geo_dict=geo_dict,
                           weather_dict=weather_dict)


@app.route('/zip_code', methods=['GET', 'POST'])
def zip_code():
    """
    Returns page prompting for a zip code or containing weather for a specific zip code
    :return:
    """
    if request.method == 'GET':
        app.logger.debug('Returning response for GET of /zip_code')
        return render_template('zip_code.html', method=request.method)
    elif request.method == 'POST':
        if 'zip' in request.form:
            # Get weather based on location
            weather_dict = retrieve_weather(request.form['zip'])
            if weather_dict is None:
                return not_found()

            app.logger.debug('Returning response for POST of /zip_code')
            return render_template('zip_code.html',
                                   zip_code=request.form['zip'],
                                   weather_dict=weather_dict,
                                   method=request.method)
        else:
            app.logger.error('POST received for /zip_code without "zip" parameter.')
            return not_found()
    else:
        app.logger.error('Invalid request method received for /zip_code')
        return not_found()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
