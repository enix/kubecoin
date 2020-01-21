FROM ruby
RUN gem install sinatra
RUN gem install thin
RUN gem install prometheus-client
ADD hasher.rb /
CMD ["ruby", "hasher.rb"]
EXPOSE 80
