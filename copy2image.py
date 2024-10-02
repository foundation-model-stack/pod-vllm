import os
import subprocess
from utils import load_environment_from_shell_script


load_environment_from_shell_script("env.sh")
NUM_PODS = int(os.environ.get("NUM_PODS"))
POD_PREFIX = os.environ.get("POD_PREFIX")
POD_WORKDIR = os.environ.get("POD_WORKDIR")
START_OFFSET = int(os.environ.get("SKIP_PODS", 0)) + 1

print(f"We are copying to {NUM_PODS-START_OFFSET+1} pods")


class Copy2Pod:
    def __init__(self, shared_path=None):
        self.shared_path = shared_path
        self.first_run = True

    def __call__(self, id=1):
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
            "datalake-0.20.0.tar.gz",
            "copy_data.py",
            "run_in_image.sh",  # put at the end
        ]
        cmd = "tar -cvf raga-gen.tar raga-gen"
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        shared_path = self.shared_path
        if shared_path is not None:
            if self.first_run:
                cmd = f"kubectl exec {podname} -- mkdir -p {shared_path}"
                print(cmd)

                result = subprocess.run(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
                )
                _ = result.stdout.decode("utf-8")
                for fname in fnames:
                    cmd = f"kubectl cp {fname} {podname}:{shared_path}/"

                    result = subprocess.run(
                        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
                    )
                    _ = result.stdout.decode("utf-8")
                self.first_run = False
            if not self.first_run:
                for fname in fnames:
                    cmd = f"kubectl exec {podname} -- cp {shared_path}/{fname} {POD_WORKDIR}/"

                    result = subprocess.run(
                        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
                    )
                    _ = result.stdout.decode("utf-8")
        else:
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


shared_path = "/model/from_local/"
copy = Copy2Pod(shared_path)
for ii in range(START_OFFSET, NUM_PODS + 1):
    # copy2pod(ii)
    copy(ii)
    print(f"done pod {ii}")
