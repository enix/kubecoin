from flask import Flask, Response
import os
import socket
import time

try: # Python3
    from urllib.parse import urlparse
except ImportError: # Python2
    from urlparse import urlparse

from opentelemetry import trace
from opentelemetry.ext.flask import instrument_app
from opentelemetry.ext.jaeger import JaegerSpanExporter
from opentelemetry.sdk.trace import Tracer
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.sdk.trace.export import SimpleExportSpanProcessor

trace.set_preferred_tracer_implementation(lambda T: Tracer())
tracer = trace.tracer()

app = Flask(__name__)
instrument_app(app)

# Enable debugging if the DEBUG environment variable is set and starts with Y
app.debug = os.environ.get("DEBUG", "").lower().startswith('y')

hostname = socket.gethostname()

urandom = os.open("/dev/urandom", os.O_RDONLY)

def setup_tracing():
    agent_url = os.environ.get('TELEMETRY_AGENT', None)
    if agent_url:
        if agent_url.lower() == "console":
            span_exporter = ConsoleSpanExporter()
        else:
            agent = urlparse(agent_url)
            if not agent.scheme or not agent.netloc:
                agent = urlparse('udp://' + agent_url)
            span_exporter = JaegerSpanExporter(
                service_name="kubecoin.rng",
                agent_host_name=agent.netloc,
                agent_port=agent.port or 6831,
            )
        tracer.add_span_processor(SimpleExportSpanProcessor(span_exporter))

@app.route("/")
def index():
    return "RNG running on {}\n".format(hostname)


@app.route("/<int:how_many_bytes>")
def rng(how_many_bytes):
    # Simulate a little bit of delay
    time.sleep(0.1)
    with tracer.as_current_span('compute_random'):
        return Response(
            os.read(urandom, how_many_bytes),
            content_type="application/octet-stream")


if __name__ == "__main__":
    setup_tracing()
    app.run(host="0.0.0.0", port=80)
