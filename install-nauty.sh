#!/bin/sh
# install nauty + Traces from Brendan McKay and Adolfo Piperno's site
set -ex
cd /tmp
wget --no-check-certificate http://pallini.di.uniroma1.it/nauty25r9.tar.gz -O /tmp/nauty25r9.tar.gz
tar -xzvf nauty25r9.tar.gz
cd nauty25r9 && ./configure && make
sudo cp dreadnaut /usr/local/bin

