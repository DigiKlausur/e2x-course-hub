# Course Hub Configuration

At the heart of the E2x Course Hub is the `ServerConfig`.
In this config we define roles, the directory where profiles are stored, where courses are stored and where mounts are defined.

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.schema.server.ServerConfig
   :exclude-members: server_config_file, modification_times, config_changed_on_disk
``` 

## Example Hub Configuration

The following example defines where to find profiles, courses and mounts.
It also defines roles with permissions.
Here we have three roles:

- `student`: Can spawn the student profile
- `grader`: Inherits from `student`. Can spawn the grader profile and add and remove `student` members to / from a course.
- `course_admin`: Inherits from `grader`. Can add and remove all roles to / from a course.

```yaml
profile_dir: "profiles"
course_config_dir: "course_configs"
mount_definitions_file: "mount_definitions.yaml"

roles:
  student:
    priority: 100
    scopes:
      - spawn:profile!profile=student_profile
  grader:
    priority: 200
    scopes:
      - spawn:profile!profile=grader_profile
      - add:course-members!role=student
      - remove:course-members!role=student
  course_admin:
    priority: 300
    scopes:
      - add:course-members
      - remove:course-members
```