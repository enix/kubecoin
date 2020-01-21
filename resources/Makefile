INGRESS_CHART = stable/nginx-ingress
INGRESS_RELEASE = nginx-ingress
INGRESS_NAMESPACE = ingress
INGRESS_VERSION = 1.28.0

JETSTACK_HELM_REPO = ~/.cache/helm/repository/jetstack-index.yaml
CERTMANAGER_CHART = jetstack/cert-manager
CERTMANAGER_RELEASE = cert-manager
CERTMANAGER_NAMESPACE = $(INGRESS_NAMESPACE)
CERTMANAGER_VERSION = 0.12.0

GITLAB_HELM_REPO = ~/.cache/helm/repository/gitlab-index.yaml
GITLAB_CHART = ./gitlab
GITLAB_RELEASE = gitlab
GITLAB_NAMESPACE = gitlab
GITLAB_VERSION =

MONITORING_NAMESPACE = monitoring

PROMETHEUS_CHART = stable/prometheus
PROMETHEUS_RELEASE = prometheus
PROMETHEUS_NAMESPACE = $(MONITORING_NAMESPACE)
PROMETHEUS_VERSION = 10.0.1

GRAFANA_CHART = stable/grafana
GRAFANA_RELEASE = grafana
GRAFANA_NAMESPACE = $(MONITORING_NAMESPACE)
GRAFANA_VERSION = 4.3.0

ELASTIC_HELM_REPO = ~/.cache/helm/repository/elastic-index.yaml
ELASTICSEARCH_CHART = elastic/elasticsearch
ELASTICSEARCH_RELEASE = elasticsearch
ELASTICSEARCH_NAMESPACE = $(MONITORING_NAMESPACE)
ELASTICSEARCH_VERSION = 7.5.1

JAEGERTRACING_HELM_REPO = ~/.cache/helm/repository/jaegertracing-index.yaml
JAEGER_CHART = jaegertracing/jaeger
JAEGER_RELEASE = jaeger
JAEGER_NAMESPACE = $(MONITORING_NAMESPACE)
JAEGER_VERSION = 0.18.5

CA_DIR = ca

include custom.mk

.PHONY: gitlab
gitlab: $(GITLAB_HELM_REPO) namespace-$(GITLAB_NAMESPACE) ca-self-sign ingress cert-manager
	# Create self-sign cert in the gitlab namespace, gitlab-runner use the public endpoint
	kubectl -n $(GITLAB_NAMESPACE) create secret generic gitlab-ca-crt \
	--from-literal=gitlab.$(INGRESS_IP).nip.io.crt="$$(cat ${CA_DIR}/ca.crt)" \
	--dry-run -o yaml | kubectl apply -f -
	# Install gitlab
	@echo "#####  Installing gitlab, could take a while ...(be patient) ######"
	helm upgrade --install $(GITLAB_RELEASE) $(GITLAB_CHART) \
	--namespace $(GITLAB_NAMESPACE) $(if $(GITLAB_VERSION),--version=$(GITLAB_VERSION),) \
	--set global.hosts.domain=$(INGRESS_IP).nip.io \
	-f values/gitlab.yaml;
	# Install crt into docker conf
	kubectl apply -f manifests/docker-self-sign-ca-daemonset.yaml
	# Display password for gitlab
	@echo "The gitlab 'root' password is:"
	@kubectl get secret -n $(GITLAB_NAMESPACE) $(GITLAB_RELEASE)-gitlab-initial-root-password \
	-ojsonpath='{.data.password}' | base64 -d; echo

$(GITLAB_HELM_REPO):
	helm repo add gitlab https://charts.gitlab.io/
	helm repo update

.PHONY: ingress
ingress: namespace-$(INGRESS_NAMESPACE)
	helm upgrade --install $(INGRESS_RELEASE) $(INGRESS_CHART) \
	--namespace $(INGRESS_NAMESPACE) --version=$(INGRESS_VERSION) \
	--set tcp.2222=$(GITLAB_NAMESPACE)/$(GITLAB_RELEASE)-gitlab-shell:22 \
	-f values/nginx-ingress.yaml

