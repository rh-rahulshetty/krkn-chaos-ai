#!/usr/bin/env bash
set -euo pipefail

# Keep these aligned with install-krkn-ai-operator.sh.
NAMESPACE="krkn-ai"
RELEASE="krkn-operator"
KRKN_OPERATOR_CHART="../krkn-operator/charts/krkn-operator"
OPERATOR_IMAGE="registry.example/krkn-operator:latest"
AI_ORCHESTRATOR_IMAGE="registry.example/krkn-ai:latest"
AI_SERVICE_IMAGE="registry.example/krkn-ai-service:latest"
STORAGE_CLASS=""
STORAGE_SIZE="1Gi"
AI_SERVICE_EXISTING_CLAIM=""

kubectl -n "$NAMESPACE" delete krknairuns,krknscenarioruns --all --ignore-not-found
kubectl -n "$NAMESPACE" wait --for=delete pods,configmaps -l krkn.dev/ai-run --timeout=5m
helm uninstall "$RELEASE" --namespace "$NAMESPACE"

# The ai-service PVC is deliberately retained on uninstall, whether chart-created
# or supplied through aiService.storage.existingClaim. Delete data explicitly only
# after an intentional backup/retention decision.
printf 'Retained ai-service PVC data in namespace %s.\n' "$NAMESPACE"
