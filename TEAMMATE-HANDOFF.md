# Team hand-off: TaskBoard Kubernetes demo

**App:** TaskBoard, a Python standard-library web app with a browser UI and task CRUD API.
**Entry point:** `app/server.py`.
**Test suite:** `python3 -m unittest discover -s tests -v`.
**Sandbox deploy:** `bash scripts/deploy.sh` (from project root).
**Check:** `kubectl -n taskboard get pods,svc`.
**Expose temporarily:** `kubectl -n taskboard port-forward --address 0.0.0.0 service/taskboard 8080:80`.
**Test:** `curl http://127.0.0.1:8080/health` and `curl http://127.0.0.1:8080/api/tasks` in a second sandbox terminal.
**Delete:** `kubectl delete namespace taskboard`.

Important: Killercoda is Kubernetes, not managed GKE; sandbox hosting is temporary. Tasks are in-memory, not persistent or synchronized between replicas. Read README before scaling or changing code. The recommended sandbox deploy mounts code via ConfigMap, not a custom-built image. A Dockerfile is included for conventional image-building practice.
