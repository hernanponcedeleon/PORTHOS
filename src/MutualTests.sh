#!/bin/sh
echo bakery.pts
./porthos.py -s sc -t tso -i bakery.pts
echo x86_bakery.pts
./porthos.py -s sc -t tso -i x86_bakery.pts
./porthos.py -s tso -t power -i x86_bakery.pts
echo pwr_bakery.pts
./porthos.py -s tso -t power -i pwr_bakery.pts

echo burns.pts
./porthos.py -s sc -t tso -i burns.pts
echo x86_burns.pts
./porthos.py -s sc -t tso -i x86_burns.pts
./porthos.py -s tso -t power -i x86_burns.pts
echo pwr_burns.pts
./porthos.py -s tso -t power -i pwr_burns.pts

echo dekker.pts
./porthos.py -s sc -t tso -i dekker.pts
echo x86_dekker.pts
./porthos.py -s sc -t tso -i x86_dekker.pts
./porthos.py -s tso -t power -i x86_dekker.pts
echo pwr_dekker.pts
./porthos.py -s tso -t power -i pwr_dekker.pts

echo lamport.pts
./porthos.py -s sc -t tso -i lamport.pts
echo x86_lamport.pts
./porthos.py -s sc -t tso -i x86_lamport.pts
./porthos.py -s tso -t power -i x86_lamport.pts
echo pwr_lamport.pts
./porthos.py -s tso -t power -i pwr_lamport.pts

echo parker.pts
./porthos.py -s sc -t tso -i parker.pts
echo x86_parker.pts
./porthos.py -s sc -t tso -i x86_parker.pts
./porthos.py -s tso -t power -i x86_parker.pts
echo pwr_parker.pts
./porthos.py -s tso -t power -i pwr_parker.pts

echo peterson.pts
./porthos.py -s sc -t tso -i peterson.pts
echo x86_peterson.pts
./porthos.py -s sc -t tso -i x86_peterson.pts
./porthos.py -s tso -t power -i x86_peterson.pts
echo pwr_peterson.pts
./porthos.py -s tso -t power -i pwr_peterson.pts

echo szymanski.pts
./porthos.py -s sc -t tso -i szymanski.pts
echo x86_szymanski.pts
./porthos.py -s sc -t tso -i x86_szymanski.pts
./porthos.py -s tso -t power -i x86_szymanski.pts
echo pwr_szymanski.pts
./porthos.py -s tso -t power -i pwr_szymanski.pts


