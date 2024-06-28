FROM python:3
RUN pip install requests
RUN pip install boto3
RUN pip install datetime
ADD config.py .
ADD get_metric.py .
ADD get_request_data.py .
ADD scripts_run.sh /
RUN chmod +x scripts_run.sh
CMD ["./scripts_run.sh"]