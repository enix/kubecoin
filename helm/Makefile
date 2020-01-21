
NAMESPACE = kubecoin
RELEASE = kubecoin
CHART = ./kubecoin

-include custom.mk
-include ../resources/custom.mk

REGISTRY ?= registry.$(INGRESS_IP).nip.io/root/kubecoin

kubecoin: namespace-$(NAMESPACE)
	helm upgrade --install $(RELEASE) $(CHART) \
	--namespace=$(NAMESPACE) \
	-f values.yaml \
	--set global.registry=registry.$(INGRESS_IP).nip.io \
	$(if $(INGRESS_IP),--set ingress.host=kubecoin.$(INGRESS_IP).nip.io,) \
	$(if $(VERSION),--set global.tag=$(VERSION),)

registry-creds: namespace-$(NAMESPACE)
	@echo -n "docker-registry: "; \
	read DOCKER_REGISTRY; \
	echo -n "docker-username: "; \
	read DOCKER_USERNAME; \
	echo -n "docker-password: "; \
	read DOCKER_PASSWORD; \
	set +x; \
	kubectl create secret -n $(NAMESPACE) docker-registry regcreds \
	--docker-server=$${DOCKER_REGISTRY} \
	--docker-username=$${DOCKER_USERNAME} \
       	--docker-password=$${DOCKER_PASSWORD} \
	--docker-email=""

namespace-%:
	kubectl get namespace $* || kubectl create namespace $*
