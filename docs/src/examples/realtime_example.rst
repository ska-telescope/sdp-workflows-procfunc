.. _example_realtime:

Real-time workflow
==================

This is a simple example of a real-time workflow (``test_realtime``). It requires the
`logging`, `ska_ser_logging` and `ska_sdp_workflow` Python modules.

.. code-block::

  import logging
  import ska_ser_logging
  import ska_sdp_workflow

We initialise the logging

.. code-block::

  ska_ser_logging.configure_logging()
  LOG = logging.getLogger('test_realtime')
  LOG.setLevel(logging.DEBUG)

The first step is to claim the processing block and get its parameters.

.. code-block::

  pb = workflow.ProcessingBlock()
  parameters = pb.get_parameters()

We then need to request the input and output buffer reservations. This is
just a placeholder currently to give an example of how resources will be
requested.

.. code-block::

  in_buffer_res = pb.request_buffer(100e6, tags=['sdm'])
  out_buffer_res = pb.request_buffer(parameters['length'] * 6e15 / 3600, tags=['visibilities'])

We declare the phases of the workflow and define which resource requests are
needed for each phase. In the current implementation, we can only declare one
phase, which in this example we call the 'work' phase:

.. code-block::

  work_phase = pb.create_phase('Work', [in_buffer_res, out_buffer_res])

We start the work phase using a ``with`` block. On entry, it waits until the
resources are available and in the meantime it monitors the processing block
state. Once the resources are available, it proceeds into the body of the
``with`` block and deploys a Helm chart using the ``ee_deploy_helm`` method.
This happens in a separate thread, so the method returns immediately.
It then enters the loop at the end, which monitors the scheduling block instance
to check if it has been cancelled.

.. code-block::

  with work_phase:
      work_phase.ee_deploy_helm('cbf-sdp-emulator')

      for txn in work_phase.wait_loop():
          if work_phase.is_sbi_finished(txn):
              break
          txn.loop(wait=True)

On exiting the ``with`` block it waits until the scheduling block instance is
finished. When the scheduling block instance state is updated, it
then removes the execution engine and updates the processing block state.
