"""
Workflow to test batch processing.
"""

import time
import logging
import ska.logging
from ska_sdp_workflow import workflow

ska.logging.configure_logging()
LOG = logging.getLogger("test_batch")
LOG.setLevel(logging.DEBUG)

# Claim processing block
pb = workflow.ProcessingBlock()

# Get the parameters from the processing block
parameters = pb.get_parameters()
duration = parameters.get("duration", 60.0)

# Make buffer request - right now this doesn't do anything, but it gives an
# example of how resource requests will be made
out_buffer_res = pb.request_buffer(100.0e6, tags=["images"])

# Create work phase with the (fake) buffer request.
work_phase = pb.create_phase("Work", [out_buffer_res])

# Define the function to be executed by the execution engine. In a real
# pipeline this would be defined elsewhere and imported here.


def some_processing(duration):
    """Do some processing for the required duration"""
    time.sleep(duration)


with work_phase:

    deploy = work_phase.ee_deploy_test(
        "test_batch", func=some_processing, f_args=(duration,)
    )

    for txn in work_phase.wait_loop():
        # Check if deployment is finished.
        if deploy.is_finished(txn):
            break
        txn.loop(wait=True)
