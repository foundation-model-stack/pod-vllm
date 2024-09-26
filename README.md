# pod-vllm
Source code to launch a number of pods, performing synthetic data generation

Requirements: 
* you have access to a namespace/project (e.g. tuan) in a K8s cluster or OCP cluster
* you have two NFS-mounted VPC: /model/ and /result
* you have access to HuggingFace to download model, e.g. meta-llama/Meta-Llama-3.1-405B-Instruct-FP8

Use-case:
* you have a bunch of JSONL files, each line is a dictionary with 'prompt' key
* the file sizes can vary, i.e. some small in sizes and some of very large size
* you want to use the prompt to generate output (e.g. synthetic data)
* the generated data will be saved to the NFS-mounted VPC

Design principles:
* load balancing, i.e. each pod handles the same number of request
* checkpoint - if there is a crash, it can recover and continue
* stop on-demand - we can stop the run, if there is a need to release resource or add more resource
* adaptable - if there are more resource available, it can be restarted and use more resource
 
# Step-1 : create pods

* modify `vllm-pod.yaml` file to get
  + the correct PVC names, e.g. `llama-tuan` and `llama-results-tuan`
  + the secret key `GIT_PAT`
  + the right image name

* modify `create_pods.sh` and choose the number of pods to create via `NUM_PODS`

* ensure that you are logged into your OCP cluster, and from your local machine, run it

  ```
  chmod +x create_pods.sh
  ./create_pods.sh
  ```
