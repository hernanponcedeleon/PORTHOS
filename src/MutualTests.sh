for file in ../benchmarks/*.pts; do echo $file; ./porthos.py -s sc -t tso -i $file; done
