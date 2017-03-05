#!/bin/sh
for file in ../benchmarks/*.pts; do echo $file; ./porthos.py -s tso -t power -i $file; done
