# K8S
minikube start
kubectl config use-context minikube
kubectl apply -f k8s/

kubectl get pods
kubectl get services




kubectl get hpa
ab -n 10000 -c 100 http://192.168.130.2:31681/
kubectl get hpa -w
kubectl get pods -w
kubectl top pods