# Course Configuration

This guide explains how to configure courses in the E2x Course Hub. Courses define metadata, active terms, profile availability, and optional runtime overrides.

## Overview

A course configuration allows you to:

1. **Define Course Metadata** - Course ID, name, and description
2. **Organize by Terms** - Separate configurations for different semesters/sessions
3. **Control Profile Access** - Specify which profiles are available per term
4. **Customize Runtime Settings** - Override profile configurations at the course or term level

Course configurations are stored as YAML files in the directory specified by the `course_configs_dir` setting.

## Course Configuration Schema

### Course Metadata

Course metadata provides basic information about the course:

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.schema.course.CourseMetadata
```

### Term Configuration

Each term within a course has its own configuration:

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.schema.course.TermConfig
```

### Course Configuration

The complete course configuration combines metadata, terms, and optional overrides:

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.schema.course.CourseConfig
```

### Course Model

The resolved course model used internally by the system:

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.schema.course.Course
```

## Configuration Components

### Metadata Section

The metadata section identifies and describes the course:

- **course_id**: Unique identifier for the course (used in paths, database references, etc.)
- **course_name**: Human-readable full name of the course
- **description**: Optional detailed description

### Terms Section

The terms section defines active teaching periods (semesters, sessions, etc.):

- Each term has a unique key (e.g., `WS25`, `SS25`)
- Contains an `allowed_profiles` list specifying which profiles students/instructors can use
- Can include term-specific `profile_runtime_overrides`

### Profile Runtime Overrides

Runtime overrides allow you to customize profile settings without modifying the base profile definitions. Overrides can be applied at:

1. **Course Level** - Affects all terms in the course
2. **Term Level** - Affects only a specific term

See [Runtime Configuration](runtime.md) for details on runtime settings. Common use cases include:
- Using course-specific container images
- Adjusting resource limits for demanding courses
- Setting course-specific environment variables

## Examples

### Example 1: Basic Course Configuration

A simple course with two terms and standard profiles:

```yaml
metadata:
  course_id: Math101
  course_name: Mathematics
  description: "An introductory course to Mathematics."
terms:
  SS25:
    allowed_profiles:
    - grader_profile
    - student_profile
  WS25:
    allowed_profiles:
    - grader_profile
    - student_profile
```

**Key Points:**
- Defines metadata for course identification
- Two active terms: SS25 (Summer Semester 2025) and WS25 (Winter Semester 2025)
- Both terms allow the same two profiles: student and grader
- No runtime overrides - uses default profile configurations

### Example 2: Course with Runtime Overrides

A Machine Learning course that uses specialized container images:

```yaml
metadata:
  course_id: ML101
  course_name: "Machine Learning"
  description: "An introductory course to Machine Learning."
profile_runtime_overrides:
  grader_profile:
    image:
      name: ghcr.io/digiklausur/docker-stacks/ml-notebook-teacher
  student_profile:
    image:
      name: ghcr.io/digiklausur/docker-stacks/ml-notebook-student
terms:
  WS25:
    allowed_profiles:
    - grader_profile
    - student_profile
```

**Key Points:**
- Course-level runtime overrides apply to all terms
- Overrides the container image for both profiles
- Student profile gets ML-specific student image with required libraries
- Grader profile gets ML-specific teacher image with additional tools
- All other profile settings (resources, mounts, environment) remain unchanged

### Example 3: Term-Specific Overrides

A course with different resource allocations per term:

```yaml
metadata:
  course_id: DataScience101
  course_name: "Data Science Fundamentals"
  description: "Introduction to data science with Python and R."
terms:
  SS25:
    allowed_profiles:
    - student_profile
    - grader_profile
  WS25:
    allowed_profiles:
    - student_profile
    - grader_profile
    profile_runtime_overrides:
      student_profile:
        resources:
          cpu_limit: 4.0
          mem_limit: 8.0G
        environment:
          ENABLE_GPU: "true"
      grader_profile:
        resources:
          cpu_limit: 8.0
          mem_limit: 16.0G
```

**Key Points:**
- SS25 uses default profile configurations
- WS25 includes term-specific overrides with higher resource limits
- Useful when different terms have different computational requirements
- Can enable features (like GPU access) for specific terms

