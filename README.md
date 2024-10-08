# pod-vllm
Source code to launch a number of pods, performing synthetic data generation

Requirements: 
* you have access to a namespace/project (e.g. tuan) in a K8s cluster or OCP cluster
* you have two NFS-mounted VPC: /model/ and /result
* you have access to HuggingFace to download model, e.g. meta-llama/Meta-Llama-3.1-405B-Instruct-FP8 (i.e. HF token, and model download is approved)

Use-case:
* you have a bunch of JSONL files, each line is a dictionary with 'prompt' key
* the file sizes can vary, i.e. some small in sizes and some of very large size
* you want to use the prompt to generate output (e.g. synthetic data)
* the generated data will be saved to the NFS-mounted VPC
* the data is copied back to S3-backend, e.g. IBM COS.

Design principles:
* load balancing, i.e. each pod handles the same number of request
* checkpoint - if there is a crash, it can recover and continue
* stop on-demand - we can stop the run, if there is a need to release resource or add more resource
* adaptable - if there are more resource available, it can be restarted and use more resource

NOTE: The code can be adopted to use Ray or Spark on K8s/OCP to do this job, but this is a simple approach with performant and easy to run with minimal installation required for K8s/OCP admin.

# Step-0 : configure env.

run this first on the shell you run the next steps, as this information is needed for each step.

Update the `env.sh` script) and run this
```
source env.sh
```


# Step-1 : create pods

* modify `vllm-pod.yaml` file to get
  + the correct PVC names, e.g. `llama-tuan` and `llama-results-tuan` [one is used to host the model checkpoint and data; one is used to host the model output]
  + the secret key `GIT_PAT`
  + the right image name

* modify `create_pods.sh` and choose the number of pods to create via `NUM_PODS`

* ensure that you are logged into your OCP cluster, and from your local machine, run it

  ```
  chmod +x create_pods.sh
  ./create_pods.sh
  ```
  
The pods are named using the convention `gen-pod-<id>` with `<id>` is a 2-letter number, e.g. `gen-pod-01`. It can be changed by modifying the `POD_PREFIX` env variable in `create_pods.sh`. 


# Step-2 : copy scripts 2 pods

We don't want to copy data to pod via `kubectl cp` as it overloads K8s/OCP API Server. Data should be copied to S3 storage, e.g. IBM COS; and then download to mounted VPC storage. 

Here, we only copy scripts file to each pod. The datalake library is copied as well to support operations with S3 storage. Therefore, you need to have the 
gz file of this [library](https://github.ibm.com/Common-TimeSeries-Analytics-Library/datalake), e.g. `datalake-0.20.0.tar.gz`.

Before running this, we need to make sure we add the `HF_TOKEN` to `run_in_image.sh` script. This is needed to download the model from HF.

```
python copy2image.py
```

# Step-3 : copy data to VPC storage

We only need to use one pod, 
```
./enter.sh 01
```
and from there perform data downloading to `/model/data` path. There are several example from [`datalake/scripts/copy_data.py` script](https://github.ibm.com/Common-TimeSeries-Analytics-Library/datalake/blob/master/scripts/copy_data.py)


# Step-4 : send jobs to pods


```
python run.py
```

Jobs runs within a tmux session, that we can inspect at each pod. 

NOTE: To kill jobs, there are a few options

1. 'signal' to stop - job waits until checkpoint before stopping itself:

  log into one pod
```
./enter.sh 01
```
Edit the file `/model/stop_run_end_chunk.txt` and add `1` to the first line

 2. 'signal' to stop - job stop gracefully in a few minutes:

  log into one pod
```
./enter.sh 01
```
Edit the file `/model/stop_run_immediately.txt` and add `1` to the first line
  
3. stop immediately by killing the process

run from the local machine
```
python run.py -k
# or
python run.py --kill

```

# Step-5 : sync generated data back to COS

You can use the script in `copy_data.py` to run a CRON job which regularly (e.g. every 3 hours) to upload new data files to COS.
