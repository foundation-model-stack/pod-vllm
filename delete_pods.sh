#!/bin/bash
export NUM_PODS=11
for id in $(seq -f "%02g" 1 ${NUM_PODS})
do
    echo $id
    export POD_NAME="gen-pod-${id}"
    oc delete  pod ${POD_NAME}
done
