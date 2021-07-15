# Batch Imaging Workflow

The `batch_imaging` workflow is a proof-of-concept of integrate a scientific
workflow with the SDP prototype. It simulates visibilities and images them using
RASCIL with Dask as an execution engine.

The workflow simulates SKA1-Low visibility data in a range of hour angles from
-30 to 30 degrees and adds phase errors. The visibilities are then calibrated
and imaged using the ICAL pipeline.

The workflow creates buffer reservations for storing the visibilities and
images.

## Parameters

The workflow parameters are:

* `n_workers`: number of Dask workers to deploy
* `freq_min`: minimum frequency (in hertz)
* `freq_max`: maximum frequency (in hertz)
* `nfreqwin`: number of frequency windows
* `ntimes`: number of time samples
* `rmax`: maximum distance of stations to include from array centre (in metres)
* `ra`: right ascension of the phase centre (in degrees)
* `dec`: declination of the phase centre (in degrees)
* `buffer_vis`: name of the buffer reservation to store visibilities
* `buffer_img`: name of the buffer reservation to store images

For example:

```json
{
  "n_workers": 4,
  "freq_min": 0.9e8,
  "freq_max": 1.1e8,
  "nfreqwin": 8,
  "ntimes": 5,
  "rmax": 750.0,
  "ra": 0.0,
  "dec": -30.0,
  "buffer_vis": "buff-pb-mvp01-20200523-00001-vis",
  "buffer_img": "buff-pb-mvp01-20200523-00001-img"
}
```

## Running the workflow using iTango

If using Minikube, make sure to increase the memory size (minimum 16 GB):

```console
minikube start --memory=16g
```

Once the [SDP is running](https://developer.skao.int/projects/ska-sdp-integration/en/latest/running/standalone.html), 
start an [iTango shell](https://developer.skao.int/projects/ska-sdp-integration/en/latest/running/standalone.html#accessing-the-tango-interface).

First, obtain a handle to a subarray device and turn it on:

```python
d = DeviceProxy('mid_sdp/elt/subarray_1')
d.On()
```

If you are not sure what devices are available, list them with `lsdev`.

Create a configuration string for the scheduling block instance. This contains
one real-time processing block, which uses the `test_realtime` workflow as a
placeholder, and one batch processing block containing the `batch_imaging`
workflow, which uses the example parameters from above:

```python
config_sbi = '''
{
  "id": "sbi-mvp01-20200523-00000",
  "max_length": 21600.0,
  "scan_types": [
    {
      "id": "science",
      "channels": [
        {"count": 8, "start": 0, "stride": 1, "freq_min": 0.9e8, "freq_max": 1.1e8, "link_map": [[0,0]]}
      ]
    }
  ],
  "processing_blocks": [
    {
      "id": "pb-mvp01-20200523-00000",
      "workflow": {"type": "realtime", "id": "test_realtime", "version": "0.2.2"},
      "parameters": {}
    },
    {
      "id": "pb-mvp01-20200523-00001",
      "workflow": {"type": "batch", "id": "batch_imaging", "version": "0.1.1"},
      "parameters": {
        "n_workers": 4,
        "freq_min": 0.9e8,
        "freq_max": 1.1e8,
        "nfreqwin": 8,
        "ntimes": 5,
        "rmax": 750.0,
        "ra": 0.0,
        "dec": -30.0,
        "buffer_vis": "buff-pb-mvp01-20200523-00001-vis",
        "buffer_img": "buff-pb-mvp01-20200523-00001-img"
      },
      "dependencies": [
        {"pb_id": "pb-mvp01-20200523-00000", "type": ["none"]}
      ]
    }
  ]
}
'''
```

Note that each workflow may come with multiple versions. Always use the latest number,
unless you know a specific version that suits your needs. (The Changelog
at the end of this page may help to decide.)

The scheduling block instance is created by the `AssignResources` command:

```python
d.AssignResources(config_sbi)
```

In order for the batch processing to start, you need to end the real-time processing 
with the `ReleaseResources` command:

```python
d.ReleaseResources()
```

You can watch the pods and persistent volume claims (for the buffer reservations)
being deployed with the following command or using [k9s](https://k9scli.io/):

```console
kubectl -w get pod,pvc -n sdp
```

At this stage you should see a pod called
`proc-pb-mvp01-20200523-00001-workflow-...` and the status is `RUNNING`. To see
the logs, run:

```console
kubectl logs <pod-name> -n sdp
```

and it should look like this:

```console
INFO:batch_imaging:Claimed processing block pb-mvp01-20200523-00001
INFO:batch_imaging:Waiting for resources to be available
INFO:batch_imaging:Resources are available
INFO:batch_imaging:Creating buffer reservations
INFO:batch_imaging:Deploying Dask EE
INFO:batch_imaging:Running simulation pipeline
INFO:batch_imaging:Running ICAL pipeline
...
```

## Accessing the data

The buffer reservations are realised as Kubernetes persistent volume claims.
They should have persistent volumes created to satisfy them automatically. The
name of the corresponding persistent volume is in the output of:

```console
kubectl get pvc -n sdp
```

The location of the persistent volume in the filesystem is shown in the output
of:

```console
kubectl describe pv <pv-name>
```

If you are running Kubernetes with Minikube in a VM, you need to log in to it
first to gain access to the files:

```console
minikube ssh
```

## Running the workflow using the SDP CLI

Deploy SDP and start the console as described at 
[Running SDP stand-alone](https://developer.skao.int/projects/ska-sdp-integration/en/latest/running/standalone.html).

You may also run this workflow directly from the console using the 
[`ska-sdp` CLI](https://developer.skao.int/projects/ska-sdp-config/en/latest/cli.html).

Run the workflow:

```console
ska-sdp create pb batch:batch_imaging:0.1.1
```

If you want to change the default parameters, you can run instead as follows (update the JSON string as needed):

```console
ska-sdp create pb batch:batch_imaging:0.1.1 '{"n_workers": 4, "freq_min": 0.9e8, "freq_max": 1.1e8}'
```

You can watch the pod being created as before either using 
```console
kubectl -w get pods -n sdp
```
or [k9s](https://k9scli.io/). To access the data created by the workflow, follow the steps above at 
"Accessing the data" in the "Running the workflow using iTango" section.

## Changelog

### 0.1.2

- use latest SDP configuration library