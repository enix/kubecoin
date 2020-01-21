import logging
import os
from redis import Redis
import requests
import time

try: # Python3
    from urllib.parse import urlparse
except ImportError: # Python2
    from urlparse import urlparse

#import opentelemetry.ext.http_requests
#
#from opentelemetry import trace
#from opentelemetry.ext.jaeger import JaegerSpanExporter
#from opentelemetry.sdk.trace import Tracer
#from opentelemetry.sdk.trace.export import ConsoleSpanExporter
#from opentelemetry.sdk.trace.export import SimpleExportSpanProcessor

DEBUG = os.environ.get("DEBUG", "").lower().startswith("y")

log = logging.getLogger(__name__)
if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)


#trace.set_preferred_tracer_implementation(lambda T: Tracer())
#tracer = trace.tracer()
#
#opentelemetry.ext.http_requests.enable(tracer)
#
#def setup_tracing():
#    agent_url = os.environ.get('TELEMETRY_AGENT', None)
#    if agent_url:
#        if agent_url.lower() == "console":
#            span_exporter = ConsoleSpanExporter()
#        else:
#            agent = urlparse(agent_url)
#            if not agent.scheme or not agent.netloc:
#                agent = urlparse('udp://' + agent_url)
#            span_exporter = JaegerSpanExporter(
#                service_name="kubecoin.worker",
#                agent_host_name=agent.netloc,
#                agent_port=agent.port or 6831,
#            )
#        tracer.add_span_processor(SimpleExportSpanProcessor(span_exporter))
#
#setup_tracing()


redis = Redis("redis")


def get_random_bytes():
    r = requests.get("http://rng/32")
    return r.content


def hash_bytes(data):
    r = requests.post("http://hasher/",
                      data=data,
                      headers={"Content-Type": "application/octet-stream"})
    hex_hash = r.text
    return hex_hash


def work_loop(interval=1):
    deadline = 0
    loops_done = 0
    while True:
        if time.time() > deadline:
            log.info("{} units of work done, updating hash counter"
                     .format(loops_done))
            redis.incrby("hashes", loops_done)
            loops_done = 0
            deadline = time.time() + interval
        work_once()
        loops_done += 1


def work_once():
    # with tracer.start_as_current_span('work_unit') as work_span:
        #namespace = os.environ.get('NAMESPACE', None)
        #if namespace:
        #    work_span.set_attribute(key='namespace', value=namespace)
    log.debug("Doing one unit of work")
    time.sleep(0.1)
    random_bytes = get_random_bytes()
    hex_hash = hash_bytes(random_bytes)
    if not hex_hash.startswith('0'):
        log.debug("No coin found")
        return
    log.info("Coin found: {}...".format(hex_hash[:8]))
    #with tracer.start_as_current_span('redis_put'):
    created = redis.hset("wallet", hex_hash, random_bytes)
    if not created:
        log.info("We already had that coin")


if __name__ == "__main__":
    while True:
        try:
            work_loop()
        except:
            log.exception("In work loop:")
            log.error("Waiting 10s and restarting.")
            time.sleep(10)


