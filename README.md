# dockerweather
A simple Flask application to provide the weather via a web interface using
data from openweathermap.org

## Running on your own machine
Create a dockerweather.ini configuration file in the same directory as the
dockerweather.py script with the following format:

    [dockerweather]
    log_level=DEBUG
    
    [open weather map]
    api_key=<api key>

Install any required python libraries:

    pip install -r requirements.txt
    
Then you can run it with the following command:

    python dockerweather/dockerweather.py

## Build Docker Image
    docker build --no-cache -t <username>/dockerweather .
    
## Run Docker Image
    docker run -d \
               -P \
               -e DOCKERWEATHER_LOG_LEVEL=INFO \
               -e DOCKERWEATHER_OWM_API_KEY=<api key> \
               --name=dockerweather \
               <username>/dockerweather               
               
## Additional Resources
* Open Weather Map - https://openweathermap.org
* Bootstrap - https://getbootstrap.com/
* Flask - http://flask.pocoo.org/
* Docker - https://www.docker.com/ 
* uWSGI and NGINX Flask container - https://github.com/tiangolo/uwsgi-nginx-flask-docker
