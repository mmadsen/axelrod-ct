#!/bin/sh

## replace "foo" with experiment name, and adjust the number of entries if parallelism != 4

nohup sh simrunner-exp-foo-0.sh &
nohup sh simrunner-exp-foo-1.sh &
nohup sh simrunner-exp-foo-2.sh &
nohup sh simrunner-exp-foo-3.sh &
