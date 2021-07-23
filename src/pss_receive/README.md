# PSS Receive Workflow

This is a cheetah-based User Datagram Protocol (UDP) receiver for ingesting PSS (Pulsar Search Sub-system)
single pulse candidate data in the SDP (Science Data Processor).

## Description

Cheetah is a set of real-time pulsar and fast-transient searching pipelines designed to process data from the CBF (Correlator and Beamformer).
Its end products are candidate pulsar and transient signals which are exported to the SDP for further analysis.
The pipelines are started using a command line executable which can be configured using command line flags or
by passing a file containing pipeline configuration information.  A full description of the pipeline can be found in the
PSS Detailed Design Document.

For the purposes of this demonstration we will use the cheetah\_pipeline executable (PSS) to receive
UDP time-frequency data from a CBF emulator pipeline, from which it will produce single-pulse candidate data
which is exported over a UDP stream using [SPEAD2](https://spead2.readthedocs.io/en/latest/).
We will use a separate cheetah based pipeline to "receive" this data on the SDP side.

The executables are served from the [pss-centos-docker repository](https://gitlab.com/ska-telescope/pss-centos-docker).

## Running send and receive standalone

To demonstrate their functionality, it is possible to deploy the CBF emulator,
the PSS pipeline and the SDP receive pipeline in same docker container by downloading and running the pss docker.

Pull the PSS docker image by running.

```bash
$ docker pull nexus.engageska-portugal.pt/ska-telescope/pss-docker-centos-dev:1.0.0
```

It's important to ensure that the maximum receive buffer size for all connection types is appropriately tuned on the host,
so it may be necessary to run the following command before we start the docker container.
If this is not set correctly, SPEAD2 will print a warning to the console when we start the receiver and we risk packets being lost.
(Note, the below command was tested on Linux.)

```bash
sudo sysctl net.core.rmem_max=268435456 && sudo sysctl net.core.wmem_max=268435456 && sudo sysctl net.core.netdev_max_backlog=65536 && sudo sysctl net.core.wmem_default=268435456 && sudo sysctl net.core.rmem_default=268435456
```

Once the docker image is pulled, we can start it. The entrypoint starts the receiver listening so we don't need to override it.

```bash
$ docker run -it nexus.engageska-portugal.pt/ska-telescope/pss-docker-centos-dev:1.0.0
```

In a separate terminal we can connect to this docker in order to trigger the cheetah pipeline to start listening for a UDP stream from the CBF emulator.

```bash
$ docker exec -it <container id> bash
```

By default, the cheetah\_pipeline is configured (in our config files) to send candidate data to pss-receive and our CBF emulator will send data to cbf-receive, but this time we want both to send to localhost, so we'll need to adjust this parameter in our config files. This file is located at /opt/pss-pipeline/configurations/mvp\_emulator\_config.xml. Find the lines where we configure the IP address spead2 will send to and replace "pss-receive" with "localhost" and save the file". Do the same with cbf-emulator.xml (in the same directory) and replace "cbf-receive" with "localhost".


```bash
<spccl_spead>
 <candidate_window>
  <ms_before>10</ms_before>
  <ms_after>10</ms_after>
 </candidate_window>
 <rate_limit>1e7</rate_limit>
 <ip>
  <port>9021</port>
  <ip_address>pss-receive</ip_address>
 </ip>
 <id>spead_stream</id>
</spccl_spead>
```

Navigate to /opt/build/thirdparty/cheetah/src/cheetah-build/cheetah/pipeline. In this directory we'll find the cheetah\_pipeline executable. Run this with -h to see the options. We'll trigger the cheetah pipeline with the following command.

```bash
$ ./cheetah_pipeline -s udp_low -p SinglePulse --log-level debug --config /opt/pss-pipeline/configurations/mvp_emulator_config.xml
```

Where:

* -s denotes the source of the input data stream (in this case a udp stream from the CBF emulator
* -p is the specific pipeline that cheetah should run (in this case the single pulse search pipeline)
* --config is the path to the configuration file

We see some output from the pss pipeline to show that it is in a listening state.

```bash
[log][tid=140131450292096][/opt/pss-pipeline/thirdparty/cheetah/cheetah/../cheetah/pipeline/detail/BeamLauncher.cpp:148][1613571585]Creating Beams....
[log][tid=140131450292096][/opt/pss-pipeline/thirdparty/cheetah/cheetah/rcpt_low/src/UdpStream.cpp:37][1613571585]listening for UDP Low stream from 0.0.0.0:9029
[debug][tid=140131450292096][/opt/pss-pipeline/thirdparty/cheetah/cheetah/../cheetah/exporters/detail/DataExport.cpp:61][1613571585]Creating sink of type spccl_files (id=spccl_files)
[debug][tid=140131450292096][/opt/pss-pipeline/thirdparty/cheetah/cheetah/../cheetah/exporters/detail/DataExport.cpp:61][1613571585]Creating sink of type spccl_sigproc_files (id=candidate_files)
[debug][tid=140131450292096][/opt/pss-pipeline/thirdparty/cheetah/cheetah/../cheetah/exporters/detail/DataExport.cpp:61][1613571585]Creating sink of type spccl_spead (id=spead_stream)
[log][tid=140131450292096][/opt/pss-pipeline/thirdparty/cheetah/cheetah/exporters/src/SpCclSpeadStreamer.cpp:46][1613571585]Spead UDP output stream on 127.0.0.1:9021 (limited to 10000000.000000 bytes/sec)
[log][tid=140131450292096][/opt/build/thirdparty/panda/install/include/panda/detail/packet_stream/PacketStreamImpl.cpp:125][1613571585]start packet stream listening on:0.0.0.0:9029
[log][tid=140131450292096][/opt/pss-pipeline/thirdparty/cheetah/cheetah/../cheetah/pipeline/detail/BeamLauncher.cpp:171][1613571585]Finished creating pipelines
[log][tid=140131450292096][/opt/pss-pipeline/thirdparty/cheetah/cheetah/../cheetah/pipeline/detail/BeamLauncher.cpp:223][1613571585]Starting Beam: 1

```

We can then trigger the CBF emulator to send to data into pss where the single pulse search pipeline will process it.
Connect a third terminal to this docker container and navigate to /opt/build/thirdparty/cheetah/src/cheetah-build/cheetah/emulator.
In this directory we'll find the cheetah\_emulator executable. Run this with -h to see the options.
We'll trigger the emulator with the following command.


```bash
$ ./cheetah_emulator --config /opt/pss-pipeline/configurations/cbf_emulator_config.xml --log-level debug
```

The emulator will produce some log messages to show it's working and streaming Gaussian noise over UDP.

```bash
[log][tid=140592331782016][/opt/build/thirdparty/panda/install/include/panda/detail/SocketConnectionImpl.cpp:203][1613572250][this=0x1792948] setting remote endpoint:127.0.0.1:9029
[log][tid=140592331782016][/opt/pss-pipeline/thirdparty/cheetah/cheetah/emulator/src/emulator_main.cpp:63][1613572250]emulator using generator: 'gaussian_noise'
```

and after a short time, the cheetah\_pipeline will show a bunch of log message to show that it is processing the data
that it is receiving from CBF.

```bash
[debug][tid=140130935695104][/opt/build/thirdparty/panda/install/include/panda/detail/packet_stream/ChunkerContext.cpp:453][1613572937]clearing chunk 0x7f72c0099610
[debug][tid=140130935695104][/opt/build/thirdparty/panda/install/include/panda/detail/DataManager.cpp:221][1613572937]pushing data 0x7f72c0099610
```

Eventually we'll see that pss-receive is starting to receive candidate data when log message like the following appear

```bash
[debug][tid=139774761645952][/opt/pss-pipeline/thirdparty/cheetah/cheetah/exporters/src/SpeadLoggingAdapter.cpp:50][1613572975]spead: packet with 1432 bytes of payload at offset 52279064 added to heap 9
```

Whenever we like, we can simple CTRL+C on the CBF emulator and wait for the final packets to arrive at pss-receive.

What just happened? We triggered the pss pipeline to listen for test data from a udp stream.
This data was passed through a single pulse search emulator module and the resulting single pulse candidate
data was exported to the pss-receive application.

## Deploying pss\_receive as an SDP workflow in Minikube

Generalised instruction for deploying the SDP can be found at
[Running SDP stand-alone](https://developer.skao.int/projects/ska-sdp-integration/en/latest/running/standalone.html).

Start minikube,

```bash
$ minikube config set memory 16384
$ minikube start --cpus=16 --driver virtualbox
```

and set the minikube buffer size (command tested on Linux)

```bash
$ minikube ssh
> sudo sysctl net.core.rmem_max=268435456 && sudo sysctl net.core.wmem_max=268435456 && sudo sysctl net.core.netdev_max_backlog=65536 && sudo sysctl net.core.wmem_default=268435456 && sudo sysctl net.core.rmem_default=268435456
> CTRL+D
```

Create the SDP namespace, add the SDP chart repository to helm and launch the SDP

```bash
$ kubectl create namespace sdp
$ helm repo add ska https://artefact.skao.int/repository/helm-internal
$ helm repo update
$ helm install test ska/ska-sdp --set helmdeploy.createClusterRole=true
```

You can watch the progress of installing the SDP by running

```bash
$ watch -n 0.5 kubectl get all
```

and once it's up and running it should look something like..

```bash
Every 0.5s: kubectl get all

NAME                                   READY   STATUS	   RESTARTS   AGE
pod/databaseds-tango-base-test-0       1/1     Running     3          23h
pod/sdp-console-0                      1/1     Running     0          23h
pod/sdp-etcd-0                         1/1     Running     0          23h
pod/sdp-helmdeploy-0                   1/1     Running     0          23h
pod/sdp-lmc-configurator-dtmrp         0/1     Completed   0          23h
pod/sdp-lmc-master-0                   1/1     Running     0          23h
pod/sdp-lmc-subarray-1-0               1/1     Running     0          23h
pod/sdp-lmc-subarray-2-0               1/1     Running     0          23h
pod/sdp-lmc-subarray-3-0               1/1     Running     0          23h
pod/sdp-proccontrol-0                  1/1     Running     0          23h
pod/tango-base-tangodb-0               1/1     Running     0          23h
pod/tangotest-tango-base-test-test-0   1/1     Running     0          23h

NAME                                     TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)             AGE
service/databaseds-tango-base-test	 NodePort    10.106.233.129   <none>        10000:30412/TCP     23h
service/kubernetes                       ClusterIP   10.96.0.1        <none>        443/TCP             43h
service/sdp-console                      ClusterIP   None             <none>        <none>              23h
.
.
.
. and so on
```

Now we can connect to the sdp-console pod to give us access to the `ska-sdp` tool which with we can start a workflow.

```bash
$ kubectl exec -it sdp-console-0 -- bash
```

Now let's start the pss\_receive workflow which will deploy the cheetah receiver container

```bash
$ ska-sdp create pb realtime:pss_receive:0.2.1
```

Note that each workflow may come with multiple versions. Always use the latest number,
unless you know a specific version that suits your needs. (The Changelog
at the end of this page may help to decide.)

We can watch the deployment of the workflow in the sdp namespace

```bash
$ watch -n 0.5 kubectl get all - n sdp
  NAME                                               READY   STATUS    RESTARTS   AGE
  pod/proc-pb-sdpcli-20210217-00003-workflow-njh8s   1/1     Running   0          21s
  pod/pss-receive-9rsbf                              1/1     Running   0          14s

  NAME                  TYPE        CLUSTER-IP	  EXTERNAL-IP   PORT(S)    AGE
  service/pss-receive   ClusterIP   10.111.94.131   <none>        9021/UDP   14s

  NAME                                               COMPLETIONS   DURATION   AGE
  job.batch/proc-pb-sdpcli-20210217-00003-workflow   0/1           21s        22s
  job.batch/pss-receive                              0/1           14s        14s
```

Looking at the logs from the pss-receive pod we can see the receiver waiting for data...

```bash
$ kubectl logs pss-receive-9rsbf -n sdp
[debug][tid=139702737897344][/opt/pss-pipeline/thirdparty/cheetah/cheetah/../cheetah/exporters/detail/DataExport.cpp:61][1613583356]Creating sink of type sp_candidate_data (id=candidate_files)
```

and we have a service waiting to route data sent to the hostname pss-receive to this pod.
Now to send this some data we can use the pss-pipeline kubernetes manifest,
[deploy-sender.yaml](https://gitlab.com/ska-telescope/sdp/ska-sdp-science-pipelines/-/blob/master/src/pss_receive/deploy-sender.yaml).
This will deploy cheetah as a new pod. It will wait for data to arrive from the CBF emulator
(which we'll deploy shortly) and when it arrives will run the single pulse emulator pipeline and export the
candidate to the pss-receive application.

```bash
$ kubectl apply deploy-sender.yaml -n sdp
```

Our sender pod "pss-pipeline" will appear in the sdp namespace

```bash
  NAME                                               READY   STATUS              RESTARTS   AGE
  pod/proc-pb-sdpcli-20210217-00003-workflow-njh8s   1/1     Running             0          3m9s
  pod/pss-pipeline-wjdm6                             0/1     ContainerCreating   0          2s
  pod/pss-receive-9rsbf                              1/1     Running             0          3m2s

  NAME                  TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
  service/cbf-receive   ClusterIP   10.102.80.249   <none>        9029/UDP   2s
  service/pss-receive   ClusterIP   10.111.94.131   <none>        9021/UDP   3m2s

  NAME                                               COMPLETIONS   DURATION   AGE
  job.batch/proc-pb-sdpcli-20210217-00003-workflow   0/1           3m10s      3m11s
  job.batch/pss-pipeline                             0/1           3s         3s
  job.batch/pss-receive                              0/1           3m3s       3m3s
```

We can see that the pss-pipeline is waiting for data from the CBF by running..

```bash
$ kubectl logs pss-pipeline-wjdm6 -n sdp
  [log][tid=140007832209280][/opt/pss-pipeline/thirdparty/cheetah/cheetah/../cheetah/pipeline/detail/BeamLauncher.cpp:148][1613583537]Creating Beams....
  [log][tid=140007832209280][/opt/pss-pipeline/thirdparty/cheetah/cheetah/rcpt_low/src/UdpStream.cpp:37][1613583537]listening for UDP Low stream from 0.0.0.0:9029
  [debug][tid=140007832209280][/opt/pss-pipeline/thirdparty/cheetah/cheetah/../cheetah/exporters/detail/DataExport.cpp:61][1613583537]Creating sink of type spccl_files (id=spccl_files)
  [debug][tid=140007832209280][/opt/pss-pipeline/thirdparty/cheetah/cheetah/../cheetah/exporters/detail/DataExport.cpp:61][1613583537]Creating sink of type spccl_sigproc_files (id=candidate_files)
  [debug][tid=140007832209280][/opt/pss-pipeline/thirdparty/cheetah/cheetah/../cheetah/exporters/detail/DataExport.cpp:61][1613583537]Creating sink of type spccl_spead (id=spead_stream)
  [log][tid=140007832209280][/opt/pss-pipeline/thirdparty/cheetah/cheetah/exporters/src/SpCclSpeadStreamer.cpp:46][1613583537]Spead UDP output stream on 10.111.94.131:9021 (limited to 10000000.000000 bytes/sec)
  [log][tid=140007832209280][/opt/build/thirdparty/panda/install/include/panda/detail/packet_stream/PacketStreamImpl.cpp:125][1613583537]start packet stream listening on:0.0.0.0:9029
  [log][tid=140007832209280][/opt/pss-pipeline/thirdparty/cheetah/cheetah/../cheetah/pipeline/detail/BeamLauncher.cpp:171][1613583537]Finished creating pipelines
  [log][tid=140007832209280][/opt/pss-pipeline/thirdparty/cheetah/cheetah/../cheetah/pipeline/detail/BeamLauncher.cpp:223][1613583537]Starting Beam: 1
```

Now we can deploy the CBF emulator to stream UDP time frequency data using the pss_receive:0.2.1
[deploy-cbf-emulator.yaml](https://gitlab.com/ska-telescope/sdp/ska-sdp-science-pipelines/-/blob/master/src/pss_receive/deploy-cbf-emulator.yaml):

```bash
$ kubectl apply -f deploy-cbf-emulator.yaml -n sdp
```

This will deploy a cbf-emulator pod. Now let's watch the logs of the pss-receive application and eventually
we'll see packets arriving..

```bash
$ kubectl logs -f pss-receive-9rsbf -n sdp
  .
  .
  [debug][tid=139702737897344][/opt/pss-pipeline/thirdparty/cheetah/cheetah/exporters/src/SpeadLoggingAdapter.cpp:50][1613584774]spead: packet with 1432 bytes of payload at offset 211172184 added to heap 2
  [debug][tid=139702737897344][/opt/pss-pipeline/thirdparty/cheetah/cheetah/exporters/src/SpeadLoggingAdapter.cpp:50][1613584774]spead: packet with 1432 bytes of payload at offset 211173616 added to heap 2
  [debug][tid=139702737897344][/opt/pss-pipeline/thirdparty/cheetah/cheetah/exporters/src/SpeadLoggingAdapter.cpp:50][1613584774]spead: packet with 1432 bytes of payload at offset 211175048 added to heap 2
 .
 .
 .
```

### Cleaning up.

We can simply turn off the CBF and PSS will the following..

```bash
kubectl delete job cbf-emulator -n sdp
kubectl delete job pss-pipeline -n sdp
kubectl delete service cbf-receive -n sdp
```
Removing the pss\_receive workflows using the sdp-console. First get a list of entries in the configuration database.

```bash
$ ska-sdp list -a
Keys with / prefix:
 /deploy/proc-pb-sdpcli-20201126-00000-pss-receive
 /deploy/proc-pb-sdpcli-20201126-00000-workflow
 /master
 /pb/pb-sdpcli-20201126-00000
 /pb/pb-sdpcli-20201126-00000/owner
 /pb/pb-sdpcli-20201126-00000/state
 /subarray/01
 /subarray/02
 /subarray/03
```

Now remove the following entries, and we'll see items disappear from the sdp namespace

```bash
$ ska-sdp delete deployment proc-pb-sdpcli-20201126-00000-pss-receive
$ ska-sdp delete deployment proc-pb-sdpcli-20201126-00000-workflow
```

Then we can disable the sdp

```bash
$ helm uninstall test
```

## Changelog

### 0.2.2

- use python:3.9-slim as the base docker image