"""
Example PSS Receive workflow
"""

# pylint: disable=invalid-name

import logging
import ska.logging
from ska_sdp_workflow import workflow

# Initialise logging
ska.logging.configure_logging()
log = logging.getLogger("pss_receive")
log.setLevel(logging.INFO)

# Claim Processing block
pb = workflow.ProcessingBlock()
parameters = pb.get_parameters()

log.info("Setting default parameters")
values = {
    "receiver.image": "nexus.engageska-portugal.pt/ska-telescope/pss-docker-centos-dev:1.0.0",
    "receiver.completions": 1,
    "receiver.imagePullPolicy": "IfNotPresent",
    "receiver.containerPort": "9021",
    "receiver.protocol": "UDP",
    "service.port": "9021",
    "sender.image": "pulsarben/pss2sdp-send",
    "sender.completions": 1,
    "sender.imagePullPolicy": "Always",
}

# Override the defaults with values from the PB
if parameters:
    for param in parameters.keys():
        log.info("Over-riding defaults with parameters from the PB")
        values[param] = parameters.get(param)

# Converting the values to nested values
nested_values = pb.nested_parameters(values)

# Create work phase
log.info("Create work phase")
work_phase = pb.create_phase("Work", [])

with work_phase:

    # Deploy PSS Receive with 1 worker.
    work_phase.ee_deploy_helm("pss-receive", nested_values)
    log.info("Done, now idling...")

    for txn in work_phase.wait_loop():
        if work_phase.is_sbi_finished(txn):
            break
        txn.loop(wait=True)
