#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
kubectl -n taskboard create configmap taskboard-source --from-file=server.py=app/server.py --dry-run=client -o yaml | kubectl apply -f -
kubectl -n taskboard rollout restart deployment/taskboard
kubectl -n taskboard rollout status deployment/taskboard --timeout=180s
