#!/bin/bash

POD_NAME=$1
#"your-pod-name"
while true; do
  STATUS=$(kubectl get pod "$POD_NAME" -o jsonpath='{.status.phase}')
  if [ "$STATUS" == "Running" ]; then
    echo "Pod $POD_NAME is running."
    break
  else
    echo "Pod $POD_NAME is not yet running. Waiting..."
    sleep 5
  fi
done
