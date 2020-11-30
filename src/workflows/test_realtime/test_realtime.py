"""
Workflow to test real-time processing.
"""

import logging
import ska.logging

from ska_sdp_workflow import workflow

ska.logging.configure_logging()
LOG = logging.getLogger('test_realtime')
LOG.setLevel(logging.DEBUG)

# Claim processing block
pb = workflow.ProcessingBlock()

# Get parameters from processing block.
parameters = pb.get_parameters()
length = parameters.get('length', 3600.0)

# Make buffer requests - right now this doesn't do anything, but it gives an
# example of how resource requests will be made
in_buffer_res = pb.request_buffer(100.0e6, tags=['sdm'])
out_buffer_res = pb.request_buffer(length * 6e15 / 3600, tags=['visibilities'])

# Create work phase
LOG.info("Creating work phase")
work_phase = pb.create_phase('Work', [in_buffer_res, out_buffer_res])

with work_phase:

    LOG.info("Pretending to deploy execution engine.")
    LOG.info("Done, now idling...")

    for txn in work_phase.wait_loop():
        if work_phase.is_sbi_finished(txn):
            break
        txn.loop(wait=True)
