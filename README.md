# hpa-scaler

This tool adjusts the minimum number of containers in a horizontal pod autoscaler object in Kubernetes, based on previous data gathered in Prometheus.

In order to handle traffic drops in an environment with fluctuating but recurrent load, the minimum number of containers can be modified dynamically, to track historical usage of previous hours/days/weeks.

## Running the tool

**⚠️ This is completely untested code and should not be used for anything that you care about**

The tool is intended to be run as a CronJob within the Kubernetes cluster containing the HPA/deployment to modify.

The tool assumes pre-existing data in Prometheus, in the format generated by [kube-state-metrics](https://github.com/kubernetes/kube-state-metrics).

Required environment variables :
- `PROM_URL` : URL to prometheus server. Required
- `NAMESPACE` : namespace of the deployment/hpa to update. Required
- `DEPLOYMENT` : namespace of the deployment which metrics we will use. Required
- `HPA_FLOOR` : Absolute minimum number of containers. Defaults to 2
- `COMPARISON_POINTS` : Comma-separated list of offsets for the prometheus query. Defaults to `1d,7d` (get data from 1 day ago and 7 days ago)
- `BUFFER` : Modifier on the gathered data to apply to new minimum number of containers. Defaults to `-.2` (new number of containers will be 20% lower than what was found in Prometheus)
