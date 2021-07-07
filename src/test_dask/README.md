## Test Dask Workflow

The `test_dask` workflow is designed to test deploying two 
instance of Dask execution engine and execute a simple function. 

The sequence of actions carried out by the workflow is:

* Claims processing block
* Sets processing block `status` to `'WAITING'`
* Waits for `resources_available` to be `True`
    * This is the signal from the processing controller that the workflow can start
* Sets processing block `status` to `'RUNNING'`
* Deploys two dask deployments in parallel
    * This is just a first step. Demonstrates scalability and run multiple instances.
* Does a simple operations. Adds two numbers together, constructs the graph and computes
  the result by calling the 'compute' method.
* Sets processing block `status` to `'FINISHED'`

### Changelog

#### 0.2.5

- Ported to use the latest version of workflow library (0.2.4).

#### 0.2.4

- use python:3.9-slim as the base docker image
- slimmed down the requirements file as well