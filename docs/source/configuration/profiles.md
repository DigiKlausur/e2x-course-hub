# Profile Configuration

This guide explains how to configure profiles for the E2x Course Hub. Profiles define the runtime environment and storage mounts for JupyterHub containers.

## Overview

A profile is a configuration template that defines:

1. **Runtime Environment** - Container image, resources, and environment variables
2. **Mount Requests** - Storage volumes to attach (see [Mount Configuration](mounts.md))
3. **Input Parameters** - Dynamic values that can be substituted at spawn time
4. **Inheritance** - Ability to extend other profiles to create variations

Profiles support inheritance, allowing you to define base configurations and create specialized profiles that extend them. This promotes reusability and consistency across different user roles (students, graders, instructors).

## Profile Types

The E2x Course Hub supports two types of profiles:

### Base Profile

A standalone profile that defines a complete configuration. It cannot inherit from other profiles.

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.schema.profile.BaseProfile
```

### Inherited Profile

A profile that extends a base profile or another inherited profile. It can override or extend any configuration from its parent.

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.schema.profile.InheritedProfile
```

## Profile Components

### Input Parameters

Input parameters define the dynamic values that a profile accepts. These are used for template substitution in runtime environment variables and mount requests.

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.schema.base.Parameter
   :no-index:
```

Parameters can be referenced in configuration values using the template syntax: `${{inputs.parameter_name}}`

### Runtime Configuration

The runtime defines the container environment. See [Runtime Configuration](runtime.md) for detailed documentation.

### Mount Requests

Mount requests specify which storage volumes to attach to the container. Each request references a mount definition and provides the required arguments. See [Mount Configuration](mounts.md) for details.

**Regular mounts** are attached for all users, while **admin mounts** are only attached when the user has admin privileges.

## Examples

### Example 1: Base Profile

This example shows a minimal base profile with essential runtime settings and an admin-only mount:

```yaml
name: base_profile
display_name: "Base"
inputs:
  username:
    required: true
    type: string
runtime:
  image:
    name: ghcr.io/digiklausur/docker-stacks/minimal-notebook
    tag: latest
    pullPolicy: IfNotPresent
  resources:
    cpu_guarantee: 0.001
    cpu_limit: 2.0
    mem_guarantee: 1.0G
    mem_limit: 2.0G
  environment:
    NB_USER: "${{inputs.username}}"
    CHOWN_HOME: "no"
    NB_GID: 1000
    NB_UID: 1000
admin_mount_requests:
  jupyterhub_config_mount:
    id: course_config
    args: {}
```

**Key Points:**
- Defines a single required parameter: `username`
- Uses a minimal notebook image
- Sets resource limits for CPU and memory
- Configures environment variables with template substitution
- Includes an admin-only mount for course configuration

### Example 2: Student Profile (Inherited)

This profile inherits from the base profile and adds student-specific configuration:

```yaml
name: student_profile
inherits: base_profile
display_name: "Student Profile"
description: "The base student profile using a file based exchange."
inputs:
  username:
    required: true
    type: string
  course_id:
    required: true
    type: string
  term_id:
    required: true
    type: string
runtime:
  image:
    name: ghcr.io/digiklausur/docker-stacks/datascience-notebook-student
    tag: staging
    pullPolicy: IfNotPresent
  environment:
    NBGRADER_COURSE_ID: "${{inputs.course_id}}-${{inputs.term_id}}"
mount_requests:
  home:
    id: student_home
    args:
      username: "${{inputs.username}}"
      course_id: "${{inputs.course_id}}"
      term_id: "${{inputs.term_id}}"
  personalized_feedback:
    id: nbgrader_exchange_mount
    args:
      course_id: "${{inputs.course_id}}"
      term_id: "${{inputs.term_id}}"
      step: "personalized-feedback/${{inputs.username}}"
  personalized_inbound:
    id: nbgrader_exchange_mount
    args:
      course_id: "${{inputs.course_id}}"
      term_id: "${{inputs.term_id}}"
      step: "personalized-inbound/${{inputs.username}}"
      readonly: false
  outbound:
    id: nbgrader_exchange_mount
    args:
      course_id: "${{inputs.course_id}}"
      term_id: "${{inputs.term_id}}"
      step: "outbound"
