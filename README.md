# YugabyteDB (YSQL) Cache Demo App

This is a demo Spring Boot application using YugabyteDB (YSQL/Postgres) as an arbitrary JSON "cache".

The exposed REST API is primarily for testing, as it would not be expected that the actual caching layer would require
using REST. The actual logic could be easily embedded within the application itself, particularly if it was already
using YugabyteDB for other structured data.

As a demo, this application implements a basic pattern of JDBC read/write using a caching key, time-to-live (TTL), and
any arbitrary JSON value. While the schema itself is very simple, the use of JSONB allows for optimal storage. As a
typical cache may not require persistent storage, this implementation uses an `expires_at` timestamp to simulate cache
expiration (and its eventual purge).

For a fast read and write path, it is anticipated that a "near-by" YugabyteDB cluster be deployed - this could even be
deployed within the k8s cluster itself to reduce network latency. If the cache needs to survive a full region failure,
using asynchronous xCluster replication would be possible.

With the current configuration of GKE PODs connecting to YugabyteDB (outside GKE), the cache read p95s are < 2ms, cache
inserts p95s < 3ms, and read with update p95 < 5ms. If the applications performance budget needs less than that, there
would be some improvements by deploying YugabyteDB directly within the GKE cluster, but beyond that, another caching
implementation might be needed.

## Build the Container Image

```shell
$ ./gradlew clean build bootBuildImage
```

## Push the Container Image to DockerHub

Authenticate with DockerHub and upload the image:

```shell
$ docker push docker.io/<id>/yb-cache-app:latest
```

This will be the container image to use. Update the `cache-app-deployment.yml` file with the correct path
to uploaded image (i.e. don't use mine).

## Create a GKE Autopilot Cluster

TODO. This is pretty basic through the UI and get the `gloud` command to run.

### GKE Tips

- Pick the same region/zones as the database nodes.
- For better security, use a private cluster.
- Select `Enable control plane authorized networks` and add your personal IP address(es).
- The YugabyteDB VPC may need an ingress rule for the IP range of the provisioned GKE cluster.
  To locate the IP address CIDR, go to the cluster configuration and find `Pod IPv4 address range`.
  Add this to a firewall rule allowing ingress from these IPs.
- Don't forget any required Labels!

### Set up Local `kubectl` Credentials

```shell
gcloud container clusters get-credentials <cluster_name> --region <region> --project <project>
```

## Create Database Secrets

Provide your YugabyteDB credentials:

```shell
kubectl create secret generic ysql-db-secrets --from-literal=ysql-app.db.username=yugabyte --from-literal=yslq-app.db.password="<password>"
```

## Create ConfigMap (east1)

Update the config map with the IP addresses of the bootstrap nodes and the topology keys for the desired cluster. This
example config allows for overriding most `application.yml` settings for ease in testing.

```shell
kubectl apply -f k8s/cache-app-config-east1.yml
```

## Create Deployment (east1)

```shell
kubectl apply -f k8s/cache-app-deployment.yml
```

## Initial Application Testing

Find the IP address assigned to the deployment.

Look under `Exposing services` for the LoadBalancer. This is the external IP that can be used to test the deployment
from outside the PODs.

Example:

```shell
http <IP>/api/cache/20467137-43b2-4a70-a495-6965c37bc804
```

The database won't have any records at first, so this will likely 404.

## Initialize the Database

TODO

## Set up Locust Load Tests

TODO research this: https://abdelrhmanhamouda.github.io/locust-k8s-operator/

The `locustfile.py` needs to be deployed as a ConfigMap called `scripts-cm`:

```shell
kubectl create configmap scripts-cm --from-file=k8s/locust/locustfile.py
```

If you need to modify the script, to redeploy it without having to delete and recreate the ConfigMap use the `dry-run`
and `replace` option:

```shell
k create configmap scripts-cm --from-file=k8s/locust/locustfile.py -o yaml --dry-run=client | kubectl replace -f -
```

This ConfigMap contains the actual scripts to run. Any changes will require a full redeploy of the
map and the Locust worker nodes: `kubectl rollout restart deployment locust-worker`.

```shell
kubectl apply -f k8s/locust/locust-deploy.yml
```

### Port Forward

```shell
kubectl port-forward locust-master-<id> 8089:8089
```

Then navigate to http://localhost:8089 and use the Locust UI to start the load tests. It is highly recommended to watch
the number of workers deployed as they will become the primary limiting factor to throughput. Also, as long as the
YugabyteDB cluster is under 80% utilization, use the GKE settings to scale both number of workers and the number of
application PODs for higher RPS.

## Known Issues

- The LB configured for the `locust-master` is not working, the requests just time out (this used to work fine).
  For now, this is why the special `port-forward` is being done.
- The worker nodes are being flaky (i.e. the sometimes just stop) - this may be an autopilot issue.