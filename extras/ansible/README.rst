My Ansible playbook manual
==========================

How it works
------------

Requirements
************

- One or serveral server with SSH accessible root user
- Ansible version <= 1.9.1

Roles
*****

All services has been splitted into ansible's roles as following:

- common
- database
- cache
- middleware
- frontend

Inventory
*********

It gathers hosts by IP and roles. It is used for declare host-specific
variables like ``mysql_bind_addr`` for set in configuration and have the value
available from other hosts.

An example of inventory file present at ``./hosts.example``, it is a single
host example. For a multi-hosts example see below:

.. code::

    [database]
    192.168.0.1 mysql_bind_addr=192.168.0.1

    [cache]
    192.168.0.2 redis_bind_addr=192.168.0.2

    [middleware]
    192.168.0.3 uwsgi_bind_addr=192.168.0.3

    [frontend]
    192.168.0.4

Variables
*********

Variables which must be set by user is in ``vars.yml``. See below their
descriptions.

ssh_public_key_file
    Your SSH private key to add to ``~/.ssh/authorized_keys``
myblog_version
    myblog version as git commit, branch or tag
static_root
    Static file root address on middleware hosts
root_db_password
    Database root user's password
db_password
    Database myblog user's password
secret_key
    Django secret key
ssl_cert
    SSL certificate's address on launcher, will be copied to frontend
ssl_key
    SSL key's address on launcher, will be copied to frontend
env
    Wanted environment: prod or testing


Instructions
------------

#. From repo's root, ``cd extras/ansible``
#. ``cp hosts{.example,}`` and edit ``hosts``
#. ``cp vars.yml{.example,}`` and edit ``vars.yml`` for contain great variables.
#. Run playbook with following command:
   ``ansible-playbook main.yml -i hosts -u root``

.. image:: ../../docs/_static/dat_ansible.jpg