```

**Key Points:**
- Inherits base configuration from `base_profile`
- Adds course-specific parameters: `course_id` and `term_id`
- Overrides the container image to use a student-specific image
- Adds environment variables for nbgrader integration
- Defines multiple mount requests for home directory and nbgrader exchange

**Inheritance Behavior:**
- Runtime settings are merged (image overrides base, resources inherited)
- Environment variables are merged (new ones added, existing ones can be overridden)
- Mount requests from the base profile are inherited (admin mounts still available)
- All input parameters must be defined (even if inherited)

### Example 3: Grader Profile (Inherited)

This profile is designed for instructors and graders with higher resource limits:

```yaml
name: grader_profile
inherits: base_profile
display_name: "Grader Profile"
description: "The base grader profile using a file based exchange."
inputs:
  username:
    required: true
    type: string
  course_id:
    required: true
    type: string
  term_id:
    required: true
    type: string
runtime:
  image:
    name: ghcr.io/digiklausur/docker-stacks/datascience-notebook-teacher
    tag: staging
    pullPolicy: IfNotPresent
  resources:
    cpu_guarantee: 0.001
    cpu_limit: 4.0
    mem_guarantee: 1.0G
    mem_limit: 8.0G
  environment:
    NBGRADER_COURSE_ID: "${{inputs.course_id}}-${{inputs.term_id}}"
    NBGRADER_COURSE_DIR: "~/courses/${{inputs.course_id}}/${{inputs.course_id}}-${{inputs.term_id}}"
    CHOWN_HOME: "no"
    NB_GID: 2000
    NB_UID: 2000
mount_requests:
  home:
    id: grader_home
    args:
      username: "${{inputs.username}}"
  grader_course_directory:
    id: course
    args:
      username: "${{inputs.username}}"
      course_id: "${{inputs.course_id}}"
  grader_writable_exchange:
    id: nbgrader_exchange_mount
    args:
      course_id: "${{inputs.course_id}}"
      term_id: "${{inputs.term_id}}"
      step: ""
      readonly: false
```

**Key Points:**
- Inherits from the same base profile as student profile
- Uses a teacher-specific container image
- Increases resource limits (4 CPUs, 8GB memory)
- Sets different UID/GID for grader permissions
- Mounts grader-specific directories including course materials
- Has write access to the nbgrader exchange

## Profile Resolution

When a user spawns a container, the system resolves the profile through the following steps:

1. **Inheritance Resolution** - If the profile inherits from another, recursively merge parent configurations
2. **Parameter Validation** - Ensure all required input parameters are provided
3. **Template Substitution** - Replace all `${{inputs.parameter_name}}` placeholders with actual values
4. **Mount Resolution** - Resolve mount requests using mount definitions to create actual mount configurations
5. **Admin Mount Handling** - Include admin mounts only if the user has admin privileges

The result is a `ResolvedProfile` ready for container spawning:

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.schema.profile.ResolvedProfile
```

## Best Practices

### Profile Organization

- **Create a base profile** with common settings (image, basic resources, environment)
- **Inherit for roles** (student, grader, instructor) rather than duplicating configuration
- **Use descriptive names** that clearly indicate the profile's purpose

### Parameter Design

- **Define parameters in base profiles** when they're used across multiple child profiles
- **Use consistent parameter names** (e.g., `course_id`, `term_id`, `username`)
- **Mark parameters as required** when they're essential for the profile to function

### Resource Allocation

- **Set appropriate limits** based on workload (students typically need less than graders)
- **Use guarantees** to ensure minimum resources are available
- **Test resource settings** under load to avoid over-allocation

### Mount Configuration

- **Reference mount definitions** rather than hardcoding paths
- **Use template substitution** for dynamic paths based on user/course context
- **Separate admin mounts** from regular mounts for security

### Template Syntax

- Always use the format: `${{inputs.parameter_name}}`
- Ensure parameter names match those defined in the `inputs` section
- Test template substitution with actual values before deployment

## Complete Workflow

1. **Define mount definitions** in `mount_definitions_file` (see [Mount Configuration](mounts.md))
2. **Create a base profile** with common runtime and environment settings
3. **Create inherited profiles** for different user roles (student, grader, etc.)
4. **Configure profile inputs** that will be provided at spawn time
5. **Add mount requests** referencing your mount definitions
6. **Deploy** - users select profiles when spawning their containers

