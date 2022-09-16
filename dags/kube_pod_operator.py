from datetime import timedelta

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.utils.dates import days_ago


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": days_ago(2),
    "email": ["airflow@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(seconds=15),
}

dag = DAG(
    "kube_pod_opereator",
    default_args=default_args,
    description="A DAG using K8s pod operator",
    schedule_interval=None,
    catchup=False,
)

hello_world = KubernetesPodOperator(
    task_id="hello-world",
    namespace="default",
    image="hello-world",
    name="hello-world",
    in_cluster=True,
    get_logs=True,
    log_events_on_failure=True,
    dag=dag,
)

python_version = KubernetesPodOperator(
    task_id="python-version",
    namespace="default",
    image="python:3.8-slim",
    cmds=["python", "--version"],
    name="python-version",
    in_cluster=True,
    get_logs=True,
    dag=dag,
)

node_version = KubernetesPodOperator(
    task_id="node-version",
    namespace="default",
    image="node:lts-alpine",
    cmds=["node", "--version"],
    name="node-version",
    in_cluster=True,
    get_logs=True,
    dag=dag,
)

go_version = KubernetesPodOperator(
    task_id="go-version",
    namespace="default",
    image="golang:alpine",
    cmds=["go", "version"],
    name="go-version",
    in_cluster=True,
    get_logs=True,
    dag=dag,
)

hello_world >> [python_version, node_version, go_version]
