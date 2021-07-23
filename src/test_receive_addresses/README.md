## Test Receive Addresses Workflow

### Introduction

The purpose of this workflow is to test the mechanism for generating SDP
receive addresses from the channel link map for each scan type which is
contained in the list of scan types in the SB. The workflow picks it up from
there, uses it to generate the receive addresses for each scan type and writes
them to the processing block state. It consists of a map of scan type to a
receive address map. This address map get publishes to the appropriate
attribute once the SDP subarray finishes the transition following
AssignResources.


### Testing

[Deploy SDP](https://developer.skao.int/projects/ska-sdp-integration/en/latest/running/standalone.html)
and make sure the [iTango console](https://developer.skao.int/projects/ska-sdp-integration/en/latest/running/standalone.html#accessing-the-tango-interface)
pod is also running.

After entering the iTango pod, obtain a handle to a subarray device and turn it on:

```
d = DeviceProxy('mid_sdp/elt/subarray_1')
d.On()
```

If you are not sure what devices are available, list them with `lsdev`.

Here is the configuration string for the scheduling block instance:

```
config = '''
{
  "id": "sbi-mvp01-20200318-0001",
  "max_length": 21600.0,
  "scan_types": [
     {
       "id": "science_A",
       "coordinate_system": "ICRS", "ra": "02:42:40.771", "dec": "-00:00:47.84",
       "channels": [{
          "count": 744, "start": 0, "stride": 2, "freq_min": 0.35e9, "freq_max": 0.368e9, "link_map": [[0,0], [200,1], [744,2], [944,3]]
       },{
          "count": 744, "start": 2000, "stride": 1, "freq_min": 0.36e9, "freq_max": 0.368e9, "link_map": [[2000,4], [2200,5]]
       }]
     },
     {
       "id": "calibration_B",
       "coordinate_system": "ICRS", "ra": "12:29:06.699", "dec": "02:03:08.598",
       "channels": [{
          "count": 744, "start": 0, "stride": 2, "freq_min": 0.35e9, "freq_max": 0.368e9, "link_map": [[0,0], [200,1], [744,2], [944,3]]
       },{
          "count": 744, "start": 2000, "stride": 1, "freq_min": 0.36e9, "freq_max": 0.368e9, "link_map": [[2000,4], [2200,5]]
       }]
     }
   ],
  "processing_blocks": [
    {
      "id": "pb-mvp01-20200318-0001",
      "workflow": {"type": "realtime", "id": "test_receive_addresses", "version": "0.3.4"},
      "parameters": {}
    },
    {
      "id": "pb-mvp01-20200318-0002",
      "workflow": {"type": "realtime", "id": "test_realtime", "version": "0.2.2"},
      "parameters": {}
    }
  ]
} '''
```

Note that each workflow may come with multiple versions. Always use the latest number,
unless you know a specific version that suits your needs. (The Changelog
at the end of this page may help to decide.)

Start the scheduling block instance by the AssignResources command:

```
d.AssignResources(config)
```

You can connect to the configuration database by running the following command:

```
kubectl exec -it sdp-console-0 -- bash
```

and from there to see the full list of entries, run

```
ska-sdp list -a
```

To check if the receive addresses are updated in the processing block state correctly, run the following command:

```
ska-sdp get pb pb-mvp01-20200318-0001/state
```

and the output should look like this:

```
/pb/pb-mvp01-20200318-0001/state = {
  "receive_addresses": {
    "calibration_B": {
      "host": [
        [
          0,
          "192.168.0.1"
        ],
        [
          2000,
          "192.168.0.1"
        ]
      ],
      "port": [
        [
          0,
          9000,
          1
        ],
        [
          2000,
          9000,
          1
        ]
      ]
    },
    "science_A": {
      "host": [
        [
          0,
          "192.168.0.1"
        ],
        [
          2000,
          "192.168.0.1"
        ]
      ],
      "port": [
        [
          0,
          9000,
          1
        ],
        [
          2000,
          9000,
          1
        ]
      ]
    }
  },
  "resources_available": true,
  "status": "RUNNING"
}
```

To access the SBI run this

```
ska-sdp get /sb/sbi-mvp01-20200318-0001
```

In there you should see that pb_receive_addresses is updated with the PB_ID.

This should now update the receiveAddresses attribute with receive addresses map
and that can be verified by running d.receiveAddresses and the output should look like this:

```
Out[4]: '{"calibration_B": {"host": [[0, "192.168.0.1"], [2000, "192.168.0.1"]], "port": [[0, 9000, 1], [2000, 9000, 1]]}, "science_A": {"host": [[0, "192.168.0.1"], [2000, "192.168.0.1"]], "port": [[0, 9000, 1], [2000, 9000, 1]]}}'
```

### Changelog

#### 0.3.7

- Use dependencies from the central artefact repository and publish the
  workflow image there.

#### 0.3.6

- Ported to use the latest version of workflow library (0.2.4).

#### 0.3.5

- use python:3.9-slim as the base docker image
