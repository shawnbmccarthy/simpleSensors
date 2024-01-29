#!/bin/bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

# setup virtual environment if needed
if [[ ! -f ${SCRIPT_DIR}/venv/bin/python ]]; then
  echo "[INFO] Attempting to setup python environment"
  python3 -m venv "${SCRIPT_DIR}"/venv --system-site-packages &> /dev/null
  VRVAL=$?
  "${SCRIPT_DIR}"/venv/bin/python -m pip install -r "${SCRIPT_DIR}"/requirements.txt &> /dev/null
  RRVAL=$?
  if [[ ${VRVAL} -ne 0 ]]; then
    echo "[ERROR] Problem setting up virtual environment, cannot continue (please   review errors in log)"
    exit 1
  fi

  if [[ ${RRVAL} -ne 0 ]]; then
    echo "[ERROR] Problem installing requirements, cannot continue (please review errors in log)"
    exit 1
  fi
fi

# TODO: Error checking for empty string
RUST_UTILS_SO=$(find "${SCRIPT_DIR}" -name libviam_rust_utils.so -printf '%h')
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${RUST_UTILS_SO}

# Source env file
if [[ -f ./env.sh ]]; then
  source ./env.sh
else
  echo "[ERROR] please setup env.sh that can be sourced for api secret"
  exit 1
fi

if [[ -z ${API_KEY} || -z ${API_KEY_ID} || -z ${ROBOT_ADDRESS} ]]; then
  echo "[ERROR] missing env variable - API_KEY, API_KEY_ID, or ROBOT_ADDRESS"
  exit 1
fi

exec "${SCRIPT_DIR}"/venv/bin/python "${SCRIPT_DIR}"/client.py "$@"