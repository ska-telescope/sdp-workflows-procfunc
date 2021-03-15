"""
Example CBF-SDP receive workflow
Adapted from the vis_receive workflow
This just deploys the simple-pair chart
"""

# pylint: disable=invalid-name

import logging
import ska.logging
from ska_sdp_workflow import workflow

# Initialise logging and configuration
ska.logging.configure_logging()
log = logging.getLogger("cbf_sdp")
log.setLevel(logging.INFO)

# Claim processing block
pb = workflow.ProcessingBlock()
parameters = pb.get_parameters()

log.info("Setting default parameters")
values = {
    "model.pull": "true",
    "model.url": "https://gitlab.com/ska-telescope/cbf-sdp-emulator/-/raw/master/data/sim-vis.ms.tar.gz",
    "model.name": "sim-vis.ms",
    "transmit.model": "true",
    "reception.outputfilename": "output.ms",
    "transmission.channels_per_stream": 4,
    "transmission.rate": "147500",
    "payload.method": "icd",
    "reader.num_timestamps": 0,
    "reader.start_chan": 0,
    "reader.num_chan": 0,
    "reader.num_repeats": 1,
    "results.push": "false",
}

# Override the defaults with values from the PB
for param in parameters.keys():
    log.info("Over-riding defaults with parameters from the PB")
    values[param] = parameters.get(param)

# Create work phase
log.info("Create work phase")
# Buffer request is not required therefore, pass in an empty list
work_phase = pb.create_phase("Work", [])

with work_phase:

    # Deploy CBF-SDP emulator
    work_phase.ee_deploy_helm("cbf-sdp-emulator", values)
    log.info("Done, now idling...")

    for txn in work_phase.wait_loop():
        if work_phase.is_sbi_finished(txn):
            break
        txn.loop(wait=True)
