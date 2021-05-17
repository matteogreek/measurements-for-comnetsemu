#!/bin/bash
timeout 5m ./pathload_classic/pathload_rcv -s $1 > test.txt
sed -n '4,80p' test.txt > path.csv
sed -i 's/Receiving Fleet //' path.csv
sed -i 's/ Rate //' path.csv
sed -i 's/Mbps//' path.csv
cat path.csv