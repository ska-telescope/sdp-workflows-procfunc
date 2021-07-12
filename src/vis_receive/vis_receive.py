"""
Example receive workflow
Ported CBF-SDP receive workflow
Deploys and update receive addresses attribute with DNS-based IP address
"""

# pylint: disable=invalid-name

import logging
import ska.logging
from ska_sdp_workflow import workflow

# Initialise logging
ska.logging.configure_logging()
log = logging.getLogger("vis_receive")
log.setLevel(logging.INFO)

# Claim processing block
pb = workflow.ProcessingBlock()
parameters = pb.get_parameters()

log.info("Setting default parameters")
values = {
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
}

# Default maximum number of channels per receive process
max_channels = 20

# Override the defaults with values from the PB
if parameters:
    for param in parameters.keys():
        log.info("Over-riding defaults with parameters from the PB")
        values[param] = parameters.get(param)

# Port configuration
port_start = values["reception.receiver_port_start"]
num_ports = values["reception.num_ports"]

# Get the channel link map from SBI
scan_types = pb.get_scan_types()

# Port and receive process configuration
host_port, num_process = pb.configure_recv_processes_ports(
    scan_types, max_channels, port_start, num_ports
)

# Update values with number of process
values["replicas"] = num_process

# Construct command list
command = []

for keys, v in values.items():
    if keys.startswith("recv_emu"):
        command.append(str(v))
        command.append("-o")
    if keys.startswith("transmission"):
        k = str(keys) + "=" + str(v)
        command.append(k)
        command.append("-o")
    if keys.startswith("reader"):
        k = str(keys) + "=" + str(v)
        command.append(k)
        command.append("-o")
    if keys.startswith("reception"):
        if keys.endswith("outputfilename"):
            k = str(keys) + "=" + values["pvc.path"] + "/" + str(v)
        else:
            k = str(keys) + "=" + str(v)
        command.append(k)
        command.append("-o")
    if keys.startswith("payload"):
        k = str(keys) + "=" + str(v)
        command.append(k)
        command.append("-o")

data_model = (
    str("reception.datamodel") + "=" + values["pvc.path"] + "/" + values["model.name"]
)
command.append(data_model)
values["command"] = command

# Convert values to nested parameters
nested_values = pb.nested_parameters(values)

# Create work phase
log.info("Create work phase")
work_phase = pb.create_phase("Work", [])

with work_phase:

    # Deploy visibility receive
    deploy_name = "receive"
    ee_receive = work_phase.ee_deploy_helm(deploy_name, nested_values)
    deploy_id = ee_receive.get_id()

    # Add receive addresses to pb
    pb.receive_addresses(chart_name=deploy_id, configured_host_port=host_port)

    log.info("Done, now idling...")

    for txn in work_phase.wait_loop():
        if work_phase.is_sbi_finished(txn):
            break
        txn.loop(wait=True)
