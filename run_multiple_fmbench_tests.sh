#!/bin/bash

# Script to run multiple FMBench configurations
CONDA_ENV_PATH=$CONDA_PREFIX/lib/python3.11/site-packages
# mention the ame of the model folder that needs to be benchmarked
# This code can be changed to add multiple model files and loop through each of the 
# model and benchmark config files for each of the models
MODEL_NAME='mistral'
CONFIG_DIR="./src/fmbench/configs/$MODEL_NAME"

# list the name of the config files that are to be tested in the given order.
# make sure that the general name of each of the config file is different so that
# the result folders are separately generated for each of the config file they do not
# override each other
CONFIG_FILES=(
    "config-mistral-trn1-32xl-deploy-ec2-tp32.yml"
    "config-mistral-trn1-32xl-deploy-ec2-tp16.yml"
)
LOGFILE="fmbench_multiple_tests_run.log"

# Function to log messages to both console and log file
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOGFILE"
}

# Function to run FMBench for a single configuration file
run_fmbench() {
    local config_file="$1"
    log_message "Starting FMBench run with config: $config_file"
    
    # Delete existing install
    log_message "Deleting existing FMBench installation"
    rm -rf $CONDA_ENV_PATH/fmbench*

    # Build a new version
    log_message "Building and installing new FMBench version"
    poetry build >> "$LOGFILE" 2>&1
    pip install -U dist/*.whl >> "$LOGFILE" 2>&1

    # Run FMBench
    log_message "Running FMBench"
    fmbench --config-file "$config_file" --local-mode yes --write-bucket placeholder --tmp-dir /tmp >> "$LOGFILE" 2>&1

    # Kill the docker container and remove it
    log_message "Stopping and removing Docker container that was currently running"
    docker stop fmbench_model_container >> "$LOGFILE" 2>&1
    docker rm fmbench_model_container >> "$LOGFILE" 2>&1

    log_message "Completed FMBench run for $config_file"
    log_message "----------------------------------------"
}

# Main execution
log_message "Starting multi-run FMBench script"

for config_file in "${CONFIG_FILES[@]}"; do
    full_config_path="$CONFIG_DIR/$config_file"
    if [ -f "$full_config_path" ]; then
        run_fmbench "$full_config_path"
    else
        log_message "Config file not found: $full_config_path"
    fi
done

log_message "All FMBench runs completed"