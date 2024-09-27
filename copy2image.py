import os
import subprocess
from utils import load_environment_from_shell_script


load_environment_from_shell_script("env.sh")
NUM_PODS = int(os.environ.get("NUM_PODS", 11))
POD_PREFIX = os.environ.get("POD_PREFIX")
POD_WORKDIR = os.environ.get("POD_WORKDIR")

print(f"We are copying to {NUM_PODS} pods")


def copy2pod(id=1):
    podname = f"{POD_PREFIX}-{str(id).zfill(2)}"

    if 0:
        cmd = "apt-get update "
        cmd = f"kubectl exec {podname} -- {cmd}"
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        cmd = "apt-get install vim tmux -y"
        cmd = f"kubectl exec {podname} -- {cmd}"
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )

    fnames = [
        "raga-gen.tar",
        "datalake-0.19.0.tar.gz",
        "run_in_image.sh",  # put at the end
    ]
    cmd = "tar -cvf raga-gen.tar raga-gen"
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    for fname in fnames:
        cmd = f"kubectl cp {fname} {podname}:{POD_WORKDIR}/"

        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        _ = result.stdout.decode("utf-8")
    for fname in fnames:
        tmux = "tmux new-session -d "
        if fname.endswith(".sh"):
            cmd = tmux + f"{POD_WORKDIR}/{fname}"
            continue
        elif fname.endswith(".tar"):
            cmd = f"""  bash -c "cd {POD_WORKDIR} && tar -xvf {POD_WORKDIR}/{fname}" """
        elif fname.startswith("datalake"):
            cmd = f"pip install {POD_WORKDIR}/{fname}"
        cmd = f"kubectl exec {podname} -- {cmd}"
        # print(cmd)

        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        _ = result.stdout.decode("utf-8")


for ii in range(1, NUM_PODS + 1):
    copy2pod(ii)
    print(f"done pod {ii}")
