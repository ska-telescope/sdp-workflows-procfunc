# Test New Receive  Workflow

This is the integration of the CBF-SDP interface emulation and receive workflow

## Deploying the Receive Workflow in the SDP Prototype

To set up SDP on your local machine using Minikube, follow the instructions at 
[Running SDP stand-alone](https://developer.skao.int/projects/ska-sdp-integration/en/latest/running/standalone.html).

### Configuring the Workflow

Although this repository contains example workflows - the helm-charts specific to deployment of the SDP prototype are
stored in another repository (https://gitlab.com/ska-telescope/sdp/ska-sdp-helmdeploy-charts). For the purposes of continuity
we will document the use of the chart here. The documentation may be replicated in other repositories.

The configuration of the receive workflow is managed via adding to the configuration of the processing block.
The processing block can be created using the `ska-sdp` utility or via the iTango interface. In this example we will assume
`ska-sdp` is being used::

    > ska-sdp create pb realtime:test_new_receive:0.1.4

This will start up a default deployment. Without arguments this is a test deployment. It will launch a number of containers and
both a sender and receiver in the same pod. We typically use this for testing purposes. The behaviour and the chart deployed
can be altered by adding a JSON blob to the command line, for example::

    > ska-sdp create pb realtime:test_new_receive:0.1.4 "{ transmit.model : false, reception.ring_heaps : 133 }"

In the above example you can see there are two key value pairs in the JSON blob. The first ``transmit.model : false`` tells
the receive workflow not to start a sender/emulator container. In the future we may make this the default state. The second
``reception.ring_heaps : 133`` is an example of a configuration setting for the receive workflow. All the options supported
by the receiver are supported by the chart deployment. The defaults set by the workflow currently are::

    'model.pull' : 'true',
    'model.url' : 'https://gitlab.com/ska-telescope/cbf-sdp-emulator/-/raw/master/data/sim-vis.ms.tar.gz',
    'model.name' : 'sim-vis.ms',
    'transmit.model' : 'true',
    'reception.outputfilename' : 'output.ms',
    'transmission.channels_per_stream' : 4,
    'transmission.rate' : '147500',
    'payload.method' : 'icd',
    'reader.num_timestamps' : 0,
    'reader.start_chan' : 0,
    'reader.num_chan' :  0,
    'reader.num_repeats' : 1,
    'results.push' : 'false'


The important consideration for the current version of the emulator and receive workflow is that the interface Telescope Model is
via the measurement set. As the charts need to be agnostic about where and how they are deployed it was necessary to provide a
schema whereby the data-model could be accessed by the deployment. What we do here is we provide a mechanism by which the model
can be pulled by providing a URL to a compressed tarfile of the model measurement set, and the name of that measurement set
once unzipped. This should be the same as the measurement set that will be transmitted by the emulator to allow the UVW and
timestamps to match.

Once `ska-sdp` has been run with the desired configuration, the receive will be running as a server inside a pod and waiting for
packets from the emulator (or even the actual CBF).

Note that each workflow may come with multiple versions. Always use the latest number,
unless you know a specific version that suits your needs, or you follow the example above. (The Changelog
at the end of this page may help to decide.)

### Retrieving Data from Kubernetes Deployments

If the receive workflow is configured to generate a measurement set, then it needs to be exported from the Kubernetes environment.
The mechanism we have provided for this is mediated by the ``rclone`` package `https://rclone.org`. In order for this to
work in a secure manner we have provided a mechanism by which a container can pull an rclone configuration file - containing the
credentials and configured end points. This configuration is then used by a container to push the results out. There are only two configuration
options required:

    - ``rclone.configurl``. This is a URL of an ``rclone.conf``. Please see the rclone documentation for instructions regarding the generation of this.
    - ``rclone.command``. This is the destination you want for the measurement set in the format expected by rclone - namely theremote type, as defined in your configuration file, followed by the path for that remote.

For example this is a workflow configuration utilising this capability::

    > ska-sdp create pb realtime:test_new_receive:0.1.4 "{ transmit.model : false, results.push : true , rclone.configurl = 'https://www.dropbox.com/s/yqmzfs8ovtnonbe/rclone.conf?dl=1' , rclone.command = gcs:/yan-486-bucket/demo.ms }"

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

In the case of the receive workflow, this is the equivalent ``ska-sdp`` line with the proxy information::

    > ska-sdp create pb realtime:test_new_receive:0.1.4 "{proxy.server : delphinus.atnf.csiro.au:8888 ,
    transmit.model : false , results.push : true ,
    rclone.configurl : 'https://www.dropbox.com/s/yqmzfs8ovtnonbe/rclone.conf?dl=1' ,
    rclone.command : gcs:/yan-483-bucket/psi-demo002.ms , reception.ring_heaps : 133 ,
    proxy.use : true }"

This command line would launch the receive workflow on the PSI, behind a proxy, configured to push the results to a
Google Cloud Services bucket.

## Changelog