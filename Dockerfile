FROM tiangolo/uwsgi-nginx-flask:flask

COPY dockerweather/dockerweather.py /app/main.py
COPY dockerweather/templates /app/templates
COPY dockerweather/static /app/static

CMD ["/usr/bin/supervisord"]