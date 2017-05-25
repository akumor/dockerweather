#!/bin/bash
set -x

# Build the dockerweather configuration file from environment variables passed to container.
echo '[dockerweather]' > /app/dockerweather.ini
if [ "${DOCKERWEATHER_LOG_LEVEL}" != "" ]; then
    echo "log_level=${DOCKERWEATHER_LOG_LEVEL}" >> /app/dockerweather.ini
else
    echo "log_level=INFO" >> /app/dockerweather.ini
fi
echo '' >> /app/dockerweather.ini
echo '[open weather map]' >> /app/dockerweather.ini
if [ "${DOCKERWEATHER_OWM_API_KEY}" != "" ]; then
    echo "api_key=${DOCKERWEATHER_OWM_API_KEY}" >> /app/dockerweather.ini
else
    echo "api_key=" >> /app/dockerweather.ini
fi
echo '' >> /app/dockerweather.ini

/usr/bin/supervisord