import os
from textwrap import dedent

from docker.types import Mount, DriverConfig

from traitlets import HasTraits, Unicode

from dockerspawner import SwarmSpawner


class VolumeSwarmSpawner(SwarmSpawner):

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
                    read_only=vol["mode"] == "ro",
                    driver_config=self.mount_driver_config_for_volume(volume_name),
                )
                for volume_name, vol in binds
            ]
        else:
            return []

