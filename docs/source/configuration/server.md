# Course Hub Configuration

At the heart of the E2x Course Hub is the `ServerConfig`.
In this config we define roles, the directory where profiles are stored, where courses are stored and where mounts are defined.

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.schema.server.ServerConfig
   :exclude-members: server_config_file, modification_times, config_changed_on_disk
``` 

```{literalinclude} ../example/mount_definitions.yaml
:language: yaml
:linenos: