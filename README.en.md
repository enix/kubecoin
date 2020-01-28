Let's create a build pipeline for *kubecoin*
(it's the code of DockerCoins, running in Kubernetes).

The kubecoin project is split in 4 parts:

* hasher
* rng
* webui
* worker

## Preparation: deploy tooling to kubernetes

### Step 1

We need to retrieve the IP address of one of the nodes of our cluster. This is cluster dependent,
and there is no magical way to do this. On minikube we can use `minikube ip`.
If you're attending a training, ask the trainers how to obtain this value.
In the rest of the tutorial, we will refer to this address by `$INGRESS_IP`.
The first `make` command that we will run (see below) will ask us for that IP address.

We need an *ingress controller* and a *dynamic storage provisioner*.

**If we're using minikube,** we need to make sure that the addons `storage-provisioner` and `ingress` are enabled. The former is enabled by default. The latter can be enabled by running:

```shell
minikube addons enable ingress
```

**If we're using a bare cluster,** we can install an ingress controller
and a storage provisioner with the following commands:

```shell
$ cd resources
resources $ make ingress
resources $ make local-path-provisionner
```

### Step 2

Once we have the required components, we can install GitLab.
The following commands will take care of everything for us:

```shell
resources $ make gitlab                   # Default password will be displayed at the end
resources $ kubectl -n gitlab get pods -w # Wait for installation to finish
```

Now, we can open https://gitlab.$INGRESS_IP.nip.io/ in our browser, and setup GitLab as desired. We should change the default password, and add an SSH key.

### Step 3

Let's create an empty project (with no README or anything else), and add a remote that points to GitLab:

```shell
git remote add origin gitlab ssh://gitlab.$INGRESS_IP.nip.io:2222/root/kubecoin
```

### Step 4 (optional)

minikube users might want to edit the ConfigMap `tcp-services` in namespace `kube-system` to enable SSH port forwarding:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: tcp-services
  namespace: kube-system
data:
  '2222': 'gitlab/gitlab-gitlab-shell:22'
```

## Exercise 1: Build dockerfiles and push to a registry

Use GitLab CI to build the Dockerfile automatically.

Everything is located in the `.gitlab-ci.yml` the on the top-level directory of
the repository. We have 4 images to build (`hasher`, `rng`, `webui`, `worker`)
and to push to the GitLab built-in Docker registry.

### Notes

- This documentation has a lot of helpful information: https://docs.gitlab.com/ce/ci/docker/using_docker_build.html.
- Values associated with gitlab deployement are located in `resources/values/gitlab.yaml`.
- Use `make gitlab` in the `resources` directory to deploy changes.
- The `.gitlab-ci.yaml` file is using some custom extensions, like the `<<` operator; those are supported by the gitlab parser, not by Kubernetes, so don't try to use it in kubernetes manifests.

## Exercice 2: Use kaniko to build the images

In the previous exercise, we used privileged containers to build
the Docker image. To improve security, we are going to use Kaniko instead.
Kaniko can build Docker images without requiring special permissions.

- Kaniko documentation: https://github.com/GoogleContainerTools/kaniko
- Kaniko with GitLab integration: https://docs.gitlab.com/ce/ci/docker/using_kaniko.html

## Exercise 3: Deploy a per-commit test sandbox

Use the GitLab CI pipeline to deploy an environment per commit.
Try scaling the various component of the app! (Remember, we want to get richer and richer! More DockerCoins!)

### Notes

To use an image from a private registry (that requires authentication),
we need to create a Secret of type `docker-registry`.

To generate the YAML representing a docker-registry secret, we can run the following command:

```shell
kubectl create secret --dry-run -o yaml docker-registry regcreds \
        --docker-server=registry.$INGRESS_IP.nip.io \
        --docker-username=foo --docker-password=bar
```

We can find a `kubeconfig` file to access the cluster on the master node, in `/etc/kubernetes/admin.conf`.

## Exercice 4: Deploy prometheus to analyze scaling problem

Install prometheus and grafana:

```shell
resources $ make protheus
resources $ make grafana
```

Then edit `hasher` and `rng` to create prometheus endpoints.

Finally, try to analyze the scaling problem.

## Exercice 5: Deploy Jaeger and use tracing

Install jaeger:

```shell
resources $ make jaeger
```

Integrate worker python code with opentelemetry (tracing framework, compatible with jaeger) and enable tracing:

- opentelemetry python sample: https://opentelemetry.io/docs/python/tracing/
- opentelemetry python repository: https://github.com/open-telemetry/opentelemetry-python
- opentelemetry python documentation: https://open-telemetry.github.io/opentelemetry-python/
