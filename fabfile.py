# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import raven
import os

from fabric.api import local, run, hosts, env, sudo, settings, abort, lcd
from fabric.colors import green, red, yellow
from fabric.contrib.console import confirm

from ci import dev, omega, prod


GIT_SHA = raven.fetch_git_sha(os.path.dirname(os.pardir))

def prepare_deploy(tag=None):
    if not tag:
        tags = local('git tag', capture=True)
        if tags:
            parts = tags.splitlines().pop().split('.')
            sub_version = int(parts.pop()) + 1
            tag = '{}.{}.{}'.format(parts[0], parts[1], sub_version)
        else:
            tag = 'v1.0.0'

    print(green('Tagging release as {}'.format(tag)))
    with settings(warn_only=True):
        result = local('git tag {}'.format(tag), capture=True)
    if result.failed and not confirm("Git tag failed. Continue?"):
        abort("Aborting at user request.")
    local('git push origin --tags')
    local('python manage.py runserver localhost:8000 &')
    local('python manage.py collectstatic --settings=myproject.settings.deploy --no-input')
    local('pkill python manage.py runserver')
    local('docker build -t myproject . -f ci/Dockerfile')
    local('docker tag myproject us.gcr.io/myproject-183417/myproject:{}'.format(tag))
    local('gcloud docker -- push us.gcr.io/myproject-183417/myproject:{}'.format(tag))
    return tag

def deploy(tag=None):
    print(yellow('Starting deploy...'))
    tag = prepare_deploy(tag)
    local('/bin/bash ci/set_env_variables.sh')
    local('python manage.py migrate --settings=myproject.settings.prod')
    
    # Compressing and uploading files
    local("""gsutil -m \
        -h "Cache-Control:public, max-age=315360000" \
        cp -r -z js,css,html,png,jpg,jpeg -a public-read \
        assets/{} \
        gs://myproject-cdn-testing/{}""".format(GIT_SHA, GIT_SHA))
    dev.deploy(tag)
    print(green('deploy successful of tag {}'.format(tag)))
