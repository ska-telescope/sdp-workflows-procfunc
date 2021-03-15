"""
Example Dask workflow.
"""

import time
import logging
import dask
import ska.logging
from ska_sdp_workflow import workflow

# Initialise logging
ska.logging.configure_logging()
LOG = logging.getLogger("test_dask")
LOG.setLevel(logging.INFO)

# Claim Processing block
pb = workflow.ProcessingBlock()

# Get parameters from processing block
parameters = pb.get_parameters()
n_workers = parameters.get("n_workers", 2)  # Number of Dask workers

# Create work phase
LOG.info("Creating work phase")
work_phase = pb.create_phase("Work", [])

# These are the functions executed by the Dask execution engines. In a real
# pipeline they would be defined elsewhere and imported here.


def inc(x_i):
    time.sleep(2)
    return x_i + 1


def dec(y_i):
    time.sleep(2)
    return y_i - 1


def add(x, y):
    x1 = inc(x)
    y1 = dec(y)
    time.sleep(2)
    z = x1 + y1
    return z


def calc(x, y):
    # This is the top-level function that returns the Dask graph to be executed
    # by the execution engine. It will be called by the EE interface to
    # construct the graph, then the graph will be executed on the Dask
    # deployment by calling its 'compute' method.
    x1 = dask.delayed(inc)(x)
    y1 = dask.delayed(dec)(y)
    z = dask.delayed(add)(x1, y1)
    return z


with work_phase:

    # Deploy two instances of a Dask EE
    deploy1 = work_phase.ee_deploy_dask("dask-1", n_workers, calc, (1, 5))
    deploy2 = work_phase.ee_deploy_dask("dask-2", n_workers, calc, (1, 7))

    # Wait until deployments are finished or PB is cancelled
    for txn in work_phase.wait_loop():
        if deploy1.is_finished(txn) and deploy2.is_finished(txn):
            break
        txn.loop(wait=True)
