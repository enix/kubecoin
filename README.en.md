Let's create a build pipeline for *kubecoin*
(it's the code of DockerCoins, running in Kubernetes).

The kubecoin project is split in 4 parts:

* hasher
* rng
* webui
* worker

## Preparation: deploy tooling to kubernetes

### Step 0

Clone this repository:

```shell
cd ~
git clone https://github.com/enix/kubecoin
cd kubecoin
```

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
resources $ make gitlab
# The GitLab password will be shown at the end of the "make gitlab" command.
resources $ watch kubectl -n gitlab get pods
# Wait until all the pods have Running or Completed in the STATUS column.
# (This will take a few minutes.)
```

Now, we can open https://gitlab.$INGRESS_IP.nip.io/ in our browser, and setup GitLab as desired. The login is `root`, and the password is the (very long) password that was generated and displayed at the end of `make gitlab`. We can change the default password if we wish.

Add an SSH key. This is done by opening our profile settings: click on our
user menu in the top-right corner, select "Settings". Then in the menu
on the left, there will be "SSH keys". We need to add our *public key*
here. If you're using a training cluster, the SSH public key would be in
`~/.ssh/id_rsa.pub`. Copy-paste it, click "Add key".

### Step 3

Using GitLab's web UI, create an empty project. (To do that, click on
the GitLab logo in the top left corner, then select "Create project" in
the middle). Let's name the project `kubecoin`.

*Do not* tick the box "Initialize repository with a README", because we want
the repository to be completely empty, so that we can push to it directly.

The next step is to push our `kubecoin` repository to the one
that we just created on GitLab.

Let's add a git remote that points to GitLab:

```shell
git remote add gitlab ssh://git@gitlab.$INGRESS_IP.nip.io:2222/root/kubecoin
```

We can now push our local repository to GitLab:

```shell
git push gitlab full_pipeline
```

Back to the GitLab UI, in the left sidebar, if we click on "CI /CD"
then "Jobs", we will see the status of our pipeline. The "Build" phase
will take a few minutes the first time, then the "Test" phase will
fail, because we need to make some additional configuration
(more about that in a moment).

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

The GitLab pipeline is described
in the `.gitlab-ci.yml` the on the top-level directory of
the repository. We have 4 images to build (`hasher`, `rng`, `webui`, `worker`)
and to push to the GitLab built-in Docker registry.

The "Test" phase of the pipeline fails because it needs a couple of
environment variables: `KUBECONFIG` and `REGCREDS`.

To set environment variables in GitLab, select "Settings" → "CI/CD"
in the left sidebar. There will be a variables section. We need
our variables to be of type "File", which means that GitLab
will create a file with the data that we provide, and will set
the environment variable to the path to that file.

For `KUBECONFIG`, we can use our Kubernetes configuration file,
located in `~/.kube/config`. Set it, try to run the pipeline again;
now it should fail at the `REGCREDS` phase.

To specify registry credentials, we need to create these credentials,
then pass them to GitLab.

To create the credentials, select "Settings" → "Repository" in
the left sidebar. Expand the "Deploy tokens" section, input a
name, tick the "read_registry" checkbox, and create the token.
Save the user and password that are displayed.

To use these credentials, we need to pass them to the GitLab
CI job. This is done by generating the YAML corresponding
to a Secret of type `docker-registry`, and passing that YAML
as a File variable (like we did for `KUBECONFIG`).

To generate the YAML representing a docker-registry secret, we can run the following command:

```shell
kubectl create secret docker-registry regcreds \
        --docker-server=registry.$INGRESS_IP.nip.io \
        --docker-username=foo --docker-password=bar \
        -o yaml --dry-run
```

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
