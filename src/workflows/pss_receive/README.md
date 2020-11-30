# PSS Receive Workflow

This is a cheetah based UDP receiver for ingesting PSS single pulse candidate data in the SDP.

## Description


Cheetah is a set of real-time pulsar and fast-transient searching pipelines designed to process data from the CFB. Its end products are candidate pulsar and transient signals which are exported to the SDP for further analysis. The pipelines are started using a command line executable which can be configured using command line flags or by passing a file containing pipeline configuration information.  A full description of the pipeline can be found in the PSS Detailed Design Document.

For the purposes of this demonstration we will use the cheetah\_pipeline executable to read in raw time-frequency data, from which it will produce a set of single pulse candidates which are exported over a UDP stream using SPEAD2. We will use a separate cheetah based pipeline to "receive" this data on the SDP side.

The executables are served from the pss-centos-docker repository.

## Running send and receive standalone

To demostrate their functionality, it is possible to deploy the sender and receiver in same docker container by downloading and running the pss docker.

Pull the PSS docker image by running.

```bash
$ docker pull nexus.engageska-portugal.pt/ska-telescope/pss-docker-centos-dev:0.0.0
```

It's important to ensure that the maximum receive buffer size for all connection types is appropriately tuned on the host so it may be necessary to run the following command before we start the docker container. If this is not set correctly, SPEAD2 will print a warning to the console when we start the receiver and we risk packets being lost.

```bash
$ sudo sysctl net.core.wmem_max=16777216 && sudo sysctl net.core.rmem_max=16777216
```

Once the docker image is pulled we can start it. The entrypoint starts the receiver listening so we don't need to override it.

```bash
$ docker run -it nexus.engageska-portugal.pt/ska-telescope/pss-docker-centos-dev:0.0.0
```

In a seperate terminal we can connect to this docker in order to trigger the cheetah pipeline to send to data to the receiver (over localhost).

```bash
$ docker exec -it <container id> bash
```

By default the cheetah\_pipeline is configured (in our config file) to send candidate data to pss-receive, but this time we want to send to localhost, so we'll need to adjust this parameter in our config file. This file is located at /opt/pss-pipeline/configurations/mvp\_emulator\_config.xml. Find the lines where we configure the IP address spead2 will send to and replace "pss-receive" with "localhost and save the file".


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

Nagivate to /opt/build/thirdparty/cheetah/src/cheetah-build/cheetah/pipeline. In this directory we'll find the cheetah\_pipeline executable. Run this with -h to see the options. We'll trigger the cheetah pipeline with the following command.

```bash
$ ./cheetah_pipeline -s sigproc -p SinglePulse --log-level debug --config /opt/pss-pipeline/configurations/mvp_emulator_config.xml
```

We see a series of log messages from cheetah and from spead2 on the console and we see similar messages in the terminal we started the receiver in, ending with

```bash
[debug][tid=140052772771712][/opt/pss-pipeline/thirdparty/cheetah/cheetah/exporters/src/SpeadLoggingAdapter.cpp:50][1606396139]spead: UDP reader: end of stream detected
[log][tid=140052772771712][/opt/pss-pipeline/thirdparty/cheetah/cheetah/../cheetah/exporters/detail/SpCclSpeadReader.cpp:126][1606396139]Received end of SpCclSpead Stream - resetting
```

The cheetah\_pipeline has completed but the receiver returns to a "waiting" state. At this point you can choose to re-run the cheetah\_pipeline and send another batch, or terminate the receiver by closing the terminal.

What just happened? We triggered the pss pipeline to process test data read from a filterbank file. This file contains data from a 10 s observation of the radio pulsar PSR B1929+10 undertaken with the Lovell telescope at Jodrell Bank. This data was passed through a single pulse search emulator module which generated candidates at a rate specified in the cheetah\_pipeline configuration file. In this case we generate 1 fake single pulse candidate per second which means we should have approximately 10 candidates generated (in might be slightly less than 10 if we have a sifter enabled that will filter candidates that are very close together in time and have a similar DM). The receiver places the list of received candidates in /home/pss2sdp/. If we check here we'll find a .spccl file containing the received candidates' parameters.

```bash
MJD(decimal days)           dm(dimensionless)        width(ms)        sigma
56352.6344797533 MJD                 20              4               37
56352.6345109622 MJD                 50              9               49
56352.6345211904 MJD                 80              8               29
56352.6345252881 MJD                 70              6               62
56352.6345387311 MJD                 80              1               87
56352.6345429563 MJD                 80              7               20
56352.6345546126 MJD                 20              1               14
56352.6345690422 MJD                 60              4               18
56352.6345823104 MJD                 30              3               23
56352.6345889267 MJD                 80              3               58
``` 

## Deploying pss_receive as an SDP workflow in Minikube

Generalised instruction for deploying the SDP can be found at https://gitlab.com/ska-telescope/sdp-integration/-/tree/master/charts.

Start minikube,

```bash
$ minikube config set memory 16384
$ minikube start --cpus=16 --driver virtualbox
```