### Example 4: Limiting Profile Availability

A course that restricts certain profiles to specific terms:

```yaml
metadata:
  course_id: AdvancedML201
  course_name: "Advanced Machine Learning"
  description: "Advanced topics in machine learning and deep learning."
profile_runtime_overrides:
  student_profile:
    image:
      name: ghcr.io/digiklausur/docker-stacks/ml-notebook-student
      tag: advanced
  grader_profile:
    image:
      name: ghcr.io/digiklausur/docker-stacks/ml-notebook-teacher
      tag: advanced
  research_profile:
    image:
      name: ghcr.io/digiklausur/docker-stacks/ml-notebook-research
terms:
  SS25:
    allowed_profiles:
    - student_profile
    - grader_profile
  WS25:
    allowed_profiles:
    - student_profile
    - grader_profile
    - research_profile
```

**Key Points:**
- Research profile only available in WS25 term
- All profiles use advanced image tags with latest features
- Allows controlled rollout of new profiles
- Useful for pilot programs or advanced sections

## Runtime Override Behavior

When runtime overrides are applied, they follow a merge hierarchy:

1. **Base Profile** - Defined in the profiles configuration
2. **Course Override** - Applied to all terms in the course
3. **Term Override** - Applied only to the specific term

Later overrides take precedence and are merged with earlier configurations. The merge behavior:

- **Image settings** - Completely replaced if overridden
- **Resources** - Individual limits can be overridden (e.g., only `cpu_limit`)
- **Environment variables** - Merged (new variables added, existing can be overridden)
- **Mounts** - Not typically overridden in course configs

## Course Resolution Process

When a user spawns a container, the system resolves the configuration:

1. **Load server profiles** - Read base profile definitions
2. **Apply course overrides** - Merge course-level runtime overrides
3. **Apply term overrides** - Merge term-specific runtime overrides
4. **Filter allowed profiles** - Show only profiles listed in `allowed_profiles`
5. **Present to user** - User selects from available profiles
6. **Resolve profile** - Apply parameter substitution and mount resolution (see [Profile Configuration](profiles.md))

## Best Practices

### Course Organization

- **Use meaningful course IDs** that match your institution's course codes
- **Keep descriptions concise** but informative for students
- **Organize terms consistently** (e.g., WS25, SS26) for easy sorting

### Profile Management

- **Define base profiles once** at the server level
- **Use runtime overrides sparingly** - only when truly course-specific
- **Document why overrides exist** in comments within the YAML file
- **Test overrides** before deploying to production

### Term Configuration

- **Create terms as needed** - don't pre-create future terms unnecessarily
- **Review allowed_profiles** - ensure they match the term's teaching needs
- **Archive old terms** - move configurations for completed terms to a separate directory

### Resource Overrides

- **Monitor actual usage** before increasing limits
- **Be conservative** - over-allocation wastes cluster resources
- **Consider time of day** - high-usage courses may need different limits
- **Document resource decisions** - note why specific courses need more resources

### Image Overrides

- **Use tags appropriately** - `latest` for development, specific versions for production
- **Test new images** before applying to active courses
- **Maintain consistency** - avoid too many different image variations
- **Document requirements** - note what libraries/tools are needed

## File Naming and Location

Course configuration files should be:

- **Located** in the directory specified by `course_configs_dir` setting
- **Named** using the course ID (e.g., `math101.yaml`, `ml-101.yaml`)
- **Formatted** as valid YAML with consistent indentation
- **Version controlled** to track changes over time

## Integration with Profiles

Courses work together with profiles to provide a complete configuration:

1. **Profiles** define the container environment, resources, and mounts (see [Profile Configuration](profiles.md))
2. **Courses** select which profiles are available and customize them as needed
3. **Users** select from available profiles when spawning their environment
4. **System** resolves the complete configuration and launches the container

## Complete Workflow

1. **Define server-wide profiles** with common configurations
2. **Create course configuration files** in the `course_configs_dir`
3. **Specify metadata** for course identification
4. **Add terms** with allowed profiles for each teaching period
5. **Apply runtime overrides** if course-specific customization is needed
6. **Deploy** - the Course Hub automatically discovers and loads course configurations
7. **Monitor** - review resource usage and adjust overrides as needed

