require 'digest'
require 'sinatra'
require 'socket'
#require 'prometheus/client'
#require 'prometheus/client/formats/text'

set :bind, '0.0.0.0'
set :port, 80

#prometheus = Prometheus::Client.registry
#http_requests = prometheus.counter(:http_requests, docstring: 'A counter of HTTP requests made')
#hash_size = prometheus.counter(:hash_size, docstring: 'A counter of total size hashed')

post '/' do
    # Simulate a bit of delay
    sleep 0.5
    content_type 'text/plain'
    body = request.body.read
    #http_requests.increment
    #hash_size.increment(:by => body.length)
    "#{Digest::SHA2.new().update(body)}"
end

get '/' do
    "HASHER running on #{Socket.gethostname}\n"
end

#get '/metrics' do
#  "#{Prometheus::Client::Formats::Text::marshal(prometheus)}"
#end
