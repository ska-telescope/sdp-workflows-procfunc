"""
Workflow to test generation of receive addresses.

The purpose of this workflow is to test the mechanism for generating SDP
receive addresses from the channel link map contained in the SBI. The workflow
picks it up from there, uses it to generate the receive addresses for each scan
type and writes them to the processing block state. The subarray publishes this
address map on the appropriate attribute to complete the transition following
AssignResources.

This workflow does not generate any deployments.
"""

import logging
import ska.logging
from ska_sdp_workflow import workflow

ska.logging.configure_logging()
LOG = logging.getLogger("test_receive_addresses")
LOG.setLevel(logging.DEBUG)

# Claim processing block
pb = workflow.ProcessingBlock()

# Default maximum number of channels per receive process
max_channels = 20

# Port configuration
port_start = 9000
num_ports = 1

# Get the channel link map from SBI
scan_types = pb.get_scan_types()

# Port and receive process configuration
host_port, num_process = pb.configure_recv_processes_ports(
    scan_types, max_channels, port_start, num_ports
)

# Create work phase
LOG.info("Create work phase")
work_phase = pb.create_phase("Work", [])

with work_phase:

    # Deploying a fake execution engine.
    work_phase.ee_deploy_helm("test-receive")

    # Add receive addresses to pb
    pb.receive_addresses(configured_host_port=host_port)

    # ... Do some processing here ...

    LOG.info("Done, now idling...")

    for txn in work_phase.wait_loop():
        if work_phase.is_sbi_finished(txn):
            break
        txn.loop(wait=True)
