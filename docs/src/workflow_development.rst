Workflow Development
====================

The steps to develop and test an SDP workflow are as follows:

- Clone the ska-sdp-science-pipelines repository from GitLab and create a new branch for
  your work.

- Create a directory for your workflow in ``src``:

  .. code-block::

    $ mkdir src/<my_workflow>
    $ cd src/<my_workflow>

- Write the workflow script (``<my_workflow>.py``). See the existing workflows
  for examples of how to do this. The examples :ref:`example_realtime` (:ref:`test_realtime`)
  and :ref:`example_batch` (:ref:`test_batch`) are the best place to start. These
  are meant to give you a general idea of what structure batch and realtime workflows should have,
  and help develop your own.

  List of available Helm charts, which can be used for
  workflows, and their documentation can be found at: TBC

- Create a ``requirements.txt`` file with your workflow's Python requirements,
  e.g.

  .. code-block::

    --index-url https://nexus.engageska-portugal.pt/repository/pypi/simple
    --extra-index-url https://pypi.org/simple
    ska-logging
    ska-sdp-workflow

- Create a ``Dockerfile`` for building the workflow image, e.g.

  .. code-block::

    FROM python:3.9

    COPY requirements.txt ./
    RUN pip install -r requirements.txt

    WORKDIR /app
    COPY <my_workflow>.py ./
    ENTRYPOINT ["python", "<my_workflow>.py"]

  Use the base-image of your choice, preferably the latest numbered version of it, e.g. python:3.9.

- Create a file called ``version.txt`` containing the semantic version number of
  the workflow.

- Create a ``Makefile`` containing

  .. code-block::

    NAME := workflow-<my-workflow>
    VERSION := $(shell cat version.txt)

    include ../../make/Makefile

- Build the workflow image:

  .. code-block::

    $ make build
    $ make tag_release

  This will add it to your local Docker daemon where it can be used for testing
  with a local deployment of the SDP.

  For example with a local installation of ``minikube``

  .. code-block::

     $ eval $(minikube -p minikube docker-env)
     $ make build
     $ make tag_release

  This will point Docker towards the ``minikube`` Docker repository and will then build and
  tag the new workflow accordingly.

- `Deploy SDP locally <https://developer.skao.int/projects/ska-sdp-integration/en/latest/running/standalone.html>`_
  and `start a shell in the console pod <https://developer.skao.int/projects/ska-sdp-integration/en/latest/running/standalone.html#connecting-to-the-configuration-database>`_.

- Add the workflow to the configuration DB. This will tell the SDP where to
  find the Docker image to run the workflow:

  .. code-block::

    ska-sdp create workflow <kind>:<name>:<version> '{"image": "<docker-image:version>"}'

  where the values are:

    - ``<kind>``: ``batch`` or ``realtime``, depending on the kind of workflow
    - ``<name>``: name of your workflow
    - ``<version>``: version of your workflow
    - ``<docker-image:version>``: Docker image you just built from your workflow, including its version tag.

  If you have multiple workflows to add, you can import the definitions with:

  .. code-block::

    ska-sdp import some-workflows.json

  An example JSON file for importing workflows can be found at: `Example Workflow JSON
  <https://developer.skao.int/projects/ska-sdp-config/en/latest/cli.html#example-workflow-definitions-file-content-for-import>`_

- To run the workflow, create a processing block, either via the `Tango interface
  <https://developer.skao.int/projects/ska-sdp-integration/en/latest/running/standalone.html#accessing-the-tango-interface>`_,
  or by creating it directly in the configuration DB with `ska-sdp create pb
  <https://developer.skao.int/projects/ska-sdp-config/en/latest/cli.html#usage>`_.

- Once you are happy with the workflow, add it to the GitLab CI file
  (``.gitlab-ci.yml``) in the root of the repository. You need to add a build
  and publish job for it:

  .. code-block::

    build-<my_workflow>:
      extends: .docker_build_workflow
      before_script:
        - cd src/<my_workflow>>
      only:
        changes:
          - src/<my_workflow>/*

    publish-<my_workflow>:
      extends: .publish
      before_script:
        - cd src/<my_workflow>
      only:
        refs:
          - master
        changes:
          - src/<my_workflow>/*

  This will enable the Docker image to be built and pushed to the SKA artefact
  repository when it is merged into the master branch.

- Add the workflow to the workflow definition file ``workflows.json`` in the
  root of the repository. By default the SDP uses this file to populate the
  workflow definitions in the configuration DB when it starts up.

- Create a ``README.md`` and add the description and instructions to run your workflow.
  Include it in the documentation:

    - create a new file in ``docs/src/<my_workflow>.rst``
    - add the following to it:

    .. code-block::

        .. mdinclude:: ../../src/<my_workflow>/README.md

    - update ``docs/src/index.rst``

- Commit the changes to your branch and push to GitLab.
