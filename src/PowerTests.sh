#!/bin/sh
for file in ../litmus/*.litmus; do echo $file; ./porthos.py -s pso -t power -i $file; done
