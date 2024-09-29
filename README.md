# Exercise: Money Makes The World Go Round?

Money makes the world go round OR is it the root of all evil?  Although we will not be solving that particular question, we WILL be creating a simple currency exchange API that will be deployed on a local Kubernetes cluster.

## The Project

We primarily develop in Python / Go / Java, but for this exercise you may use any language you are comfortable with.

1. Create a simple service API that returns the current (latest) currency conversion rate when provided with two currencies.  For example, when provided Euro and US Dollar currency return the current value in US Dollars for 1 Euro.  The data should be returned in a manner so that it can be easily consumed by the service making the call.  You will be leveraging this [public currency exchange API](https://github.com/fawazahmed0/currency-api#readme) for the exercise.  It is a public API - no auth or api key is required for access.
2. Deploy/Test in a local kubernetes cluster using Deployment / Service.  We have provided some sample manifests in the [k8s directory](/k8s) in this repo to get you started.
3. Please feel free to include some documentation (or anything else you deem important) in the final submission.
4. This project repo will likely be distributed as a tar file, so just untar it locally and `git init` it so you can develop with a local git repo.  When you are done, please tar up the project (including the `.git` directory) and send back to us.

## Tools

This exercise assumes you have docker already installed locally.  If you do not, please install per https://docs.docker.com/get-docker/ or https://docs.docker.com/engine/install/ (for the CLI only versions).

To complete the exercise you will need a local Kubernetes cluster installed.  We have included instructions on setting up a local cluster using [KIND - K8s in docker](https://kind.sigs.k8s.io/) in the section below.   However, if you already have a local cluster set up (e.g. Rancher Desktop, Docker Desktop, minikube, k3s) and can deploy/test locally built images with the it feel free to use it instead.

This exercise has been developed and tested to work on MacOS or Linux.  Please use one of these operating systems for this exercise.  If you are running on another platform you can use optionally use a Linux VM.  This may work on Windows using Docker Desktop for Windows, but that configuration is untested.

## Local K8s Cluster Setup (KIND)

The following instructions will setup a local one node k8s cluster for use in this exercise.  We will be using [KIND - K8s in docker](https://kind.sigs.k8s.io/) and also creating a local docker registry that the KIND cluster has access to and you can push your application images to.

1. Install KIND using these [instructions](https://kind.sigs.k8s.io/docs/user/quick-start/#installation).  On MacOS, the easiest method is using homebrew `brew install kind`.  On Linux (or Linux VM), you can install using the [release binaries](https://kind.sigs.k8s.io/docs/user/quick-start/#installing-from-release-binaries).  Note that if you are on an M1 Mac (ARM arch) but want to perform this exercise in a Linux VM you will need the `arm64` linux binary.

2. Install `kubectl` if you do not have it already installed - [instructions here](https://kubernetes.io/docs/tasks/tools/).  On MacOS, the easiest method is to use homebrew `brew install kubectl`.

3. Setup KIND local cluster and registry
```
   # If your docker install is setup like this: https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user run this:
   make create-cluster

   # If for example you execute docker as `sudo docker ...`, run this:
   make create-cluster-sudo

```
4. Test cluster
```
   make test-cluster
```
Should return something like the below:
```
Kubernetes control plane is running at https://127.0.0.1:36063
CoreDNS is running at https://127.0.0.1:36063/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
NAME                 STATUS   ROLES           AGE   VERSION
kind-control-plane   Ready    control-plane   28m   v1.24.0
```

5. When KIND creates the cluster it should append to your current `~/.kube/config` (if it exists) or create a new one.  If you run as `make create-cluster-sudo` (e.g. your docker setup is not setup as a non root user), it will copy the config to `~/.kube` as `~/.kube/kind-config` and then append to your `$KUBECONFIG` in your current session.  If at any time you run into a problem with the kubeconfig, you can generate it yourself via `sudo kind get kubeconfig > ~/.kube/kind-kubeconfig` and then manually append it to your `$KUBECONFIG` like this `export KUBECONFIG=$KUBECONFIG:~/.kube/kind-kubeconfig`.

## Important info about local images / local registry using KIND

There are some specific workflows to be aware of in order to deploy your containerized application on the local cluster. In order to use the image in the cluster you will need to build and push your image to the local registry created.

For example: build/tag it `docker build -t localhost:5001/image:tag .` and then push it to the registry `docker push localhost:5001/image:foo`.  You can then reference it in the cluster as `localhost:5001/image:tag` since the local cluster will have access to the registry.  For more information see the [documentation](https://kind.sigs.k8s.io/docs/user/local-registry/)

## Cleanup

If you installed the local KIND cluster you can cleanup / delete it with `kind cluster delete kind` or use the included [Makefile](/Makefile)
