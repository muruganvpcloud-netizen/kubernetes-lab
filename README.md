# Killercoda TaskBoard — complete beginner lab

## 0. Read this first
This is a **real runnable CRUD web application**, but **Killercoda is Kubernetes, not GKE**. It is a temporary learning environment; it is not permanent hosting. You do not need a Google Cloud account, a credit card, Maven, Docker Hub, or Docker builds for the recommended sandbox route. The project also includes a production-style Dockerfile for separate container practice. The app intentionally stores tasks **in each Python process's memory**: restarting a Pod loses changes, and scaling above one replica creates inconsistent task lists. That is an intentional learning exercise; a durable production version needs a database/shared storage.

The recommended deployment mounts the application's actual `app/server.py` as a Kubernetes ConfigMap into an official `python:3.12-alpine` container. This lets you deploy **your own code** without needing to build/push a custom image inside an ephemeral sandbox. The image must be downloadable by the sandbox. For production, use a built and versioned image instead of ConfigMap-mounted source.

## 1. What each file is for
- `app/server.py`: complete backend HTTP server and HTML/CSS/JavaScript browser frontend; no third-party Python libraries.
- `tests/test_api.py`: HTTP integration tests for health, create/list/update/delete and validation.
- `Dockerfile`: optional real custom image build, using a non-root user.
- `k8s/namespace.yaml`: separates lab resources from other workloads.
- `k8s/deployment.yaml`: Pod specification, one replica, health probes, CPU/memory resources and code mount.
- `k8s/service.yaml`: stable internal virtual IP and DNS for the Pod.
- `scripts/deploy.sh`: repeatable setup and deployment.
- `scripts/update.sh`: updates source ConfigMap and restarts Pods.

## 2. Vocabulary
- **Source code**: text that tells the application what to do.
- **HTTP**: browser/API request-response protocol.
- **REST API**: URLs and HTTP verbs (GET, POST, PATCH, DELETE) for application operations.
- **Container image**: packaged filesystem and startup instructions for a process.
- **Pod**: Kubernetes unit running one or more containers.
- **Deployment**: controller that creates/replaces Pods and maintains a desired count.
- **Replica**: one Pod instance of the application.
- **Service**: stable address that forwards requests to selected Pods.
- **Namespace**: logical grouping of resources.
- **ConfigMap**: non-secret configuration; here it also stores the small demo source file.
- **Probe**: Kubernetes health test for container startup, readiness, or liveness.
- **kubectl**: command-line client that communicates with the Kubernetes API server.
- **Port-forward**: temporary tunnel from a terminal port to a Service/Pod port.

## 3. Before opening Killercoda
1. Download `killercoda-taskboard.zip` to your PC. Keep it for your teammate; sandbox data is temporary.
2. Open https://killercoda.com/playgrounds/scenario/kubernetes and start a Kubernetes playground. Sign in if prompted.
3. Identify the browser-based Linux terminal (often named `controlplane`). **Every shell command below is run in that Killercoda terminal**, not Windows PowerShell, unless explicitly stated otherwise.
4. Verify the cluster is ready:
   ```bash
   kubectl version --client
   kubectl cluster-info
   kubectl get nodes -o wide
   ```
   Why: confirm `kubectl` exists, is connected to the cluster, and at least one node is Ready. If a node is `NotReady`, wait and retry before proceeding.
5. Verify tools: `command -v python3; command -v unzip; command -v curl; command -v kubectl`. If `unzip` is unavailable, you can extract on your PC and upload files individually or use Python's `zipfile` module as shown below.

## 4. Transfer source files into the sandbox
**Option A (simplest when the Killercoda terminal provides an Upload File control):** Upload `killercoda-taskboard.zip` to the terminal working directory. Confirm with `pwd; ls -lh`. If the upload UI is unavailable, use Option B.

**Option B (share via GitHub):** On your PC, unzip the archive, create a GitHub repository and upload the contents, preserving the directories. In Killercoda terminal run `git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git` and `cd YOUR-REPOSITORY`. Replace the placeholder URL with your actual repository. Never paste passwords or access tokens into commands or public repositories.

For Option A, in Killercoda terminal:
```bash
pwd
ls -lh
python3 -m zipfile -e killercoda-taskboard.zip .
cd killercoda-taskboard
ls -la
find . -maxdepth 3 -type f | sort
```
Why: extract and inspect the real application files. If your upload went to another directory, navigate there first. If Python is missing on the host, use `unzip killercoda-taskboard.zip` instead.

