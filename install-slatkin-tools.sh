#!/bin/sh
set -ex
cd /tmp
wget --no-check-certificate  https://github.com/mmadsen/slatkin-exact-tools/archive/v1.2.tar.gz -O /tmp/slatkin-exact-tools-1.2.tar.gz
tar -xzvf slatkin-exact-tools-1.2.tar.gz
cd slatkin-exact-tools-1.2 && make && make install

