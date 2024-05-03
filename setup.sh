export GKE_CLUSTER=cluster-1
echo $GKE_CLUSTER

export GKE_PROJECT=metal-air-419704
echo $GKE_PROJECT

export GKE_ZONE=us-central1-c
echo $GKE_ZONE

export SA_NAME=github-gke-cicd-sa
echo $SA_NAME

export ARTIFACT_REGISTRY=https://us-central1-docker.pkg.dev

gcloud container clusters create $GKE_CLUSTER --project=$GKE_PROJECT --zone=$GKE_ZONE        