## 5. Read the source and run automated tests (optional but recommended)
In Killercoda terminal:
```bash
sed -n '1,100p' app/server.py
cat Dockerfile
cat k8s/deployment.yaml
python3 -m unittest discover -s tests -v
```
Why: understand what is deployed and test the API logic before using Kubernetes. If host Python is missing, run the tests on your PC with Python 3.9+ or skip this step; the Kubernetes deployment itself uses Python inside a container.
Expected: three tests pass. The tests start a temporary HTTP server on port 18080, perform requests and stop it.

## 6. Deploy to Kubernetes (recommended: no registry or custom build)
In Killercoda terminal, from the extracted project directory:
```bash
pwd
bash scripts/deploy.sh
```
What the script does, in order:
1. `kubectl apply -f k8s/namespace.yaml` creates namespace `taskboard` (safe to re-run).
2. `kubectl create configmap ... --from-file=server.py=app/server.py --dry-run=client -o yaml | kubectl apply -f -` uploads your real source file as a Kubernetes ConfigMap.
3. Another ConfigMap sets `APP_VERSION=v1`.
4. Applies Deployment: Kubernetes pulls `python:3.12-alpine`, mounts `server.py` at `/app/server.py`, and runs `python /app/server.py` on port 8080.
5. Applies Service: forwards port 80 to Pod port 8080.
6. Waits for readiness and prints Pod and Service status.

Verify separately:
```bash
kubectl get namespace taskboard
kubectl -n taskboard get configmaps
kubectl -n taskboard get deployments
kubectl -n taskboard get pods -o wide
kubectl -n taskboard get services
kubectl -n taskboard describe deployment taskboard
```
Expected: Deployment `1/1`, one Pod `1/1 Running`, and `taskboard` Service `ClusterIP`, port `80/TCP`. If not, use troubleshooting section.

## 7. Test the application from inside the cluster
From Killercoda terminal:
```bash
kubectl -n taskboard run curl-test --rm -i --restart=Never --image=curlimages/curl -- curl -fsS http://taskboard/health
kubectl -n taskboard run curl-tasks --rm -i --restart=Never --image=curlimages/curl -- curl -fsS http://taskboard/api/tasks
```
Why: verifies the Service name resolves through Kubernetes DNS and the API responds. Some playgrounds take a little time to download the `curlimages/curl` image.

## 8. Host/view the application in the sandbox
In Killercoda terminal run:
```bash
kubectl -n taskboard port-forward --address 0.0.0.0 service/taskboard 8080:80
```
Leave this terminal running. **Do not close it**. If Killercoda offers an `Open Port`, `Traffic`, or port-preview interface, select port **8080** to open the web UI in your browser. The availability and exact placement of this feature depend on the current playground UI. If there is no preview option, open a second Killercoda terminal and test `curl http://127.0.0.1:8080/` from there. The app is hosted temporarily in the sandbox, not on a durable public website.

**Security note:** `--address 0.0.0.0` makes the forwarded port listen on all sandbox interfaces; use only for this non-sensitive demonstration. For terminal-only testing, omit `--address 0.0.0.0` (default loopback).

## 9. Test every API endpoint (second Killercoda terminal)
Keep the port-forward running in the first terminal. In a second terminal:
```bash
curl -i http://127.0.0.1:8080/health
curl -i http://127.0.0.1:8080/ready
curl -s http://127.0.0.1:8080/api/tasks
curl -i -X POST http://127.0.0.1:8080/api/tasks -H 'Content-Type: application/json' -d '{"title":"Test a real REST API"}'
curl -s http://127.0.0.1:8080/api/tasks
```
Copy the `id` returned by POST. Replace `YOUR-ID` below with that ID (without brackets):
```bash
curl -i -X PATCH http://127.0.0.1:8080/api/tasks/YOUR-ID -H 'Content-Type: application/json' -d '{"done":true}'
curl -i -X DELETE http://127.0.0.1:8080/api/tasks/YOUR-ID
curl -s http://127.0.0.1:8080/api/tasks
```
Why: GET retrieves; POST creates (201); PATCH updates; DELETE removes; `/health` and `/ready` let Kubernetes check the process.

## 10. Operate the deployment
In Killercoda terminal:
```bash
kubectl -n taskboard logs deployment/taskboard --tail=50
kubectl -n taskboard get pods -o wide
kubectl -n taskboard describe pod $(kubectl -n taskboard get pods -o jsonpath='{.items[0].metadata.name}')
kubectl -n taskboard get events --sort-by=.lastTimestamp
kubectl -n taskboard get endpointslices -l kubernetes.io/service-name=taskboard
```
Why: logs show application HTTP requests; describe shows probes/image/volumes/restarts; events show scheduling/pull errors; EndpointSlices show Service backends.

