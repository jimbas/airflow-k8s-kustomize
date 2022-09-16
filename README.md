# Deploy Airflow with K8s Kustomize

## Original Repo

[Airflow Kube](https://github.com/houstonj1/airflow-kube)

## Requirements
1. Active GCP console
2. ...

## Initialize Environment Variables
  ```
  export GCP_PROJECT_ID='your-google-cloud-project-id'
  export GCP_K8S_REGION='your-k8s-cluster-region. example: asia-southeast1'
  export DOCKER_REPO_NAME='your-docker-repo-name. example: airflow-repo'
  export DOCKER_REPO_TAG='your-docker-repo-tag. example: airflow:latest'
  ```
## Docker Build & Push
   ```
   gcloud artifacts repositories create $DOCKER_REPO_NAME --repository-format=docker --location=$GCP_K8S_REGION --description="Airflow Latest"
   docker build -t $GCP_K8S_REGION-docker.pkg.dev/$GCP_PROJECT_ID/$DOCKER_REPO_NAME/$DOCKER_REPO_TAG .
   docker run --rm -p 8080:8080 $GCP_K8S_REGION-docker.pkg.dev/$GCP_PROJECT_ID/$DOCKER_REPO_NAME/$DOCKER_REPO_TAG
   gcloud auth configure-docker $GCP_K8S_REGION-docker.pkg.dev
   docker push $GCP_K8S_REGION-docker.pkg.dev/$GCP_PROJECT_ID/$DOCKER_REPO_NAME/$DOCKER_REPO_TAG
   ```

## Install PostgreSQL
   ```
   helm repo add bitnami https://charts.bitnami.com/bitnami
   helm repo update
   helm install postgres bitnami/postgresql
   ```

## Initialize PostgreSQL Password Using K8s Secret
   ```
   kubectl port-forward --namespace default svc/postgres-postgresql 5432:5432 &
   export PGPASSWORD=$(kubectl get secret --namespace default postgres-postgresql -o jsonpath="{.data.postgres-password}" | base64 --decode)
   ```
   Verify the password with,
   ```
   echo $PGPASSWORD
   ```
   There's should be some random string shows up

## Initialize Airflow DB
   ```
   psql -h localhost -U postgres -f sql/init.sql
   ```

## Edit K8s Deployment YAML
   On each of deployment.yaml files in the k8s directory, the 'image' field should points to your docker artifact repo. You can use commands below to speed up modifying those files
   ```
   sed -i'' -e "s/_GCP_K8S_REGION_/$GCP_K8S_REGION/g" $(grep -rlI _GCP_K8S_REGION_ k8s)
   sed -i'' -e "s/_GCP_PROJECT_ID_/$GCP_PROJECT_ID/g" $(grep -rlI _GCP_PROJECT_ID_ k8s)
   sed -i'' -e "s/_DOCKER_REPO_NAME_/$DOCKER_REPO_NAME/g" $(grep -rlI _DOCKER_REPO_NAME_ k8s)
   sed -i'' -e "s/_DOCKER_REPO_TAG_/$DOCKER_REPO_TAG/g" $(grep -rlI _DOCKER_REPO_TAG_ k8s)
   ```

## Final Step: Deploying Airflow Kustomize
   ```
   kubectl apply -k k8s/
   ```

## Accessing Airflow Webserver
   The webserver pod takes a bit longer to be accessible. You can use this command to check,
   ```
   kubectl get all
   ```
   Check on pod's STATUS column, if it 'Running' then it is ready to browse.
   ```
   kubectl port-forward --namespace default svc/airflow-webserver 3000:80 &
   ```
   Open your favorite browser, visit http://localhost:3000. The username is admin & password is admin

## To Delete All
   ```
   kubectl delete -k k8s/
   helm delete postgres
   ```
