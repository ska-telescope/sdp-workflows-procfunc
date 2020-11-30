"""
Example visibility receive workflow.
"""

# pylint: disable=invalid-name

import logging
import ska.logging
from ska_sdp_workflow import workflow

# Initialise logging
ska.logging.configure_logging()
log = logging.getLogger('vis_receive')
log.setLevel(logging.INFO)

# Claim processing block
pb = workflow.ProcessingBlock()

# Create work phase
log.info("Create work phase")
work_phase = pb.create_phase('Work', [])

with work_phase:

    # Deploy visibility receive
    work_phase.ee_deploy_helm('vis-receive')
    log.info("Done, now idling...")

    for txn in work_phase.wait_loop():
        if work_phase.is_sbi_finished(txn):
            break
        txn.loop(wait=True)
