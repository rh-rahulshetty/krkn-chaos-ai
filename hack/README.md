# Krkn-AI operator test workflow

Build and push the three images yourself; the scripts only deploy images already visible to the cluster.

```bash
podman build -t registry.example/krkn-operator:latest ../krkn-operator
podman build -t registry.example/krkn-ai:latest -f containers/Containerfile .
podman build -t registry.example/krkn-ai-service:latest -f containers/Containerfile.server .
podman push registry.example/krkn-operator:latest
podman push registry.example/krkn-ai:latest
podman push registry.example/krkn-ai-service:latest
```

Edit the placeholders at the top of `install-krkn-ai-operator.sh`. To use a pre-created retained PVC, create it first and set `AI_SERVICE_EXISTING_CLAIM`; leaving it empty creates the chart-managed RWO PVC. Either PVC is retained when the release is uninstalled.

```bash
./hack/install-krkn-ai-operator.sh
kubectl -n krkn-ai port-forward service/krkn-operator-operator 8080:8080
```

Create the target request Secret using the managed-cluster layout consumed by the operator:

```bash
kubectl -n krkn-ai create secret generic demo-target \
  --from-literal=managed-clusters='{"provider":{"cluster":{"kubeconfig":"BASE64_KUBECONFIG"}}}'
```

With an authenticated JWT in `$TOKEN`, discover then save the generated configuration:

```bash
curl -sS -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"targetRequestId":"demo-target","targetClusters":{"provider":["cluster"]}}' \
  http://localhost:8080/api/v1/krkn-ai/discoveries

curl -sS -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d "$(jq -n --rawfile config hack/krkn-ai.yaml '{name:"demo-config",configYaml:$config,targetRequestId:"demo-target",targetClusters:{provider:["cluster"]}}')" \
  http://localhost:8080/api/v1/krkn-ai/configs
```

Create and monitor a run with the returned `configId`:

```bash
curl -sS -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"demo-run","configId":"CONFIG_ID","targetRequestId":"demo-target","targetClusters":{"provider":["cluster"]}}' \
  http://localhost:8080/api/v1/krkn-ai/runs
curl -sS -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/v1/krkn-ai/runs
curl -sS -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/v1/krkn-ai/runs/demo-run/results
curl -sS -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/v1/krkn-ai/runs/demo-run/files/RESULT_PATH
```

For direct CR use, place the sample in a ConfigMap and reference its key. `spec.storage` is intentionally absent.

```yaml
apiVersion: krkn.krkn-chaos.dev/v1alpha1
kind: KrknAIRun
metadata:
  name: direct-demo
spec:
  targetRequestId: demo-target
  targetClusters:
    provider: [cluster]
  configMapName: direct-demo-config
  configMapKey: krkn-ai.yaml
```

Retrieve its results through the authenticated API, then remove workloads:

```bash
./hack/delete-krkn-ai-operator.sh
```

The standalone ai-service PVC is never deleted by Helm or the cleanup script; retain it for run history or delete it manually after backup.
