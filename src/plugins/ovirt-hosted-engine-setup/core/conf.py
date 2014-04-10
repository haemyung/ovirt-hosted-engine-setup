#
# ovirt-hosted-engine-setup -- ovirt hosted engine setup
# Copyright (C) 2013-2014 Red Hat, Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#


"""Core plugin."""


import gettext


from otopi import constants as otopicons
from otopi import util
from otopi import plugin
from otopi import transaction
from otopi import filetransaction


from ovirt_hosted_engine_setup import constants as ohostedcons
from ovirt_hosted_engine_setup import util as ohostedutil


_ = lambda m: gettext.dgettext(message=m, domain='ovirt-hosted-engine-setup')


@util.export
class Plugin(plugin.PluginBase):
    """Misc plugin."""

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        after=(
            ohostedcons.Stages.VM_IMAGE_AVAILABLE,
            ohostedcons.Stages.BRIDGE_AVAILABLE,
        ),
        name=ohostedcons.Stages.SAVE_CONFIG,
    )
    def _misc(self):
        # TODO: what's an VM_DISK_ID and how can it change to another value?
        self.logger.info(_('Updating hosted-engine configuration'))

        content = ohostedutil.processTemplate(
            template=ohostedcons.FileLocations.OVIRT_HOSTED_ENGINE_TEMPLATE,
            subst={
                '@FQDN@': self.environment[
                    ohostedcons.NetworkEnv.OVIRT_HOSTED_ENGINE_FQDN
                ],
                '@VM_DISK_ID@': self.environment[
                    ohostedcons.StorageEnv.IMG_UUID
                ],
                '@SHARED_STORAGE@': self.environment[
                    ohostedcons.StorageEnv.STORAGE_DOMAIN_CONNECTION
                ],
                '@CONSOLE_TYPE@': self.environment[
                    ohostedcons.VMEnv.CONSOLE_TYPE
                ],
                '@VM_UUID@': self.environment[
                    ohostedcons.VMEnv.VM_UUID
                ],
                '@CONF_FILE@': ohostedcons.FileLocations.ENGINE_VM_CONF,
                '@HOST_ID@': self.environment[ohostedcons.StorageEnv.HOST_ID],
                '@DOMAIN_TYPE@': self.environment[
                    ohostedcons.StorageEnv.DOMAIN_TYPE
                ],
                '@SP_UUID@': self.environment[ohostedcons.StorageEnv.SP_UUID],
                '@SD_UUID@': self.environment[ohostedcons.StorageEnv.SD_UUID],
                '@CONNECTION_UUID@': self.environment[
                    ohostedcons.StorageEnv.CONNECTION_UUID
                ],
                '@CA_CERT@': ohostedcons.FileLocations.LIBVIRT_SPICE_CA_CERT,
                '@CA_SUBJECT@': self.environment[
                    ohostedcons.VDSMEnv.SPICE_SUBJECT
                ],
                '@VDSM_USE_SSL@': str(
                    self.environment[ohostedcons.VDSMEnv.USE_SSL]
                ).lower(),
                '@GATEWAY@': self.environment[ohostedcons.NetworkEnv.GATEWAY],
                '@BRIDGE@': self.environment[
                    ohostedcons.NetworkEnv.BRIDGE_NAME
                ],
            }
        )
        with transaction.Transaction() as localtransaction:
            localtransaction.append(
                filetransaction.FileTransaction(
                    name=(
                        ohostedcons.FileLocations.
                        OVIRT_HOSTED_ENGINE_SETUP_CONF
                    ),
                    content=content,
                    modifiedList=self.environment[
                        otopicons.CoreEnv.MODIFIED_FILES
                    ],
                ),
            )


# vim: expandtab tabstop=4 shiftwidth=4
