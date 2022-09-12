#!/bin/bash
kubectl get secret keycloak-client-secret-regapp-client -n keycloak -o json | \
jq .metadata='{"namespace": "regapp", "name": "keycloak-client-secret-regapp"}' | \
kubectl apply -f -
