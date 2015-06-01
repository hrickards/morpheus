# Morpheus
Fun facebook chat analytics thrown together over the course of a weekend.

## Quick up and running quide
You'll need MongoDB and Redis installed and running. On OSX with Homebrew (there are equivalent commands for other package managers/operating systems), that's

    brew install mongodb redis
    mongod run --config /usr/local/etc/mongod.conf
    redis-server /usr/local/etc/redis.conf

You'll also need to install the pertinent python libraries with

    pip install -r requirements.txt

Then just fire everything up with

    python2 morpheus.py

and follow the onscreen prompts.
