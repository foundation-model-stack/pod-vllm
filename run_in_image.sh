#!/bin/bash

source env.sh
export WORKER_POOL="${NUM_PODS:-11}"
export HF_TOKEN=
export BASE_PATH="/model/data/Cosmopedia_Prompts"
export DATA_FILE="${BASE_PATH}/khanacademy.jsonl"
export BASE_OUT_PATH="/results"

# before Huggingface and vllm
export HF_HOME=/model/
export HF_HUB_CACHE=/model/


#REAL
export MODEL_NAME="meta-llama/Meta-Llama-3.1-405B-Instruct-FP8"
export OUTPUT_PATH="${BASE_OUT_PATH}/Llama-3.1-405B-FP8_output/"

# DEBUG
#export MODEL_NAME="meta-llama/Meta-Llama-3.1-8B-Instruct"
#export OUTPUT_PATH="${BASE_OUT_PATH}/Llama-3.1-8B-FP8_output/"

huggingface-cli login --token ${HF_TOKEN}
#huggingface-cli download "${MODEL_NAME}" --include "original/*" --local-dir "${MODEL_PATH}"

# -t <num-GPU> : tensor parallel
chmod +x raga-gen/gen2
# SINGLE FILE
#cd raga-gen; PYTHONUNBUFFERED=1 ./gen2 -m "${MODEL_NAME}"  -t 8 -b 1 -f "${DATA_FILE}" -o "${OUTPUT_PATH}" -x 16384
# OR
# -w 11 = 11 pods
#cd raga-gen; PYTHONUNBUFFERED=1 ./gen2 -m "${MODEL_NAME}"  -t 1 -b 1 -p "${BASE_PATH}" -w 11 -o "${OUTPUT_PATH}" -x 16384  # debug
cd raga-gen; PYTHONUNBUFFERED=1 ./gen2 -m "${MODEL_NAME}"  -t 8 -b 1 -p "${BASE_PATH}" -w ${WORKER_POOL} -o "${OUTPUT_PATH}" -x 16384
cd -
