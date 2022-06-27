#!/bin/bash

ROOT_PATH=./kubernetes

function run_kustomize() {
  echo -n "Running kustomize in ${1} ... "
  out=$(cd "${1}" && kustomize build 2>&1)
  if [ $? -ne 0 ]; then
    echo FAILED
    echo "${out}"
    exit 1
  else
    echo OK
  fi
}

for k in $(find ${ROOT_PATH} -iname kustomization.yml -exec dirname {} \;); do
  run_kustomize "${k}"
done
