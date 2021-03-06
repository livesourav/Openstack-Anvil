# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Copyright (C) 2012 Yahoo! Inc. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from anvil import log as logging
from anvil import shell as sh
from anvil import utils

import json

from contextlib import contextmanager

LOG = logging.getLogger(__name__)


class PhaseRecorder(object):
    def __init__(self, fn):
        self.fn = fn

    @contextmanager
    def mark(self, phasename):
        contents = dict()
        contents['name'] = phasename
        contents['when'] = utils.iso8601()
        yield phasename
        LOG.debug("Marking the completion of phase %r in file %r", phasename, self.fn)
        lines = [json.dumps(contents), '']
        sh.append_file(self.fn, utils.joinlinesep(*lines))

    def __contains__(self, phasename):
        phases = self.list_phases()
        if phasename in phases:
            return True
        return False

    def list_phases(self):
        phases = set()
        if not sh.isfile(self.fn):
            return phases
        for i, line in enumerate(sh.load_file(self.fn).splitlines()):
            line = line.strip()
            if line:
                data = json.loads(line)
                if not isinstance(data, dict):
                    raise TypeError("Unknown phase entry in %s on line %s" % (self.fn, i + 1))
                if 'name' in data:
                    phases.add(data['name'])
        return phases


class NullPhaseRecorder(PhaseRecorder):
    def __init__(self):
        PhaseRecorder.__init__(self, None)

    @contextmanager
    def mark(self, phasename):
        yield phasename

    def list_phases(self):
        return set()
