Let's create a build pipeline for kubecoin
(That's the code of dockercoin that run a kubernetes)

The kubecoin project has been spleet in 4 parts:

* hasher
* rng
* webui
* worker

## Preparation: deploy tooling in kubernetes

### Step 1

Retrieve the Ip of one of node of your cluster. This is cluster dependent,
and there is no magical way to know this. On minikube you can use `minikube ip`,
if you're following a training, ask the trainers on how to get this value.
This will be referenced in the rest of the tutorial by `$INGRESS_IP`.
You will be asked for the first `make` command you tiped.

On minikube make sure that the `ingress` and `storage-provisioner` are enable (the default)
If your on a bare cluster you can install them via:

```shell
$ cd resources
resources $ make ingress
resources $ make local-path-provisionner
```

### Step 2

Install gitlab via

```shell
resources $ make gitlab                   # Default password will be displayed at the end
resources $ kubectl -n gitlab get pods -w # Wait for installation to finish
```
Go on https://gitlab.$INGRESS_IP.nip.io, and setup the gitlab as you wish (change default password, add
a ssh key)


### Step 3

Create an empty project (with no README or else) and add an origin that point the repository in gitlab
```
git origin add gitlab ssh://gitlab.$INGRESS_IP.nip.io:2222/root/kubecoin
```

### Note:

minikube users might want to edit the 'kube-system/tcp-services' to enable ssh port forwarding:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: tcp-services
  namespace: kube-system
data:
  '2222': 'gitlab/gitlab-gitlab-shell:22'
```

## Exercice 1: Build dockerfiles and push to a registry

Use gitlab CI to build the dockerfile automatically.
Everything is located in the `.gitlab-ci.yml` the on the top-level directory of
the repository. We have 4 images to build (`hasher`, `rng`, `webui`, `worker`)
and to push to the gitlab built-in docker registry.

### Notes:

  - Useful link: https://docs.gitlab.com/ce/ci/docker/using_docker_build.html
  - values associated with gitlab deployement are located in `resources/values/gitlab.yaml`
      Use `make gitlab` in the `resources` directory to deploy changes
  - there is some find some yaml specialities used in `.gitlab-ci.yaml` (`<<` operator):
    those are supported by the gitlab parser, not by Kubernetes, so don't try to use it in kubernetes manifests.


## Exercice 2: Use kaniko to build previous images

Same as the previous exercice, but don't use priviledge container to build docker image.
That's a good point for security !

 - kaniko documentation: https://github.com/GoogleContainerTools/kaniko
 - kaniko with gitlab integration: https://docs.gitlab.com/ce/ci/docker/using_kaniko.html

## Exercice 3: Deploy a per-commit test sandbox

Use the gitlab CI pipeline to deploy an environment per commit.
Try scaling the various component of the app ! Remember we want to get richer and richer !

### Notes:

  - To get a yaml representing a docker-registry secret, run the following command,
    ```
    kubectl create secret --dry-run -o yaml docker-registry regcreds --docker-server=registry.$INGRESS_IP.nip.io --docker-username=foo --docker-password=bar
    ```
  - A kubeconfig to access the cluster is located on the master node in: `/etc/kubernetes/admin.conf`

## Exercice 4: Deploy prometheus to analyse scalign problem

Install prometheus and grafana

```shell
resources $ make prometheus
resources $ make grafana
```

Then you will be able to edit `hasher` and `rng` to create prometheus endpoints.
Finally try to analyse the scaling problem.

## Exercice 5: Deploy Jaeger and use tracing

Install jaeger:

```shell
resources $ make jaeger
```

Integrate worker python code with opentelemetry (tracing framework, compatible with jaeger) and enable tracing:

  - opentelemetry python sample: https://opentelemetry.io/docs/python/tracing/
  - opentelemetry python repository: https://github.com/open-telemetry/opentelemetry-python
  - opentelemetry python documentation: https://open-telemetry.github.io/opentelemetry-python/
