# Mount Configuration

This guide explains how to configure mounts for the E2x Course Hub using mount definitions and requests.

## Overview

Mounts are defined in the `mount_definitions_file` configuration. The system uses a two-tier approach:

1. **Mount Definitions** - Global templates that define how storage should be mounted
2. **Mount Requests** - Profile-specific requests that instantiate mount definitions with actual parameters

This separation allows you to define storage mounts once and reuse them across multiple profiles with different parameters. For example, you can define a student home directory mount once, then use it for different courses, terms, and users by providing the appropriate parameters 

## Mount Schema

The base mount schema defines the structure of a mounted volume:

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.schema.mount.Mount
```

## Mount Definitions

Mount definitions are global templates that specify how storage volumes should be mounted. They support parameterization through input variables, making them reusable across different contexts.

### Parameters

Parameters define the inputs that a mount definition accepts:

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.schema.base.Parameter
```

### Mount Definition Schema

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.schema.mount.MountDefinition
```

### Example: Student Home Directory

This example defines a mount for student home directories. It accepts three parameters: `course_id`, `term_id`, and `username`. The mount path and sub-path use template syntax `${{inputs.parameter_name}}` to dynamically substitute parameter values.

```yaml
student_home:
  description: "The home directory for the student."
  name: disk2
  mountPath: "/home/${{inputs.username}}"
  subPath: "homes/teaching/students/${{inputs.course_id}}-${{inputs.term_id}}/${{inputs.username}}"
  readOnly: false  
  inputs:
    course_id:
      type: string
      required: true
    term_id:
      type: string
      required: true
    username:
      type: string
      required: true
```

**Key Points:**
- The `name` field references the persistent volume or disk to use
- Template variables are enclosed in `${{inputs.variable_name}}` syntax
- All required parameters must be provided when requesting this mount
- `readOnly` controls whether the mount is writable


## Mount Requests

Mount requests are used within profile configurations to instantiate mount definitions with specific parameter values. Each request references a mount definition by its ID and provides the required arguments.

### Mount Request Schema

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.schema.mount.MountRequest
```

### Example: Requesting a Student Home Directory

This example shows how to request the `student_home` mount definition defined above, providing concrete values for the required parameters:

```yaml
home:
  id: student_home
  args:
    username: "student1"
    course_id: "Math101"
    term_id: "Winter2026"
```

When processed, this mount request will resolve to:
- **Mount Path:** `/home/student1`
- **Sub-Path:** `homes/teaching/students/Math101-Winter2026/student1`

**Usage in Profiles:**
Mount requests are typically defined in profile configurations where they can access context-specific values like the current user, course, or term.

## Complete Workflow

1. **Define** mount definitions globally in `mount_definitions_file`
2. **Reference** mount definitions in profile configurations using mount requests
3. **Provide** required parameters through the `args` field
4. **Deploy** - the system resolves templates and creates the appropriate volume mounts for each user's environment
