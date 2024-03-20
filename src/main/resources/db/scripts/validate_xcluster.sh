#!/bin/bash

low_hash_value=0
for _ in {1..16}
do
  high_hash_value=$(($low_hash_value+4096))
  ysqlsh -h /tmp/.yb* -A -F, -t -c "SELECT $low_hash_value,$high_hash_value,md5(CAST((array_agg(c.* ORDER BY id)) AS TEXT)) FROM ysql_cache.ysql_cache c WHERE yb_hash_code(id) >= $low_hash_value AND yb_hash_code(id) < $high_hash_value;" &
  low_hash_value=$high_hash_value
done

wait

## call this something like:  ./verify_xcluster.sh | sort -k1 -n -t, | md5sum
## and compare both sides

## TODO
## this should probably be command line driven
## probably should allow more or less iterations than 16
## should allow schema/table to be provided by args
##