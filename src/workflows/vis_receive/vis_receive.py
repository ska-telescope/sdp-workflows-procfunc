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
    "reception.outputfilename": "output.ms",
    "transmission.channels_per_stream": 4,
    "transmission.rate": "147500",
    "payload.method": "icd",
    "reader.num_timestamps": 0,
    "reader.start_chan": 0,
    "reader.num_chan": 0,
    "reader.num_repeats": 1,
    "results.push": "false",
    "pvc.name": "local-pvc",
    "pvc.path": "/mnt/data",
}

# Override the defaults with values from the PB
if parameters:
    for param in parameters.keys():
        log.info("Over-riding defaults with parameters from the PB")
        values[param] = parameters.get(param)

# Create work phase
log.info("Create work phase")
work_phase = pb.create_phase("Work", [])

with work_phase:

    # Deploy visibility receive
    work_phase.ee_deploy_helm("receive", values)

    # Get the channel link map from SBI
    scan_types = pb.get_scan_types()

    # Add receive addresses to pb
    pb.receive_addresses(scan_types)

    log.info("Done, now idling...")

    for txn in work_phase.wait_loop():
        if work_phase.is_sbi_finished(txn):
            break
        txn.loop(wait=True)
