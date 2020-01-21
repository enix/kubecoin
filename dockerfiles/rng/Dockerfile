FROM python
RUN pip install Flask
RUN pip install opentelemetry-api
RUN pip install opentelemetry-sdk
RUN pip install opentelemetry-ext-flask
RUN pip install opentelemetry-ext-jaeger
COPY rng.py /
CMD ["python", "rng.py"]
EXPOSE 80
