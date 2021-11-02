import logging
import math
import os
import requests
import sys
import time
import urllib.parse
from kubernetes import client, config

def get_replicas_from_prometheus(url, namespace, deployment, offset):
    current_time = int(time.time())
    query = f'kube_deployment_status_replicas{{deployment=~"^{deployment}$",namespace=~"^{namespace}$"}} offset {offset}'
    encoded_query = urllib.parse.quote_plus(query)
    try:
        json_data = requests.get(f'{url}/api/v1/query?query={encoded_query}&time={current_time}').json()
    except:
        logging.exception("Issue querying Prometheus data")
        return -1
    try:
        replicas = int(json_data['data']['result'][0]['value'][1])
    except:
        logging.warning(f"Missing or invalid data for deploy {deployment} in ns {namespace} for offset {offset}")
        return -1
    return replicas

def update_hpa(namespace, deployment, target):
    hpas = client.AutoscalingV1Api().list_namespaced_horizontal_pod_autoscaler(namespace)
    for hpa in hpas.items:
        if hpa.spec.scale_target_ref.name == deployment:
            break
    hpa.spec.min_replicas = target
    logging.info(f"Updating hpa {hpa.spec.name} in {namespace} with new minimum of {target} pods")
    client.AutoscalingV1Api().patch_namespaced_horizontal_pod_autoscaler(hpa.metadata.name, namespace, hpa)


# Kubernetes setup
config.load_incluster_config()
# Env var gathering
prometheus_url = os.environ['PROM_URL']
namespace = os.environ['NAMESPACE']
deployment = os.environ['DEPLOYMENT']
hpa_floor = int(os.environ.get('HPA_FLOOR', 2))
offsets = os.environ.get('COMPARISON_POINTS', '1d,7d').split(',')
buffer = float(os.environ.get('BUFFER', '-.2'))

targets = []
for offset in offsets:
    replicas = get_replicas_from_prometheus(prometheus_url, namespace, deployment, offset)
    if replicas > 0:
        targets.append(math.ceil(replicas * (1 + buffer)))

if targets:
    targets.append(hpa_floor)
    update_hpa(namespace, deployment, max(targets))
else:
    logging.error("No data point found, skipping update")
    sys.exit(1)
