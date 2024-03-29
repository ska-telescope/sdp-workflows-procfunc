## Test Batch Workflow

The `test_batch` workflow is designed to test the processing
controller logic concerning processing block dependencies.

The sequence of actions carried out by the workflow is:

* Claims processing block
* Reads value of `duration` parameter (type: float, units: seconds) from processing block
* Sets processing block `status` to `'WAITING'`
* Waits for `resources_available` to be `True`
    * This is the signal from the processing controller that the workflow can start
* Sets processing block `status` to `'RUNNING'`
* Does some "processing" (i.e. sleeps) for the requested duration
* Sets processing block `status` to `'FINISHED'`

The workflow makes no deployments.

### Changelog

#### 0.2.5

- Use dependencies from the central artefact repository and publish the
  workflow image there.

#### 0.2.4

- Ported to use the latest version of workflow library (0.2.4).

#### 0.2.3

- use python:3.9-slim as the base docker image
