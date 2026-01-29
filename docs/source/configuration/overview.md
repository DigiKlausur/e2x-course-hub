# E2x Course Hub Configuration

The E2x Course Hub provides a flexible, hierarchical configuration system for managing JupyterHub environments across multiple courses, terms, and user roles. This guide introduces the key concepts and how they work together.

## Introduction

The E2x Course Hub is designed to support educational institutions running JupyterHub for teaching and research. It addresses common challenges:

- **Multi-Course Management** - Run multiple courses with different configurations on a single JupyterHub instance
- **Role-Based Access Control** - Define fine-grained permissions for students, graders, and administrators
- **Role-Based Environments** - Provide different container environments based on user roles
- **Term Organization** - Manage configurations across semesters or teaching periods
- **Storage Management** - Configure course materials, student workspaces, and shared resources
- **Resource Control** - Set appropriate CPU and memory limits based on course requirements
- **Configuration Reuse** - Define common settings once and inherit them across profiles

Roles are based on JupyterHub Groups. Course groups are defined as `<course_id>.<term_id>.<role_id>`.
If a user is a member of the group `Math101.Winter2026.student`, they have all permissions of the `student` role within the course `Math101` in the specific semester / term `Winter2026`.

## Architecture Overview

The configuration system consists of six main components that work together:

```
┌─────────────────────────────────────────────────────────────┐
│                      Server Config                          │
│  - Global settings                                          │
│  - Role definitions                                         │
│  - File paths                                               │
└────────────┬────────────────────────────────────────────────┘
             │
             ├────────────┬───────────────┬───────────────┬────────────┐
             ▼            ▼               ▼               ▼            ▼
       ┌─────────┐  ┌──────────┐   ┌──────────┐   ┌──────────┐  ┌──────────┐
       │  Roles  │  │ Profiles │   │ Courses  │   │  Mounts  │  │ Runtime  │
       └─────────┘  └──────────┘   └──────────┘   └──────────┘  └──────────┘
```

### 1. Server Configuration

The [Server Configuration](server.md) is the root configuration that defines:
- Where to find profile, course, and mount definition files
- Role definitions and permissions
- Global settings

**Key Point**: The server config is the entry point that connects all other components.

### 2. Roles and Permissions

[Roles](roles.md) define access control and authorization:
- **Role Definitions** - Named roles with permissions and priority levels
- **Permissions** - Fine-grained actions on resources with optional constraints
- **Priority Hierarchy** - Higher priority roles inherit lower priority permissions
- **Permission Expansion** - Automatic inclusion of implied permissions (subscopes)

**Example Hierarchy**:
```
Priority  Role            Can Do
  100     student         Spawn student profile, view course
  200     grader          + Spawn grader profile, manage students
  300     course_admin    + Manage all members, full access
```

### 3. Mount Configuration

[Mounts](mounts.md) define how storage volumes are attached to containers:
- **Mount Definitions** - Global templates for storage volumes (defined once)
- **Mount Requests** - Profile-specific requests that instantiate definitions with parameters

**Example Flow**:
```
Mount Definition (student_home) 
    ↓ accepts parameters: username, course_id, term_id
Profile requests mount
    ↓ provides: username="alice", course_id="Math101", term_id="WS25"
Resolved Mount
    ↓ /home/alice → disk2/homes/teaching/students/Math101-WS25/alice
```

### 4. Runtime Configuration

[Runtime](runtime.md) settings define the container environment:
- **Container Image** - Which Docker image to use
- **Resources** - CPU and memory limits/guarantees
- **Environment Variables** - Environment configuration for the container

**Key Point**: Runtime settings can be defined in profiles and overridden at course/term levels.

### 5. Profile Configuration

[Profiles](profiles.md) define complete user environments:
- **Runtime** - Container image, resources, environment variables
- **Mount Requests** - Which storage volumes to attach
- **Input Parameters** - Dynamic values for template substitution
- **Inheritance** - Profiles can extend other profiles

**Example Hierarchy**:
```
base_profile (common settings)
    ├─ student_profile (student-specific image, mounts)
    └─ grader_profile (grader-specific image, higher resources)
```

### 6. Course Configuration

[Courses](course.md) organize environments by course and term:
- **Course Metadata** - Course ID, name, description
- **Terms** - Active semesters/sessions
- **Allowed Profiles** - Which profiles are available per term
- **Runtime Overrides** - Course-specific customizations

**Example Structure**:
```
Math101 Course
    ├─ SS25 Term
    │   └─ Profiles: student_profile, grader_profile
    └─ WS25 Term
        └─ Profiles: student_profile, grader_profile, research_profile
```

## Configuration Flow

Here's how the system resolves a user's environment when spawning a container:

### Step 1: Load Base Configuration

```yaml
Server Config → Roles → Profiles → Mount Definitions
```

The system loads:
- Server-wide settings
- Role definitions and permissions
- All profile definitions
- Global mount definitions

### Step 2: Apply Course Configuration

```yaml
Course Config → Runtime Overrides → Filter Profiles
```

For the selected course and term:
- Load course metadata
- Apply course-level runtime overrides
- Apply term-level runtime overrides
- Filter to allowed profiles for the term

### Step 3: Check Permissions and Present Choices

