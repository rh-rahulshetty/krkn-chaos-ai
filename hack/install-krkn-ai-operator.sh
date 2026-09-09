#!/usr/bin/env bash
set -euo pipefail

# Edit these placeholders for the images and chart already available to your cluster.
NAMESPACE="krkn-ai"
RELEASE="krkn-operator"
KRKN_OPERATOR_CHART="../krkn-operator/charts/krkn-operator"
OPERATOR_IMAGE="registry.example/krkn-operator:latest"
AI_ORCHESTRATOR_IMAGE="registry.example/krkn-ai:latest"
AI_SERVICE_IMAGE="registry.example/krkn-ai-service:latest"
STORAGE_CLASS=""
STORAGE_SIZE="1Gi"
# Set this to a pre-created RWO claim to retain control of its lifecycle.
AI_SERVICE_EXISTING_CLAIM=""

helm_args=(
  upgrade --install "$RELEASE" "$KRKN_OPERATOR_CHART"
  --namespace "$NAMESPACE" --create-namespace
  --set-string "images.operator.image=$OPERATOR_IMAGE"
  --set-string "images.aiOrchestrator.image=$AI_ORCHESTRATOR_IMAGE"
  --set-string "images.aiService.image=$AI_SERVICE_IMAGE"
  --set-string "aiService.storage.storageClassName=$STORAGE_CLASS"
  --set-string "aiService.storage.size=$STORAGE_SIZE"
)
if [[ -n "$AI_SERVICE_EXISTING_CLAIM" ]]; then
  helm_args+=(--set-string "aiService.storage.existingClaim=$AI_SERVICE_EXISTING_CLAIM")
fi
helm "${helm_args[@]}"

kubectl -n "$NAMESPACE" rollout status "deployment/${RELEASE}-operator" --timeout=5m
kubectl -n "$NAMESPACE" rollout status "deployment/${RELEASE}-ai-service" --timeout=5m
printf 'Operator API: kubectl -n %s port-forward service/%s-operator 8080:8080\n' "$NAMESPACE" "$RELEASE"
