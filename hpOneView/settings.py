# -*- coding: utf-8 -*-

"""
settings.py
~~~~~~~~~~~~

This module implements settings HP OneView REST API
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import open
from future import standard_library
standard_library.install_aliases()

__title__ = 'settings'
__version__ = '0.0.1'
__copyright__ = '(C) Copyright (2012-2015) Hewlett Packard Enterprise ' \
                ' Development LP'
__license__ = 'MIT'
__status__ = 'Development'

###
# (C) Copyright (2012-2015) Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
###

from hpOneView.common import *
from hpOneView.connection import *
from hpOneView.activity import *
from hpOneView.exceptions import *


class settings(object):

    def __init__(self, con):
        self._con = con
        self._activity = activity(con)

    ###########################################################################
    # Appliance Firmware
    ###########################################################################
    def upload_fw(self, path, name, verbose=False):
        response, body = self._con.post_multipart(uri['appliance-firmware'],
                                                  '', path, name, verbose)
        if response.status >= 400:
            raise HPOneViewException(body)
        return body

    def get_pending_fw(self):
        body = self._con.get(uri['fw-pending'])
        return body

    def upgrade_appliance_fw(self, filename):
        task, body = self._con.put(uri['fw-pending'] + '?file=' + filename, '')
        return body

    def delete_appliance_fw(self):
        task, body = self._con.delete(uri['fw-pending'])
        return body

    ###########################################################################
    # SPP Upload
    ###########################################################################
    def upload_spp(self, sppPath, sppName, verbose=False, blocking=True):
        response, body = self._con.post_multipart(uri['fwUpload'], '',
                                                  sppPath, sppName, verbose)
        if response.status >= 400:
            raise HPOneViewException(body)
        if response.status == 202 and verbose is True:
            print('Upload complete. Waiting for processing.')
        task, spp = self._activity.make_task_entity_tuple(body)
        if blocking is True:
            task = self._activity.wait4task(task, tout=600, verbose=verbose)
        if verbose is True:
            print('Processing complete.')
        return spp['resourceId']

    def delete_spp(self, sppName):
        task, body = self._con.delete(uri['fwDrivers'] + '/' + sppName)
        return body

    def get_spps(self):
        body = self._con.get(uri['fwDrivers'])
        return get_members(body)

    def get_health_status(self):
        body = self._con.get(uri['healthStatus'])
        return get_members(body)

    def get_version(self):
        body = self._con.get(uri['version'])
        return body

    def generate_support_dump(self, encrypt=True, logicalInterconnect=None):
        request = {}
        if logicalInterconnect is None:
            request['encrypt'] = encrypt
            request['errorCode'] = 'CI'
            task, body = self._con.post(uri['supportDump'], request)
        else:
            request['errorCode'] = 'LI'
            task, body = self._con.post(
                logicalInterconnect['uri'] + '/support-dumps',
                request)
        return body

    def download_support_dump(self, dumpInfo):
        body = self._con.get(dumpInfo['uri'])
        f = open(dumpInfo['uri'].split('/')[-1], 'wb')
        f.write(body)
        f.close()
        return

    def generate_backup(self, blocking=True, verbose=False):
        resp, body = self._con.do_http('POST', uri['backups'], None)
        if resp.status >= 400:
            raise HPOneViewException(body)
        taskuri = resp.getheader('Location')
        task = self._con.get(taskuri)
        if blocking is True:
            task = self._activity.wait4task(task, tout=600, verbose=verbose)
        backupResource = self._activity.get_task_associated_resource(task)
        backup = self._con.get(backupResource['resourceUri'])
        return backup

    def download_backup(self, backup):
        body = self._con.get(backup['downloadUri'])
        f = open(backup['downloadUri'].split('/')[-1] + '.bkp', 'wb')
        f.write(body)
        f.close()
        return

    def upload_backup(self, path, name, verbose=False, blocking=True):
        response, body = self._con.post_multipart(uri['archive'], '',
                                                  path, name, verbose)
        if response.status >= 400:
            raise HPOneViewException(body)
        if response.status == 202 and verbose is True:
            print('Upload complete. Waiting for processing.')
        task, backup = self._activity.make_task_entity_tuple(body)
        if blocking is True:
            task = self._activity.wait4task(task, tout=600, verbose=verbose)
        if verbose is True:
            print('Processing complete.')
        return backup

    def restore_backup(self, backupUri):
        request = {
            'type': 'RESTORE',
            'uriOfBackupToRestore': backupUri}
        task, body = self._con.post(uri['restores'], request)
        return body

    def get_backups(self):
        body = self._con.get(uri['backups'])
        return body

    def get_restores(self):
        body = self._con.get(uri['restores'])
        return body

    def get_dev_read_comm_string(self):
        body = self._con.get(uri['dev-read-community-str'])
        return body['communityString']

    def set_dev_read_comm_string(self, communityString):
        request = {'communityString': communityString}
        task, body = self._con.put(uri['dev-read-community-str'], request)
        return body

    def get_licenses(self):
        body = self._con.get(uri['licenses'])
        return get_members(body)

    def add_license(self, licenseKey):
        request = {
            'key': licenseKey,
            'type': 'License'}
        task, body = self._con.post(uri['licenses'], request)
        return body

    def factory_reset(self, mode='PRESERVE_NETWORK'):
        response = self._con.delete('/rest/appliance?mode=' + mode)
        return response

    def get_node_status(self):
        body = self._con.get(uri['nodestatus'])
        return body

    def get_node_version(self):
        body = self._con.get(uri['nodeversion'])
        return body

    def shutdown(self, mode='HALT'):
        task, body = self._con.post('/rest/appliance/shutdown?type=' + mode,
                                    None)
        return body

    def get_trap_destinations(self):
        body = self._con.get(uri['trap'])
        return body

    def get_serviceaccess(self):
        body = self._con.get(uri['service'])
        return body

    def set_service_access(self, serviceAccess):
        task, body = self._con.put(uri['serviceAccess'], serviceAccess)
        return body

    def get_domains(self):
        body = self._con.get(uri['domains'])
        return body

    def get_schema(self):
        body = self._con.get(uri['schema'])
        return body

    def get_global_settings(self):
        body = self._con.get(uri['globalSettings'])
        return body

    def get_storage_vol_template_policy(self):
        body = self._con.get(uri['vol-tmplate-policy'])
        return body

    def get_startup_progress(self):
        body = self._con.get(uri['progress'])
        return body

    ###########################################################################
    # Appliance Network Interfaces
    ###########################################################################
    def get_appliance_network_interfaces(self):
        return self._con.get(uri['applianceNetworkInterfaces'])

    def set_appliance_network_interface(self, interfaceConfig):
        self._con.post(uri['applianceNetworkInterfaces'], interfaceConfig)
        return

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
