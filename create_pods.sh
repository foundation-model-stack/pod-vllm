#!/bin/bash
# IMPORTANT: use 01-based pod id as this ID is used in calculating the offset of file content to process
# RUN 1 pod: ./run.sh 01

# run 11 pods from 01 to 11
source env.sh
for id in $(seq -f "%02g" 1 ${NUM_PODS})
do
    echo $id
    export id=${id}; shift
    export POD_YAML=vllm-pod.yaml.${id}
    envsubst < vllm-pod.yaml > ${POD_YAML}

    oc apply -f ${POD_YAML}
done

for id in $(seq -f "%02g" 1 ${NUM_PODS})
do
    export POD_NAME="gen-pod-${id}"
    ./wait_pod.sh  ${POD_NAME}
done