ca-self-sign: cert-manager | $(CA_DIR)/ca.crt $(CA_DIR)/ca.key
	kubectl create secret tls -n $(CERTMANAGER_NAMESPACE) ca-self-sign --key=$(CA_DIR)/ca.key --cert=$(CA_DIR)/ca.crt \
	--dry-run -o yaml | kubectl apply -f -
	kubectl wait --timeout=60s --for=condition=Ready \
	-n $(CERTMANAGER_NAMESPACE) $$(kubectl -n $(CERTMANAGER_NAMESPACE) get pods -o name -l app=webhook)
	kubectl -n $(CERTMANAGER_NAMESPACE) apply -f manifests/ca-self-sign-clusterissuer.yaml

$(CA_DIR)/ca.crt: $(CA_DIR)/ca.key
	openssl req -subj '/CN=training' -new -x509 -days 365 -key $< -out $@

$(CA_DIR)/ca.key:
	mkdir -p $(CA_DIR)
	openssl genrsa -out $@ 2048

.PHONY: cert-manager
cert-manager: $(JETSTACK_HELM_REPO) namespace-$(CERTMANAGER_NAMESPACE)
	kubectl apply --validate=false -f https://raw.githubusercontent.com/jetstack/cert-manager/release-0.12/deploy/manifests/00-crds.yaml
	helm upgrade --install $(CERTMANAGER_RELEASE) $(CERTMANAGER_CHART) \
	--namespace $(CERTMANAGER_NAMESPACE) --version=$(CERTMANAGER_VERSION)

$(JETSTACK_HELM_REPO):
	helm repo add jetstack https://charts.jetstack.io
	helm repo update

local-path-provisioner:
	kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/master/deploy/local-path-storage.yaml

.PHONY: prometheus
prometheus: namespace-$(PROMETHEUS_NAMESPACE)
	helm upgrade --install $(PROMETHEUS_RELEASE) $(PROMETHEUS_CHART) \
	--namespace $(PROMETHEUS_NAMESPACE) --version=$(PROMETHEUS_VERSION)

.PHONY: grafana
grafana: namespace-$(GRAFANA_NAMESPACE) grafana-dashboard
	kubectl create secret generic grafana-admin -n ${GRAFANA_NAMESPACE} \
	--from-literal=admin-user=admin \
	--from-literal=admin-password=admin \
	--dry-run -o yaml | kubectl apply -f -
	helm upgrade --install $(GRAFANA_RELEASE) $(GRAFANA_CHART) \
	--namespace $(GRAFANA_NAMESPACE) --version=$(GRAFANA_VERSION) \
	-f values/grafana.yaml

.PHONY: grafana-dashboard
grafana-dashboard:
	kubectl apply -n ${GRAFANA_NAMESPACE} -f manifests/grafana-datasource.yaml

.PHONY: jaeger
jaeger: $(JAEGERTRACING_HELM_REPO) elasticsearch namespace-$(JAEGER_NAMESPACE)
	helm upgrade --install $(JAEGER_RELEASE) $(JAEGER_CHART) \
	--namespace $(JAEGER_NAMESPACE) --version=$(JAEGER_VERSION) \
	--set storage.elasticsearch.host=$(ELASTICSEARCH_RELEASE)-master.$(ELASTICSEARCH_NAMESPACE) \
	-f values/jaeger.yaml

.PHONY: elasticsearch
elasticsearch: $(ELASTIC_HELM_REPO) namespace-$(ELASTICSEARCH_NAMESPACE)
	helm upgrade --install $(ELASTICSEARCH_RELEASE) $(ELASTICSEARCH_CHART) \
	--namespace $(ELASTICSEARCH_NAMESPACE) --version=$(ELASTICSEARCH_VERSION)

$(JAEGERTRACING_HELM_REPO):
	helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
	helm repo update

$(ELASTIC_HELM_REPO):
	helm repo add elastic https://helm.elastic.co
	helm repo update

namespace-%:
	kubectl get namespace $* || kubectl create namespace $*

custom.mk:
	@if [ ! -f $@ ]; then \
	  echo -n "What is your ingress IP ?: "; read INGRESS_IP; \
	  echo "INGRESS_IP = $${INGRESS_IP}" > $@; \
	fi
