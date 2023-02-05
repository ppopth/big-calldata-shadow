#!/usr/bin/env bash

datadir=$1
slot=$2
title=$3

echo "slot=$slot, datadir=$datadir, title=$title"

propagation_start_time=$(grep -h -R "Valid .*slot: $slot" $datadir/shadow | grep -o "..:..:..\....")
echo "propagation_start_time=$propagation_start_time"

grep -h -R "New block received.*slot: $slot" $datadir/shadow | grep -o "..:..:..\...." > input.txt
./histogram.py "$propagation_start_time" input.txt "$title"
