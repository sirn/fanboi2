============================
Docker Compose Configuration
============================

These configuration are intended to help you launch Fanboi2 and all its dependencies on one machine, mainly for development/staging. For a real production deployment, you will want to use container orchestration tools such as Docker Swarm or Kubernetes, which are beyond the scope of this document.

Setting Up
----------

These configuration files assume the following directory structure::

  project_root/
  ├── docker-compose.yml
  ├── docker-compose.override.yml
  └── fanboi2/
      └── <REPOSITORY CONTENT>

1. Create the above directory structure by copying both `yml` files to the same level as the repository directory
2. Edit the content of `docker-compose.yml` and initialize the variables with freshly generated secret tokens
3. Run `docker-compose build && docker-compose up -d` from the context of `project_root` (*not* the repository root)

Disabling Code Reload
---------------------

Removing or renaming `docker-compose.override.yml` to something else will prevent automatic reloading and rebuilding of code, similar to when in production. Don't forget to re-run `docker-compose up -d` when you make any changes.
