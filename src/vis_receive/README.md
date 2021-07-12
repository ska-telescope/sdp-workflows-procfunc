# Visibility Receive Workflow

This is the integration of the CBF-SDP interface emulation and receive workflow.
This workflow deploys and updates the receive addresses attribute with DNS-based IP address.

## Deploying the Receive Workflow in the SDP Prototype

To set up SDP on your local machine using Minikube, follow the instructions at 
[Running SDP stand-alone](https://developer.skao.int/projects/ska-sdp-integration/en/latest/running/standalone.html).

### Configuring the Workflow

Although this repository contains example workflows - the helm-charts specific to deployment of the SDP prototype are
stored in another repository (https://gitlab.com/ska-telescope/sdp/ska-sdp-helmdeploy-charts). For the purposes of continuity
we will document the use of the chart here. The documentation may be replicated in other repositories.

The important consideration for the current version of the emulator and receive workflow is that the interface Telescope Model is
via the measurement set. As the charts need to be agnostic about where and how they are deployed it was necessary to provide a
schema whereby the data-model could be accessed by the deployment. What we do here is we provide a mechanism by which the model
can be pulled by providing a URL to a compressed tarfile of the model measurement set, and the name of that measurement set
once unzipped. This should be the same as the measurement set that will be transmitted by the emulator to allow the UVW and
timestamps to match.

There are few setups we need to do before running the workflow. First need to download the `sim-vis.ms.tar.gz` from the
[CBF-SDP Emulator Repository](https://gitlab.com/ska-telescope/cbf-sdp-emulator/-/tree/master/data).

Extract the file:

    > tar -xf sim-vis.ms.tar 

Need to create a persistent volume, to do that create a file called `pvc.yaml` and add the following:

    kind: PersistentVolume
    apiVersion: v1
    metadata:
      name: pv-local
      labels:
        type: local
    spec:
      storageClassName: local
      capacity:
        storage: 5Gi
      accessModes:
        - ReadWriteOnce
      hostPath:
        path: "<path to sim-vis.ms"
    ---
    apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
      name: local-pvc
    spec:
      storageClassName: local
      accessModes:
      - ReadWriteOnce
      resources:
        requests:
          storage: 5Gi
      selector:
        matchLabels:
          type: local


Make sure to update the hostPath.

Create persistent volume by executing the following command:

    > kubectl create -f pvc.yaml -n sdp

The configuration of the receive workflow is managed via adding to the configuration of the processing block.
The processing block (PB) can only be created using the iTango interface. This is a realtime workflow, therefore 
it is linked to a Scheduling Block Instance (SBI). Currently, there is no option to create a PB and link
it to SBI using the `ska-sdp` utility. 

To run the workflow using iTango interface, follow the instructions at 
[Running SDP stand-alone](https://developer.skao.int/projects/ska-sdp-integration/en/latest/running/standalone.html).

Use the following configuration string. This contains one real-time processing block, 
which uses the `vis_receive` workflow, and one batch processing block the `test_batch` as a placeholder
workflow:

```python
config_sbi = '''
{
  "interface": "https://schema.skao.int/ska-sdp-assignres/0.2",
  "id": "sbi-mvp01-20200619-00000",
  "max_length": 21600.0,
  "scan_types": [
    {
      "id": "science_A",
      "coordinate_system": "ICRS", "ra": "02:42:40.771", "dec": "-00:00:47.84",
      "channels": [
        { "count": 5, "start": 0, "stride": 2, "freq_min": 0.35e9, "freq_max": 0.368e9, "link_map": [[0,0], [200,1], [744,2], [944,3]] }
      ]
    },
    {
      "id": "calibration_B",
      "coordinate_system": "ICRS", "ra": "12:29:06.699", "dec": "02:03:08.598",
      "channels": [
        { "count": 5, "start": 0, "stride": 2, "freq_min": 0.35e9, "freq_max": 0.368e9, "link_map": [[0,0], [200,1], [744,2], [944,3]] }
      ]
    }
  ],
  "processing_blocks": [
    {
      "id": "pb-mvp01-20200619-00000",
      "workflow": {"type": "realtime", "id": "vis_receive", "version": "0.3.3"},
      "parameters": {}
    },
    {
      "id": "pb-mvp01-20200619-00001",
      "workflow": {"type": "batch", "id": "test_batch", "version": "0.2.4"},
      "parameters": {},
      "dependencies": [
        {"pb_id": "pb-mvp01-20200619-00001", "type": ["visibilities"]}
      ]
    }
  ]
}'''
```

Note that each workflow may come with multiple versions. Always use the latest number,
unless you know a specific version that suits your needs, or you follow the example above. (The Changelog
at the end of this page may help to decide.)

This will start up a default deployment. It will launch a receiver pod.  All the options supported by the receiver are 
supported by the chart deployment. The defaults set by the workflow currently are:

    "image": "nexus.engageska-portugal.pt/ska-docker/cbf_sdp_emulator",
    "version": "latest",
    "recv_emu": "emu-recv",
    "model.name": "sim-vis.ms",
    "transmission.channels_per_stream": 4,
    "transmission.rate": "147500",
    "payload.method": "icd",
    "reader.num_timestamps": 0,
    "reader.start_chan": 0,
    "reader.num_chan": 0,
    "reader.num_repeats": 1,
    "results.push": False,
    "pvc.name": "local-pvc",
    "pvc.path": "/mnt/data",
    "reception.outputfilename": "output.ms",
    "reception.receiver_port_start": "41000",
    "reception.num_ports": 1,

To add additional parameters or to override default parameters, can be done by adding to the `parameters` key of the PB
via the configuration string.

Once the pod is deployed with the desired configuration, the receive will be running as a server inside a pod and waiting for
packets from the emulator (or even the actual CBF).

Following functionality are not available with the generic `receive` chart. Would need to update workflow to use the 
`cbf-sdp-emulator` chart. This is can be done by updating the `deploy_name`

### Retrieving Data from Kubernetes Deployments

If the receive workflow is configured to generate a measurement set, then it needs to be exported from the Kubernetes environment.
The mechanism we have provided for this is mediated by the ``rclone`` package `https://rclone.org`. In order for this to
work in a secure manner we have provided a mechanism by which a container can pull an rclone configuration file - containing the
credentials and configured end points. This configuration is then used by a container to push the results out. There are only two configuration
options required:

    - ``rclone.configurl``. This is a URL of an ``rclone.conf``. Please see the rclone documentation for instructions regarding the generation of this.
    - ``rclone.command``. This is the destination you want for the measurement set in the format expected by rclone - namely theremote type, as defined in your configuration file, followed by the path for that remote.

For example this is a workflow configuration utilising this capability::

    "parameters": {"transmit.model": False,
                   "results.push": True,
                   "rclone.configurl": "https://www.dropbox.com/s/yqmzfs8ovtnonbe/rclone.conf?dl=1",
                   "rclone.command": "gcs:/yan-486-bucket/demo.ms"}

After the receive workflow completes, the data will be synchronised with the end-point.

### Deploying the Receive Workflow Behind a Proxy (PSI deployments)

One of the more complex issues to deal with when deploying to a Kubernetes environment is networking. This is made more
difficult if the Kubernetes environment itself is behind a firewall. The SDP prototype deployment can be thought of as charts
that instantiate containers that themselves instantiate containers. Proxies are usually exposed through environment
variables which requires the environment to be propagated from chart to chart.

The PSI (Prototype System Integration) in an integration environment which is managed by CSIRO and behind a web-proxy. 
When SDP is deployed, all the elements of the prototype need to be informed of the proxy.

### Configuring Workflow to Use The Proxy

Firstly, SDP needs to be deployed with a proxy setting exposed. Upgrading the SDP helm deployment with
the following command will expose the CSIRO proxy to the helm charts of the SDP::

    helm upgrade test ska/sdp --set proxy.server=delphinus.atnf.csiro.au:8888 --set proxy.noproxy='{}'

(Above we assumed you deployed SDP using the `ska/sdp` chart with the name `test`.) 
This will ensure the prototype itself is launched with the correct proxy settings.

But as you would expect this does not necessarily pass the proxy settings on to the workflows. 

In the case of the receive workflow, with the proxy information::

    "parameters": {"transmit.model": False,
                   "results.push": True,
                   "rclone.configurl": "https://www.dropbox.com/s/yqmzfs8ovtnonbe/rclone.conf?dl=1",
                   "rclone.command": "gcs:/yan-483-bucket/psi-demo002.ms",
                   "reception.ring_heaps": 133}

Passing these parameters would launch the receive workflow on the PSI, behind a proxy, configured to push the results to a
Google Cloud Services bucket.

### Changelog

#### 0.3.3

- Ported to use the latest version of workflow library (0.2.4). Capable to deploy multiple receive processes.
  Ports published in the receive addresses match with the actual ports of the receive process(es) 

#### 0.3.2

- use python:3.9-slim as the base docker image