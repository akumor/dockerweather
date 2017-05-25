from flask import Flask, request, jsonify, render_template
from datetime import datetime
import logging
import os
import subprocess

app = Flask(__name__)

# Configure logging
file_handler = logging.FileHandler(os.path.dirname(os.path.realpath(__file__)) + '/dockerweather.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)


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
    caller_ip = request.remote_addr
    caller_ip = request.environ['REMOTE_ADDR']
    caller_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    node_ip = subprocess.check_output(['bash', '-c', "hostname -I"]).decode('utf-8').strip().split(' ')[0]
    precise_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    return render_template('index.html', name='WORLD')


@app.route('/nodeip', methods=['GET'])
def node_ip():
    """
    Returns JSON containing the IP address of the Host running this API.
    :return:
    """
    node_ip = subprocess.check_output(['bash', '-c', "hostname -I"]).decode('utf-8').strip().split(' ')[0]
    return jsonify({'node_ip': node_ip})


@app.route('/callerip', methods=['GET'])
def caller_ip():
    """
    Returns JSON containing the IP address of the client who issued the request.
    :return:
    """
    return jsonify({'caller_ip': request.remote_addr}), 200


@app.route('/precisetimestamp')
def precise_timestamp():
    """
    Returns JSON containing a precise timestamp.
    :return:
    """
    precise_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    return jsonify({'precise_timestamp': precise_timestamp})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
