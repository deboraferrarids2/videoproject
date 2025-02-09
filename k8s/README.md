# Kubernetes Deployment

## Introdução

Este diretório contém os arquivos necessários para a implantação da aplicação no Kubernetes. A configuração inclui deployment do aplicativo, worker, Redis, PostgreSQL e escalonamento automático (HPA).


## Como rodar
minikube start
kubectl config use-context minikube
kubectl apply -f k8s/

kubectl get pods
kubectl get services
