#!/bin/sh
for file in ../litmus/*.litmus; do echo $file; ./porthos.py -s tso -t power -i $file; done
