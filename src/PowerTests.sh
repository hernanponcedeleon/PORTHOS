for file in ../litmus/*.litmus; do echo $file; ./porthos.py -s alpha -t power -i $file; done