and set the minikube buffer size

```bash
$ minikube ssh
> sudo sysctl net.core.wmem_max=16777216 && sudo sysctl net.core.rmem_max=16777216
> CTRL+D
```

Create the SDP namespace, add the SDP chart repository to helm and launch the SDP

```bash
$ kubectl create namespace sdp
$ helm repo add ska https://nexus.engageska-portugal.pt/repository/helm-chart
$ helm install test ska/sdp --set helmdeploy.createClusterRole=true
```

You can watch the progress of installing the SDP by running

```bash
$ watch -n 0.5 kubectl get all
```

and once it's up and running it should look something like..

```bash
Every 0.5s: kubectl get al

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

Now we can connect to the sdp-console pod to give us access to the sdpcfg tool which with we can start a workflow.

```bash
$ kubectl exec -it sdp-console-0 -- bash
```

Now let's start the pss\_receive workflow which will deploy the cheetah receiver container

```bash
$ sdpcfg process realtime:pss\_receive:0.2.0
```

We can watch the deployment of the workflow in the sdp namespace

```bash
$ watch -n 0.5 kubectl get all - n sdp
  NAME                                               READY   STATUS    RESTARTS   AGE
  pod/proc-pb-sdpcfg-20201126-00000-workflow-phgwt   1/1     Running   0          30s
  pod/pss-receive-zpgsf                              1/1     Running   0          23s

  NAME                  TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
  service/pss-receive   ClusterIP   10.109.68.42   <none>        9021/UDP   23s

  NAME                                               COMPLETIONS   DURATION   AGE
  job.batch/proc-pb-sdpcfg-20201126-00000-workflow   0/1           30s        30s
  job.batch/pss-receive                              0/1           23s        23s
```

Looking at the logs from the pss-receive pod we can see the receiver waiting for data...

```bash
$ kubectl logs pss-receive-zpgsf -n sdp
```

and we have a service waiting to route data sent to the hostname pss-receive to this pod. Now to send this some data we can use the pss-send kubernetes manifest, deploy-sender.yaml. This will deploy cheetah as a sender pod and have it export data to pss-receive by running.

```bash
$ kubectl apply -f deploy-sender.yaml -n sdp
```

Our sender will appear in the sdp namespace

```bash
 NAME                                               READY   STATUS              RESTARTS   AGE
 pod/proc-pb-sdpcfg-20201126-00000-workflow-phgwt   1/1     Running             0          7m43s
 pod/pss-receive-zpgsf                              1/1     Running             0          7m36s
 pod/sender-5r8s8                                   0/1     ContainerCreating   0          2s

 NAME                  TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
 service/pss-receive   ClusterIP   10.109.68.42   <none>        9021/UDP   7m36s

 NAME                                               COMPLETIONS   DURATION   AGE
 job.batch/proc-pb-sdpcfg-20201126-00000-workflow   0/1           7m43s      7m43s
 job.batch/pss-receive                              0/1           7m36s      7m36s
 job.batch/sender                                   0/1           2s         2s
```

Once the sender has finished running the cheetah pipeline and exporting candidates it will enter a completed state. We can check that candidates have arrived by connecting to the receiver pod and checking the directory /home/pss2sdp, just as we did above.

```bash
kubectl exec -it pss-receive-zpgsf -- bash
```

The .spccl file contains the following lines

```bash
 MJD(decimal days)           dm(dimensionless)        width(ms)        sigma
 56352.6345109918 MJD                 50              7               90
 56352.6345127696 MJD                 80              6               92
 56352.6345161178 MJD                 70              9               23
 56352.6345245652 MJD                 30              6               89
 56352.6345299785 MJD                 40              1               23
 56352.6345304259 MJD                 90              8               17
 56352.634534257 MJD                  60              9               64
 56352.6345442955 MJD                 50              9               34
 56352.6345445415 MJD                 30              1               67
 56352.6345708556 MJD                 80              9               18

```

Our candidates have arrived.

### Cleaning up.

Deleting the completed sender job.

```bash
kubectl delete job sender -n sdp
```

Removing the pss\_receive workflows using the sdp-console. First get a list of entries in the configuration database.

```bash
$ sdpcfg ls -R /
Keys with / prefix:
 /deploy/proc-pb-sdpcfg-20201126-00000-pss-receive
 /deploy/proc-pb-sdpcfg-20201126-00000-workflow
 /master
 /pb/pb-sdpcfg-20201126-00000
 /pb/pb-sdpcfg-20201126-00000/owner
 /pb/pb-sdpcfg-20201126-00000/state
 /subarray/01
 /subarray/02
 /subarray/03
```

Now remove the following entries and we'll see items disappear from the sdp namespace

```bash
$ sdpcfg delete deploy/proc-pb-sdpcfg-20201126-00000-pss-receive
$ sdpcfg delete /deploy/proc-pb-sdpcfg-20201126-00000-workflow
```

Then we can disable the sdp

```bash
$ helm uninstall test

```
