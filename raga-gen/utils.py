import vllm
import argparse
import json
import torch
import time
import os


def banner(s):
    print()
    print(80 * "=")
    print(s)
    print(80 * "=")
    print()


class par:
    pass


class var:
    pass


def get_vllm(par, var):
    var.llm = vllm.LLM(
        model=par.model,
        dtype=torch.float16,
        tensor_parallel_size=par.tp,
        gpu_memory_utilization=0.95,
        # https://github.com/vllm-project/vllm/issues/6641
        max_model_len=64000,
    )

    var.sampling_params = vllm.SamplingParams(
        max_tokens=par.tokens,
        # min_tokens=???,  [before EOS or stop_token_ids is generated]
        # stop_token_ids: List of tokens that stop the generation when they are generated. The returned output will contain the stop tokens unless the stop tokens are special tokens.
        # stop: List of strings that stop the generation when they are generated.  The returned output will not contain the stop strings.
        stop=["<|eot_id|>", "<|eom_id|>", "<end_of_text>"],
        ignore_eos=False,
    )
    """
    <|eom_id|> indicates a continued multi-step reasoning. That is, the model is expecting a continuation message with the output of the tool call.
    """


def get_parser(single_file=False):
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", type=str, required=True)
    parser.add_argument("-t", "--tp", type=int, required=True)
    parser.add_argument("-b", "--batch", type=int, required=True)
    parser.add_argument("-o", "--output", type=str, required=True)
    parser.add_argument("-x", "--tokens", type=int, required=True)
    parser.add_argument("-s", "--start_at", type=int, default=0)
    parser.add_argument("-e", "--end_at", type=int)

    if single_file:
        parser.add_argument("-f", "--file", type=str, required=True)
    else:
        parser.add_argument("-p", "--data_path", type=str, required=True)
        # we need this to devide the jobs
        parser.add_argument("-w", "--num_workers", type=int, required=True)
    return parser


def read_prompt(filepath, start, end, keep_all=False):
    """return
    * a list of text, representing a prompt to LLM
    * a list of dict (when keep_all=True)
    """
    from itertools import islice

    with open(filepath) as input_file:
        if start == 0:
            lines = islice(input_file, start, end)
        else:
            lines = islice(input_file, start - 1, end)
        lines = map(lambda s: s.strip(), lines)
        # lines = list(lines)
        if keep_all:
            lines = [json.loads(line) for line in lines]
        else:
            lines = [json.loads(line)["prompt"] for line in lines]

    return lines
    # for line in lines:
    #     print(line)


def time_get():
    return time.time_ns()


def time_diff(t1, t0):
    return float(t1 - t0) / 1e9


def time_fmt(t):
    t = str(t).zfill(9)
    return "%s.%s" % (t[:-9], t[-9:])


def avg(x):
    return np.mean(x)


def std(x):
    return np.std(x)


def med(x):
    return np.median(x)


def mad(x):
    return med(np.absolute(x - med(x)))


def change_file(current_file):
    new_file = "/model/data/Cosmopedia_Prompts/wikihow.jsonl"
    return new_file if os.path.isfile(new_file) else current_file


def update_prompt(prompts):
    """llama 3.1 instruct prompt"""
    return [
        f"<|begin_of_text|><|start_header_id|>system<|end_header_id|><|eot_id|>\n<|start_header_id|>user<|end_header_id|>{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
        for prompt in prompts
    ]

def update_prompt_exp(prompts):
    # do nothing
    # return prompts

    # https://www.llama.com/docs/model-cards-and-prompt-formats/llama3_1/
    # simplest way to prompt llama-based models
    # return ["<|begin_of_text|>{{ user_message}}" for user_message in prompts]

    return [f"<|begin_of_text|><|start_header_id|>system<|end_header_id|><|eot_id|>\n<|start_header_id|>user<|end_header_id|>{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>" for prompt in prompts]
