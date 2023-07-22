#!/bin/bash

while getopts "n:o:i:" arg; do
  case $arg in
    n) num_cores=$OPTARG;;
    o) offset=$OPTARG;;
    i) increment=$OPTARG;;
  esac
done

list=$offset" "
for ((j=1; j<=$num_cores-1; j++)); do
  list=$list$sep$((offset+increment*j))
  sep=" "
done

#echo $list
#parallel python test_for_parallel_bash.py --start_after {1} --increment $increment :::  $list

# First run the init script
python 02-geolocate_reports.py --init 1 --start_after 0 --ends_with $offset  

# Then run the subsequent calls in parallel
parallel python 02-geolocate_reports.py --init 0 --start_after {1} --increment $increment ::: $list