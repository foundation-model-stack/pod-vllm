#!/bin/bash
# IMPORTANT: use 01-based pod id as this ID is used in calculating the offset of file content to process
# RUN 1 pod: ./run.sh 01

# run 11 pods from 01 to 11
source env.sh
START_OFFSET=${SKIP_PODS:-0}
START_OFFSET=$(($START_OFFSET+ 1))
for id in $(seq -f "%02g" $START_OFFSET ${NUM_PODS})
do
    export POD_NAME="gen-pod-${id}"
    oc delete pod ${POD_NAME}
done
