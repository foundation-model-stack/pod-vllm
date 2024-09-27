import os


def upload_prompts_data(num_processes=100):
    """
    s3://cos-optimal-llm-pile/torchtitan/outputs/
    """
    from info_cos_llm_pile_south import environ, update_endpoint

    update_endpoint("public")
    s3Client = create_s3Client(environ)
    target_folder = "data/prompts/Cosmopedia_Prompts"
    base_folder = "~/Library/CloudStorage/Box-Box/Project Avengers/Cosmopedia Prompts/"
    print(f"copying from {base_folder} to {target_folder}")
    s3Client.upload_files(
        base_folder,
        prefix=target_folder,
        num_processes=num_processes,
        verbose=True,
    )


def download_prompts_data(num_processes=100):
    """
    s3://cos-optimal-llm-pile/torchtitan/outputs/
    """
    from info_cos_llm_pile_south import environ, update_endpoint

    update_endpoint("public")
    s3Client = create_s3Client(environ)
    base_folder = "data/prompts/Cosmopedia_Prompts"
    target_folder = "/model/data/Cosmopedia_Prompts"
    print(f"copying from {base_folder} to {target_folder}")
    s3Client.download_files(
        base_folder,
        dest_dirname=target_folder,
        num_processes=num_processes,
        verbose=True,
    )


def upload_prompts_data_output(num_processes=100):
    """
    s3://cos-optimal-llm-pile/torchtitan/outputs/
    """
    from info_cos_llm_pile_south import environ, update_endpoint

    update_endpoint("public")
    s3Client = create_s3Client(environ)
    base_folder = "/results/Llama-3.1-405B-FP8_output/"
    target_folder = "data/synthetic_using/Cosmopedia_Prompts"
    print(f"copying from {base_folder} to {target_folder}")
    s3Client.upload_files(
        base_folder,
        prefix=target_folder,
        num_processes=num_processes,
        verbose=True,
    )


def create_s3Client(environ):
    import datalake

    endpoint_type = environ.get("ENDPOINT_TYPE")
    bucket = environ.get("COS_BUCKET")
    region = environ.get("COS_REGION")
    endpoint = environ.get("IBM_COS_ENDPOINT")

    s3Client = datalake.S3Client(
        endpoint,
        bucket,
        access_key=environ["AWS_ACCESS_KEY_ID"],
        secret_key=environ["AWS_SECRET_ACCESS_KEY"],
    )
    return s3Client


def main():
    import time

    tstart = time.time()
    num_processes = 100
    if 1:
        while True:
            upload_prompts_data_output(num_processes=num_processes)
            time.sleep(60 * 60 * 3)  # every 3 hours
    if 0:
        download_prompts_data(num_processes=num_processes)
    if 0:
        upload_prompts_data(num_processes=num_processes)
    print(f"runtime: {time.time()-tstart} (sec)")


if __name__ == "__main__":
    main()
    pass
