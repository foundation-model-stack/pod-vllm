import subprocess
import os

NUM_PODS = os.environ.get("NUM_PODS", 11)
POD_PREFIX = os.environ.get("POD_PREFIX", "gen-pod")
POD_WORKDIR = "/app"

def run_in_pod(id=1):
    podname = f"{POD_PREFIX}-{str(id).zfill(2)}"
    if 0:
        cmd = "apt-get update "
        cmd = f"kubectl exec {podname} -- {cmd}"
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        cmd = "apt-get install vim tmux -y"
        cmd = f"kubectl exec {podname} -- {cmd}"
        #print(cmd)
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    cmd = "tmux new-session -d -s 0"
    cmd = f"kubectl exec {podname} -- {cmd}"
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    #cmd = "tmux send-keys -t 0 "<command>" "

    fnames = [
        "raga-gen.tar",
        "run_in_image.sh", # put the end
    ]
    # copy new run code
    cmd = f"tar -cvf raga-gen.tar raga-gen"
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    for fname in fnames:
        cmd = f"kubectl cp {fname} {podname}:{POD_WORKDIR}/"
        print(cmd)
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output = result.stdout.decode("utf-8")
    for fname in fnames:
        tmux = "tmux send-keys -t 0 "
        if fname.endswith(".sh"):
            cmd = f""" bash -c "chmod +x {POD_WORKDIR}/{fname} &&  cd {POD_WORKDIR} && {tmux}  'sh ./{fname} 2>&1 | tee log_output.txt' C-m;"  """
        elif fname.endswith(".tar"):
            cmd = f"""  bash -c "cd {POD_WORKDIR} && tar -xvf {POD_WORKDIR}/{fname}" """
        elif fname.startswith("datalake"):
            cmd = f"pip install {POD_WORKDIR}/{fname}"
        cmd = f"kubectl exec {podname} -- {cmd}"
        print(cmd)
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output = result.stdout.decode("utf-8")

for ii in range(1,11+1):
    run_in_pod(ii)
