Build a custom execution engine
===============================

Note, this section is OUTDATED!

If you want to use a custom execution engine (EE) in your workflow, the
additional steps you need to do are:

- Create a directory in ``src`` for your EE.

- Add the EE code.

- Build the EE Docker image(s) and push it/them to the Nexus repository.

- Add a Helm chart to deploy the EE containers in ``src/helm_deploy/charts``.

- Add the custom EE deployment to the workflow script.

- Commit changes to your branch and push to GitLab.

- When testing, you also need to point the Helm deployer to your branch of the
  repository:

  .. code-block::

    $ helm install sdp-prototype -n sdp-prototype \
      --set processing_controller.workflows.url=https://gitlab.com/ska-telescope/sdp-prototype/raw/<my-branch>/src/workflows/workflows.json \
      --set helm_deploy.chart_repo.ref=<my-branch>
