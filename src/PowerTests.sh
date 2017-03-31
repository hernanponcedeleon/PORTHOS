#!/bin/sh
if [ -n "$3" ]
then 
for file in ../litmus/*.litmus; do echo $file; ./porthos.py -s $1 -t $2 -i $file -d; done
else
for file in ../litmus/*.litmus; do echo $file; ./porthos.py -s $1 -t $2 -i $file; done
fi
