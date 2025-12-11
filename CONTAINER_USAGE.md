# Krkn-AI Container Usage Guide

This container packages krkn-ai CLI with podman and krknctl to enable chaos engineering workflows.

## Building the Container

```bash
podman build -t krkn-ai:latest -f Containerfile .
```

## Running the Container

The container supports two modes controlled by the `MODE` environment variable:

### 1. Discovery Mode

Discovers cluster components and generates a configuration file.

**Usage:**
```bash
podman run --rm \
  -v ./tmp/container-test:/mount:Z \
  -e MODE="discover" \
  -e KUBECONFIG="/mount/kubeconfig.yaml" \
  -e OUTPUT_DIR="/mount/" \
  -e NAMESPACE="robot-shop" \
  -e POD_LABEL="service" \
  -e NODE_LABEL="kubernetes.io/hostname" \
  -e SKIP_POD_NAME="nginx-proxy.*" \
  -e VERBOSE="2" \
  krkn-ai:latest
```

**Environment Variables (Discovery):**
- `MODE=discover` (required)
- `KUBECONFIG` (required) - Path to kubeconfig file (default: `/input/kubeconfig`)
- `OUTPUT_DIR` (optional) - Output directory (default: `/output`)
- `NAMESPACE` (optional) - Namespace pattern (default: `.*`)
- `POD_LABEL` (optional) - Pod label pattern (default: `.*`)
- `NODE_LABEL` (optional) - Node label pattern (default: `.*`)
- `SKIP_POD_NAME` (optional) - Pod names to skip (comma-separated regex)
- `VERBOSE` (optional) - Verbosity level 0-2 (default: `0`)

### 2. Run Mode

Executes chaos engineering tests based on a configuration file.

**Usage:**

```bash
podman run --rm \
  -v ./input:/input:Z \
  -v ./output:/output:Z \
  -e MODE=run \
  -e CONFIG_FILE=/input/krkn-ai.yaml \
  -e RUNNER_TYPE=krknctl \
  -e FORMAT=json \
  -e EXTRA_PARAMS="key1=value1,key2=value2" \
  -e VERBOSE=2 \
  krkn-ai:latest
```

**Environment Variables (Run):**
- `MODE=run` (required)
- `KUBECONFIG` (required) - Path to kubeconfig file (default: `/input/kubeconfig`)
- `CONFIG_FILE` (required) - Path to krkn-ai config file (default: `/input/krkn-ai.yaml`)
- `OUTPUT_DIR` (optional) - Output directory (default: `/output`)
- `FORMAT` (optional) - Output format: `json` or `yaml` (default: `yaml`)
- `RUNNER_TYPE` (optional) - Runner type: `krknctl` or `krknhub`
- `EXTRA_PARAMS` (optional) - Additional parameters in `key=value` format (comma-separated)
- `VERBOSE` (optional) - Verbosity level 0-2 (default: `0`)

## Directory Structure

The container expects the following mount points:

- `/input` - Input files (kubeconfig, config files)
- `/output` - Output files (generated configs, results, logs)

## Complete Workflow Example

### Step 1: Prepare your files
```bash
mkdir -p input output
cp ~/.kube/config input/kubeconfig
```

### Step 2: Discover cluster components
```bash
podman run --rm \
  -v ./input:/input:Z \
  -v ./output:/output:Z \
  -e MODE=discover \
  -e KUBECONFIG=/input/kubeconfig \
  -e NAMESPACE="default" \
  krkn-ai:latest
```

This generates `output/krkn-ai.yaml`

### Step 3: Edit the generated config if needed
```bash
vim output/krkn-ai.yaml
```

### Step 4: Run chaos tests
```bash
cp output/krkn-ai.yaml input/
podman run --rm \
  -v ./input:/input:Z \
  -v ./output:/output:Z \
  -e MODE=run \
  -e CONFIG_FILE=/input/krkn-ai.yaml \
  -e RUNNER_TYPE=krknctl \
  krkn-ai:latest
```

### Step 5: Check results
```bash
ls -la output/
cat output/run.log
```

## Podman Considerations

When using krknctl within the container, you may need to run with additional privileges:

```bash
podman run --rm \
  --privileged \
  -v ./input:/input:Z \
  -v ./output:/output:Z \
  -e MODE=run \
  -e CONFIG_FILE=/input/krkn-ai.yaml \
  -e RUNNER_TYPE=krknctl \
  krkn-ai:latest
```

## Troubleshooting

### Issue: Permission denied on mounted volumes
**Solution:** Use `:Z` suffix on volume mounts for SELinux systems

### Issue: Kubeconfig not found
**Solution:** Ensure the kubeconfig file exists in your input directory and the path is correct

### Issue: Podman-in-podman not working
**Solution:** Run the container with `--privileged` flag

### View help
```bash
podman run --rm krkn-ai:latest
# This will show usage information
```

## Building for Different Architectures

```bash
# For ARM64
podman build --platform linux/arm64 -t krkn-ai:latest-arm64 -f Containerfile .

# For AMD64
podman build --platform linux/amd64 -t krkn-ai:latest-amd64 -f Containerfile .
```

## Version Information

- Base Image: Fedora 41
- Python: 3.12
- Podman: Latest (from Fedora repos)
- krknctl: v0.10.15-beta (configurable via build arg)

To build with a different krknctl version:
```bash
podman build --build-arg KRKNCTL_VERSION=v0.10.14-beta -t krkn-ai:latest -f Containerfile .
```

