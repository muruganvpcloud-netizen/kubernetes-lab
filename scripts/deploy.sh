#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
kubectl apply -f k8s/namespace.yaml
kubectl -n taskboard create configmap taskboard-source --from-file=server.py=app/server.py --dry-run=client -o yaml | kubectl apply -f -
kubectl -n taskboard create configmap taskboard-config --from-literal=APP_VERSION=v1 --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl -n taskboard rollout status deployment/taskboard --timeout=180s
kubectl -n taskboard get pods,svc
