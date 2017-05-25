FROM tiangolo/uwsgi-nginx-flask:flask

COPY requirements.txt /root/requirements.txt
RUN pip install -r /root/requirements.txt

COPY dockerweather/dockerweather.py /app/main.py
COPY dockerweather/templates /app/templates
COPY dockerweather/static /app/static

COPY entrypoint.sh /root/
RUN chmod +x /root/entrypoint.sh

CMD ["/root/entrypoint.sh"]