### Pod recovery experiment
```bash
kubectl -n taskboard delete pod -l app=taskboard
kubectl -n taskboard rollout status deployment/taskboard --timeout=180s
kubectl -n taskboard get pods
```
Why: Deployment creates a replacement Pod. Note that in-memory task changes are lost.

### Scaling experiment (read warning first)
```bash
kubectl -n taskboard scale deployment/taskboard --replicas=2
kubectl -n taskboard get pods -w
```
Press Ctrl+C to stop watching. Then run:
```bash
kubectl -n taskboard scale deployment/taskboard --replicas=1
kubectl -n taskboard rollout status deployment/taskboard
```
Why: practice horizontal scaling. **Do not rely on task CRUD correctness with two replicas**: each Pod has a separate in-memory task list. This intentionally demonstrates why production apps need a shared database.

## 11. Change source and roll out an update
In Killercoda terminal, from project root:
```bash
cp app/server.py app/server.py.backup
sed -i 's/Kubernetes TaskBoard/Kubernetes TaskBoard Lab/g' app/server.py
bash scripts/update.sh
kubectl -n taskboard rollout history deployment/taskboard
kubectl -n taskboard rollout status deployment/taskboard
```
Why: changes the HTML title, refreshes the source ConfigMap, and recreates the Pod so it reads the new code. Refresh the browser to see the change.

Rollback caution: `kubectl rollout undo deployment/taskboard` only rolls back the Deployment Pod template, **not ConfigMap content**. To restore source:
```bash
cp app/server.py.backup app/server.py
bash scripts/update.sh
```
This is a demonstration of why production builds use immutable, versioned images.

## 12. Troubleshooting
- `kubectl: command not found`: you're not in a Kubernetes-enabled terminal; restart the correct scenario.
- `The connection to the server was refused`: Kubernetes control plane may not be ready; check `kubectl cluster-info` and `kubectl get nodes`.
- `ImagePullBackOff`: check internet access/image pulls and `kubectl -n taskboard describe pod PODNAME`; sandbox may restrict pulls.
- `CrashLoopBackOff`: run `kubectl -n taskboard logs deployment/taskboard --previous` and check mounted source.
- `0/1 Ready`: inspect readiness probe and logs; app should listen on `0.0.0.0:8080`.
- `curl: connection refused` on localhost: start port-forward and keep its terminal open.
- `curl` not installed on host: use the temporary curl Pod from section 7.
- Browser preview doesn't work: use `curl` inside the sandbox; public browser preview is sandbox-feature-dependent.
- Source changed but page didn't: use `bash scripts/update.sh` to restart Pods; refresh browser.
- Task disappeared after restart: expected, because there is no persistent database.
- 2 replicas show different tasks: expected, because there is no shared state.
- `python3` missing in host terminal: application still runs using Python in the Kubernetes container; use `unzip` and skip host tests.

## 13. Cleanup
From Killercoda terminal:
```bash
kubectl delete namespace taskboard
kubectl get namespace taskboard
```
Stop port-forward with Ctrl+C. No Google Cloud billing resources were created by this lab. The sandbox may also expire automatically; always retain your ZIP or GitHub repository.

## 14. Optional real Docker build (outside the default sandbox flow)
On a machine with Docker installed, from project root:
```bash
docker build -t taskboard:v1 .
docker run --rm -p 8080:8080 taskboard:v1
```
Visit `http://localhost:8080`. For a real multi-node cluster, push the versioned image to an accessible registry and update `k8s/deployment.yaml` to reference that image, removing the ConfigMap source volume and Python command override. Do **not** assume a Docker image built on the control-plane host is visible on every Kubernetes node. The included ConfigMap-based sandbox workflow avoids that problem entirely.

## 15. Moving to real GKE later
You can reuse the source, Dockerfile, Service and many Deployment concepts. For actual GKE: set up a billing-enabled Google Cloud project, enable GKE and Artifact Registry APIs, build/push an image, create a GKE cluster, configure kubectl credentials, deploy a modified manifest referencing the pushed image, expose via appropriate Service/Ingress, test, and clean up all billable resources. **GKE is not guaranteed free.** Never run the sandbox ConfigMap-source method as a production deployment.

## 16. Teammate hand-off checklist
Send ZIP and this README. Teammate should be able to: inspect code; run tests; start Kubernetes sandbox; upload/unzip; execute `bash scripts/deploy.sh`; verify Pod and Service; test API; open preview if supported; inspect logs; scale and recover; update and clean up. If their objective requires a **real GKE-specific** demonstration, this Kubernetes sandbox cannot validate GKE-specific infrastructure.
