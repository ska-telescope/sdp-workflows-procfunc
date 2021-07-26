## Test Dask Workflow

The `test_dask` workflow is designed to test deploying two
instances of a Dask execution engine and executing a simple function on each one.

The sequence of actions carried out by the workflow is:

* Claims processing block
* Sets processing block `status` to `'WAITING'`
* Waits for `resources_available` to be `True`
    * This is the signal from the processing controller that the workflow can start
* Sets processing block `status` to `'RUNNING'`
* Deploys two Dask execution engines in parallel
* Does some simple operations. Constructs a graph to add two numbers together and computes
  the result by calling the 'compute' method.
* Sets processing block `status` to `'FINISHED'`

### Changelog

#### 0.2.6

- Use dependencies from the central artefact repository and publish the
  workflow image there.

#### 0.2.5

- Ported to use the latest version of workflow library (0.2.4).

#### 0.2.4

- use python:3.9-slim as the base docker image
- slimmed down the requirements file as well