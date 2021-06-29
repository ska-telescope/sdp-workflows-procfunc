"""
Example CBF-SDP receive workflow
Adapted from the vis_receive workflow
This just deploys the simple-pair chart
"""

# pylint: disable=invalid-name

import logging
import ska.logging
from ska_sdp_workflow import workflow

# Initialise logging
ska.logging.configure_logging()
log = logging.getLogger("cbf_sdp")
log.setLevel(logging.INFO)

# Claim Processing block
pb = workflow.ProcessingBlock()

# Create work phase
log.info("Create work phase")
work_phase = pb.create_phase("Work", [])

with work_phase:

    work_phase.ee_deploy_helm("plasma-pipeline")
    log.info("Done, now idling...")

    for txn in work_phase.wait_loop():
        if work_phase.is_sbi_finished(txn):
            break
        txn.loop(wait=True)