```yaml
User Role → Check Permissions → Filter Profiles
```

The system:
- Retrieves user's role(s) in the course
- Checks `spawn:profile` permissions for each allowed profile
- Filters to only profiles the user can spawn

```
User sees: Available profiles for Math101 (WS25)
  - Student Profile (if user has spawn:profile!profile=student_profile)
  - Grader Profile (if user has spawn:profile!profile=grader_profile)
```

### Step 4: Resolve Selected Profile

```yaml
Profile Selection → Parameter Substitution → Mount Resolution
```

When a user selects a profile:
- Validate required parameters (username, course_id, term_id)
- Substitute template variables (e.g., `${{inputs.username}}`)
- Resolve mount requests to actual mount configurations
- Apply admin mounts if user has admin privileges

### Step 5: Launch Container

```
Final Configuration → Kubernetes Pod → Running Container
```

The system creates a Kubernetes pod with:
- Specified container image
- Resolved resource limits
- Environment variables
- Mounted volumes

## Configuration Hierarchy

Settings cascade through multiple levels, with later levels overriding earlier ones:

```
1. Base Profile Definition
   ↓ (defines defaults)
2. Inherited Profile
   ↓ (overrides/extends base)
3. Course Runtime Override
   ↓ (course-specific changes)
4. Term Runtime Override
   ↓ (term-specific changes)
5. Final Resolved Configuration
```

**Example**: A student in ML101 (WS25) gets:
- Base profile: standard resource limits
- Student profile: student-specific image and mounts
- Course override: ML-specific container image
- Term override: higher memory limit for advanced projects
- Final config: Fully customized environment

## Template System

The configuration system supports template substitution using `${{inputs.parameter_name}}` syntax:

**In Profiles**:
```yaml
environment:
  NB_USER: "${{inputs.username}}"
  COURSE_ID: "${{inputs.course_id}}-${{inputs.term_id}}"
```

**In Mount Requests**:
```yaml
mount_requests:
  home:
    id: student_home
    args:
      username: "${{inputs.username}}"
      course_id: "${{inputs.course_id}}"
```

At spawn time, these placeholders are replaced with actual values provided by the user or system context.

## Common Patterns

### Pattern 1: Basic Course Setup

**Use Case**: Standard course with students and instructors

**Configuration**:
1. Define base profile with common settings
2. Create student and grader profiles (inherit from base)
3. Define course with terms and allowed profiles
4. Configure mounts for student homes and course materials

### Pattern 2: Specialized Course

**Use Case**: Machine learning course needing GPU and special libraries

**Configuration**:
1. Use standard profiles as base
2. Add course-level runtime overrides for ML-specific images
3. Optionally increase resource limits for GPU access
4. Keep mount configuration the same

### Pattern 3: Pilot Program

**Use Case**: Test new profile with select users

**Configuration**:
1. Create new inherited profile with experimental features
2. Add profile to specific term only (not all terms)
3. Monitor usage and feedback
4. Roll out to other terms when ready

### Pattern 4: Multi-Role Course

**Use Case**: Course with students, TAs, and instructors

**Configuration**:
1. Create base profile with shared settings
2. Create role-specific profiles (student, TA, grader, instructor)
3. Use different mount requests for each role
4. Configure appropriate resource limits per role

## Best Practices

### Organization

- **Keep base profiles minimal** - Only include truly common settings
- **Use inheritance extensively** - Avoid duplicating configuration
- **Name consistently** - Use clear, descriptive names for profiles and courses
- **Document decisions** - Add comments explaining why overrides exist

### Security

- **Use admin mounts for sensitive data** - Only mounted for admin users
- **Set appropriate readonly flags** - Prevent accidental modifications
- **Review allowed profiles** - Ensure students can't access grader environments
- **Validate parameters** - Mark required parameters correctly

### Performance

- **Set realistic resource limits** - Don't over-allocate cluster resources
- **Monitor actual usage** - Adjust limits based on data
- **Use appropriate images** - Smaller images start faster
- **Cache images** - Use consistent tags to leverage caching

### Maintenance

- **Version control everything** - Track changes to configurations
- **Test changes in staging** - Validate before production deployment
- **Archive old terms** - Move completed term configs out of active directory
- **Review regularly** - Clean up unused profiles and courses

## Getting Started

To configure the E2x Course Hub:

1. **[Set up server configuration](server.md)** - Define global settings and file paths
2. **[Define roles and permissions](roles.md)** - Configure access control and authorization
3. **[Define mount definitions](mounts.md)** - Create templates for storage volumes
4. **[Create runtime configurations](runtime.md)** - Understand runtime settings
5. **[Configure profiles](profiles.md)** - Define user environment templates
6. **[Set up courses](course.md)** - Organize by course and term

Each guide provides detailed schemas, examples, and best practices.

## Reference Documentation

```{toctree}
:maxdepth: 1

server
roles
mounts
runtime
profiles
course
```

## Additional Resources

- **Example Configurations** - See the `docs/source/example/` directory for complete working examples
- **API Documentation** - Detailed API references for each schema
- **Getting Started Guide** - Step-by-step setup instructions

## Support

For questions or issues:
- Review the detailed configuration guides linked above
- Check example configurations for reference implementations
- Consult the API documentation for schema details