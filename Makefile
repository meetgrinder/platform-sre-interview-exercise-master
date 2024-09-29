# Makefile for local use - feel free to add other targets/deps if you need them for your development

# KIND cluster setup - creates the KIND cluster and local docker registry for use in this exercise
# https://kind.sigs.k8s.io/docs/user/quick-start/ ; https://kind.sigs.k8s.io/docs/user/local-registry/
# requires docker install as a prereq
create-cluster:
	@cd scripts; ./create-kind-cluster-registry.sh

# use if you have not done this: https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user
create-cluster-sudo:
	@cd scripts; sudo ./create-kind-cluster-registry.sh

test-cluster:
	kubectl cluster-info;kubectl get nodes

remove-cluster:
	kind cluster delete kind

remove-cluster-sudo:
	sudo kind cluster delete kind
