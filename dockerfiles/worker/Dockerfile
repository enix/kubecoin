FROM python
RUN pip install redis
RUN pip install requests
RUN pip install opentelemetry-api
RUN pip install opentelemetry-sdk
RUN pip install opentelemetry-ext-jaeger
RUN pip install opentelemetry-ext-http-requests
COPY worker.py /
CMD ["python", "worker.py"]
