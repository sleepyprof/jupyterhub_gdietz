import os
from textwrap import dedent

from docker.types import Mount, DriverConfig

from traitlets import Dict, Unicode

from dockerspawner import SwarmSpawner


class VolumeSwarmSpawner(SwarmSpawner):

    non_admin_read_only_volumes = Dict(
        config=True,
        help=dedent(
            """
            Map from host file/directory to container file/directory.
            Volumes specified here will be read-only in the container for non-admins
            and writable for admins.
            If format_volume_name is not set,
            default_format_volume_name is used for naming volumes.
            In this case, if you use {username} in either the host or guest
            file/directory path, it will be replaced with the current
            user's name.
            """
        ),
    )

    hub_volume_local_path = Unicode(
        config=True,
        help=dedent(
            """
            Local path for creating volume directories.
            If you use {volume_name}, it will be replaced by the name of the volume.
            Use this when mounting a volume into the hub where you want to create subdirectories for different users.
            These subdirectories can then be mounted into the single user containers.
            """
        ),
    )

    @property
    def volume_binds(self):
        binds = super().volume_binds
        return self._volumes_to_binds(self.non_admin_read_only_volumes, binds, mode="non-admin-ro")

    def hub_volume_local_path_for_volume(self, volume_name):
        return self.hub_volume_local_path.format(volume_name=volume_name)
    
    def volume_driver_options_for_volume_name(self, volume_name):
        return {
            key: value.format(volume_name=volume_name) 
            for key, value in self.volume_driver_options.items()
        }

    def mount_driver_config_for_volume(self, volume_name):
        return DriverConfig(
            name=self.volume_driver, options=self.volume_driver_options_for_volume_name(volume_name) or None
        )

    def volume_mode_read_only(self, vol_mode):
        return vol_mode == "ro" or ((not self.user.admin) and vol_mode == "non-admin-ro")

    @property
    def mounts(self):
        if len(self.volume_binds):
            binds = self.volume_binds.items()
            if self.hub_volume_local_path:
                for volume_name, vol in binds:
                    local_volume_dir = self.hub_volume_local_path_for_volume(volume_name)
                    if not os.path.exists(local_volume_dir):
                        self.log.info("Creating local mount directory: {}".format(local_volume_dir))
                        os.mkdir(local_volume_dir)
            return [
                Mount(
                    target=vol["bind"],
                    source=volume_name,
                    type="volume",
                    read_only=self.volume_mode_read_only(vol["mode"]),
                    driver_config=self.mount_driver_config_for_volume(volume_name),
                )
                for volume_name, vol in binds
            ]
        else:
            return []

