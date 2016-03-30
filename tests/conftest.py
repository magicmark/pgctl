# -*- coding: utf-8 -*-
# pylint:disable=redefined-outer-name,unused-argument
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os

from py._path.local import LocalPath as Path
from pytest import yield_fixture as fixture
from testing import copy_example


@fixture
def in_example_dir(tmpdir, homedir, service_name):
    os.environ['HOME'] = homedir.strpath
    os.environ.pop('XDG_RUNTIME_DIR', None)

    example_dir = copy_example(service_name, tmpdir)

    with example_dir.as_cwd():
        try:
            yield example_dir
        finally:
            #  pytest does a chdir before calling cleanup handlers
            with example_dir.as_cwd():
                # XXX: this is imported here so the blanking of
                # XDG_RUNTIME_DIR above affects this call
                from pgctl.cli import PgctlApp
                PgctlApp().stop()


@fixture
def scratch_dir(pghome_dir, service_name, in_example_dir):
    yield pghome_dir.join(Path().join('playground', service_name).relto(str('/')), abs=1)


@fixture
def pghome_dir(homedir):
    yield homedir.join('.run', 'pgctl')


@fixture
def homedir(tmpdir):
    yield tmpdir.join('home')


@fixture
def service_name():
    # this fixture will be overridden by some tests
    yield 'sleep'


@fixture(autouse=True)
def disinherit_pytest_pipe():
    """
    pytest creates some weird pipe on fd3 when running under xdist
    this prevents tests from ending due to subprocesses

    Solution: disinherit the pipe.
    """
    from pgctl.flock import set_fd_inheritable
    try:
        set_fd_inheritable(3, False)
    except IOError as error:  # this only happens under single-process pytest  :pragma:nocover:
        if error.errno == 9:  # no such fd
            pass
        else:
            raise
    yield


@fixture(autouse=True)
def wait4(tmpdir):
    """wait for all subprocesses to finish."""
    lock = tmpdir.join('pytest-subprocesses.lock')
    try:
        from pgctl.flock import flock
        with flock(lock.strpath):
            yield
    finally:
        from pgctl.fuser import fuser
        from pgctl.functions import ps
        fusers = True
        i = 0
        while fusers and i < 10:
            fusers = tuple(fuser(lock.strpath))
            i += 1  # we only hit this when tests are broken. pragma: no cover
        fusers = ps(fusers)
        if fusers:
            raise AssertionError("there's a subprocess that's still running:\n%s" % ps(fusers))
