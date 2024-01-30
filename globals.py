import os
import yaml
from enum import Enum
from pathlib import Path
import boto3
from datetime import datetime

CONFIG_FILEPATH_FILE: str = "config_filepath.txt"

# S3 client initialization
s3_client = boto3.client('s3')

## Configuring the role ARN
ROLE_ARN = boto3.client('sts').get_caller_identity().get('Arn').replace('user/', 'user-')

CONFIG_FILE: str = Path(CONFIG_FILEPATH_FILE).read_text()
print(f"CONFIG_FILE={CONFIG_FILE}")
with open(CONFIG_FILE, 'r') as file:
    config = yaml.safe_load(file)

## data directory and prompts
PER_ACCOUNT_DIR: str = f"{config['general']['name']}-{ROLE_ARN}"
DATA_DIR: str = os.path.join(PER_ACCOUNT_DIR, config['dir_paths']['data_prefix'])
PROMPTS_DIR = os.path.join(DATA_DIR, config['dir_paths']['prompts_prefix'])

## --------------------- Metrics directory based on date and time ---------------------------
current_time = datetime.now()

## Adding minutes for greater detail of when and how the results/endpoint was deployed
formatted_time = current_time.strftime("%Y/%m/%d/%H/%M")

# METRICS_DIR = f"{config['dir_paths']['data_prefix']}/metrics/{formatted_time}/{config['general']['name']}-{ROLE_ARN}"
METRICS_DIR = f"{DATA_DIR}/metrics/{formatted_time}/{config['general']['name']}"

METRICS_PER_INFERENCE_DIR  = os.path.join(METRICS_DIR, "per_inference")
METRICS_PER_CHUNK_DIR  = os.path.join(METRICS_DIR, "per_chunk")


## --------------------- Models directory based on date and time ---------------------------
MODELS_DIR = f"{DATA_DIR}/models/{config['general']['name']}"

## Use this to upload to the s3 bucket (extracted from the config file)
BUCKET_NAME = config['aws']['bucket']
READ_BUCKET_NAME = config['s3_read_data']['read_bucket']

## S3 prefix
PREFIX_NAME = config['dir_paths']['data_prefix']

## SOURCE data is where your actual data resides in s3
SOURCE_DATA = config['s3_read_data']['source_data_prefix']

## Read the prompt template that the user uploads
PROMPT_TEMPLATE_S3_PREFIX = config['s3_read_data']['prompt_template_dir']

## Initialize the scripts directory
SCRIPTS_DIR: str = "scripts"

DIR_LIST = [DATA_DIR, PROMPTS_DIR, METRICS_DIR, MODELS_DIR, METRICS_PER_INFERENCE_DIR, METRICS_PER_CHUNK_DIR]

## this is for custom tokenizers
TOKENIZER_DIR_S3 = config['s3_read_data']['tokenizer_prefix']
TOKENIZER = 'tokenizer'

DEPLOYMENT_SCRIPT_S3 = config['s3_read_data']['scripts_prefix']

_ = list(map(lambda x: os.makedirs(x, exist_ok=True), DIR_LIST))

## Define the endpoint list as the config-general name plus the role arn for unique generation from different roles in the same/different accounts
ENDPOINT_LIST_PATH:str = os.path.join(MODELS_DIR, "endpoints.json")

REQUEST_PAYLOAD_FPATH:str = os.path.join(PROMPTS_DIR, "payload.jsonl")
RESULTS_FPATH:str = os.path.join(METRICS_DIR, "results.csv")
class TRUNCATE_POLICY(str, Enum):
    AT_PROMPT_TOKEN_LENGTH = 'at-prompt-token-length'

# misc. metrics related
PLACE_HOLDER: int = -1705338041

# metric filenames
COUNTS_FNAME: str = "experiment_counts.csv"
ERROR_RATES_FNAME: str = "error_rates.csv"
RESULTS_DESC_MD_FNAME: str = "results.md"
SUMMARY_METRICS_W_PRICING_FNAME: str = "summary_metrics_w_pricing.csv"
INSTANCE_PRICING_PER_HOUR_FNAME: str = "instance_pricing_per_hour.csv"
SUMMARY_METRICS_FOR_DATASET_W_SCORES_FNAME: str = "summary_metrics_for_dataset_w_scores.csv"
SUMMARY_METRICS_FOR_DATASET_W_SCORES_BEST_OPTION_FNAME: str = "summary_metrics_for_dataset_best_option.csv"
SUMMARY_METRICS_FOR_DATASET_W_SCORES_BEST_OPTION_EACH_INSTANCE_TYPE_FNAME: str = "summary_metrics_for_dataset_best_option_each_instance_type.csv"
BUSINESS_SUMMARY_PLOT_FNAME: str = "business_summary.png"

# plot filenames
ERROR_RATES_PLOT_TEXT: str = "Error rates for different concurrency levels and instance types"
ERROR_RATES_PLOT_FNAME: str = "error_rates.png"
TOKENS_VS_LATENCY_PLOT_TEXT: str = "Tokens vs latency for different concurrency levels and instance types"
TOKENS_VS_LATENCY_PLOT_FNAME: str = "tokens_vs_latency.png"
CONCURRENCY_VS_INFERENCE_LATENCY_PLOT_FNAME: str = "concurrency_vs_inference_latency.png"
CONCURRENCY_VS_INFERENCE_LATENCY_PLOT_TEXT: str = "Concurrency Vs latency for different instance type for selected dataset"


LATENCY_BUDGET: int = 20

OVERALL_RESULTS_MD: str = """
# Results for performance benchmarking

**Last modified (UTC): {dttm}**

## Summary

{business_summary}

## Per instance results

The following table provides the best combinations for running inference for different sizes prompts on different instance types.
|Dataset   | Instance type   | Recommendation   |
|---|---|---|
"""

## Dataset=`{dataset}`, instance_type=`{instance_type}`
RESULT_DESC: str = """The best option for staying within a latency budget of `{latency_budget} seconds` on a `{instance_type}` for the `{dataset}` dataset is a `concurrency level of {concurrency}`. A concurrency level of {concurrency} achieves an `average latency of {latency_mean} seconds`, for an `average prompt size of {prompt_size} tokens` and `completion size of {completion_size} tokens` with `{tpm} transactions/minute`."""

RESULT_ROW: str = "|`{dataset}`|`{instance_type}`|{desc}|"

RESULT_FAILURE_DESC: str = """This experiment did not find any combination of concurrency level and other configuration settings that could provide a response within a latency budget of `{latency_budget} seconds` on a `{instance_type}` for the `{dataset}` dataset."""
