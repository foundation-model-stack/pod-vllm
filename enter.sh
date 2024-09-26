#!/bin/bash

export id=${1}; shift
export POD_PREFIX=${POD_PREFIX:-gen-pod}

oc exec -it ${POD_PREFIX}-${id} -- /bin/bash
