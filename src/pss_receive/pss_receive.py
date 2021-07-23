"""
Example PSS Receive workflow
"""

# pylint: disable=invalid-name

import logging
import ska_ser_logging
from ska_sdp_workflow import workflow

# Initialise logging
ska_ser_logging.configure_logging()
log = logging.getLogger("pss_receive")
log.setLevel(logging.INFO)

# Claim Processing block
pb = workflow.ProcessingBlock()

# Create work phase
log.info("Create work phase")
work_phase = pb.create_phase("Work", [])

with work_phase:

    # Deploy PSS Receive with 1 worker.
    work_phase.ee_deploy_helm("pss-receive")
    log.info("Done, now idling...")

    for txn in work_phase.wait_loop():
        if work_phase.is_sbi_finished(txn):
            break
        txn.loop(wait=True)
