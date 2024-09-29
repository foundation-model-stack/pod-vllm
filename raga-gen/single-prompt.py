from utils import *
import utils

# get_parser, par, var, get_vllm, banner, read_prompt
import os


def main():
    banner("parameters")

    single_file = True
    parser = get_parser(single_file)
    parser.parse_args(namespace=par)

    start = par.start_at
    end = par.end_at

    get_vllm(par, var)

    while True:
        import importlib

        input("Press Enter to continue...")
        importlib.reload(utils)
        # reload with a different input file
        par.file = utils.change_file(par.file)
        print(par.file)
        var.prompts = read_prompt(par.file, start, end, keep_all=True)

        i = 0
        if isinstance(var.prompts[0], dict):
            # process dict
            save_full_dict = True
            prompts = [
                x["prompt"] for x in var.prompts[i * par.batch : (i + 1) * par.batch]
            ]
        else:
            prompts = var.prompts[i * par.batch : (i + 1) * par.batch]

        from utils import update_prompt_exp

        prompts = update_prompt_exp(prompts)

        if not os.path.exists(par.output):
            os.makedirs(par.output)

        t0 = time_get()
        outputs = var.llm.generate(prompts, var.sampling_params)
        t1 = time_get()
        dt = time_diff(t1, t0)
        import pprint

        for output in outputs:
            for out in output.outputs:
                var.prompts[i]["response"] = out.text  # .replace("\n", "\\n")
                print("===PROMPT===")
                print(prompts[i])
                print("===RESPONSE===")
                pprint.pprint(out.text)
                print("===END RESPONSE===")
                f = open(
                    "%s/%s.txt" % (par.output, os.path.basename(par.file)),
                    "a",
                    encoding="utf-8",
                )
                f.write(json.dumps(var.prompts[i]))
                f.write("\n")
                f.close()


if __name__ == "__main__":
    main()
