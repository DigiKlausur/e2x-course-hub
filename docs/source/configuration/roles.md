# Roles and Permissions

This guide explains the role-based access control (RBAC) system in the E2x Course Hub, which manages what users can do within courses.

## Overview

The E2x Course Hub uses a flexible RBAC system to control access to features and resources. The system provides:

1. **Role Definitions** - Named roles with assigned permissions
2. **Priority-Based Hierarchy** - Higher priority roles inherit lower priority permissions
3. **Fine-Grained Permissions** - Actions with optional constraints
4. **Permission Expansion** - Automatic inclusion of implied permissions (subscopes)

This allows you to define clear access levels (student, grader, course admin) while maintaining flexibility for custom authorization needs.

## Core Concepts

### Permissions

A permission defines an action that can be performed on a resource, with optional constraints:

```
action:resource!constraint_key=constraint_value
```

**Examples**:
- `spawn:profile!profile=student_profile` - Spawn the student profile
- `add:course-members!role=student` - Add students to the course
- `list:course-members` - List all course members (no constraints)

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.schema.roles.Permission
```

### Roles

A role is a named collection of permissions with a priority level. Higher priority roles automatically inherit all permissions from lower priority roles.

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.schema.roles.Role
```

### Permission Definitions

Permission definitions specify subscopes - permissions that are automatically implied when granting a permission. This follows JupyterHub's scope pattern.

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.schema.roles.PermissionDefinition
```

**Default Permission Definitions**:
- `add:course-members` implies `list:course-members` and `view:course-metadata`
- `remove:course-members` implies `list:course-members` and `view:course-metadata`

This means granting add/remove permissions automatically grants list and view permissions.

## Role Configuration

### Roles Schema

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.schema.roles.RolesConfig
```

## Priority-Based Hierarchy

The system uses numeric priorities to create an automatic role hierarchy:

```
Lower Priority                                    Higher Priority
     100                200                300                 400
  ┌────────┐        ┌────────┐        ┌────────┐        ┌──────────┐
  │Student │ ───────│ Grader │ ───────│ Admin  │────────│SuperAdmin│
  └────────┘        └────────┘        └────────┘        └──────────┘
    Basic             Student +        Grader +          Admin +
    Access            Management       All Access        System
```

**How it works**:
- A role with priority 200 automatically gets all permissions from roles with priority < 200
- This creates natural hierarchies without explicit inheritance configuration
- Example: A `grader` (200) automatically has all `student` (100) permissions

## Common Permissions

### Course Member Management

- `add:course-members` - Add any role to the course
- `add:course-members!role=student` - Add only students to the course
- `remove:course-members` - Remove any role from the course
- `remove:course-members!role=student` - Remove only students from the course
- `list:course-members` - List all course members
- `list:course-members!role=student` - List only students

### Profile Spawning

- `spawn:profile` - Spawn any profile
- `spawn:profile!profile=student_profile` - Spawn only the student profile
- `spawn:profile!profile=grader_profile` - Spawn only the grader profile

### Course Access

- `view:course-metadata` - View course information (name, description, terms)
- `leave:course` - Leave a course (remove yourself)

## Examples

### Example 1: Basic Three-Tier System

A standard educational setup with students, graders, and course administrators:

```yaml
roles:
  student:
    priority: 100
    scopes:
      - spawn:profile!profile=student_profile
      - view:course-metadata
      - leave:course
  grader:
    priority: 200
    scopes:
      - spawn:profile!profile=grader_profile
      - add:course-members!role=student
      - remove:course-members!role=student
  course_admin:
    priority: 300
    scopes:
      - spawn:profile!profile=grader_profile
      - add:course-members
      - remove:course-members
```

**Effective Permissions**:

**Student** (priority 100):
- Spawn student profile
- View course metadata
- Leave course

**Grader** (priority 200 - inherits from student):
- All student permissions (spawn student profile, view metadata, leave course)
- Spawn grader profile
- Add students to course
- Remove students from course
- List students (implied by add/remove)

**Course Admin** (priority 300 - inherits from grader):
- All grader permissions (including student permissions)
- Add/remove members with any role (not just students)
- List all members (implied by add/remove)

### Example 2: Multiple Profile Access

Allow students to choose between multiple environments:

```yaml
roles:
  student:
    priority: 100
    scopes:
      - spawn:profile!profile=student_profile
      - spawn:profile!profile=student_gpu_profile
      - spawn:profile!profile=student_r_profile
      - view:course-metadata
```

**Key Points**:
- Students can spawn any of three different profiles
- Useful for courses offering multiple toolsets (Python, R, GPU access)
- Profile availability can be further restricted at the course/term level

### Example 3: Teaching Assistant Role

Add a TA role between student and grader:

```yaml
roles:
  student:
    priority: 100
    scopes:
      - spawn:profile!profile=student_profile
  teaching_assistant:
    priority: 150
    scopes:
      - spawn:profile!profile=ta_profile
      - list:course-members!role=student
  grader:
    priority: 200
    scopes:
      - spawn:profile!profile=grader_profile
      - add:course-members!role=student
      - remove:course-members!role=student
```

**Effective Permissions**:

**Teaching Assistant** (priority 150):
- Student permissions (spawn student profile)
- Spawn TA profile
- List students (but cannot add/remove)

This creates a middle tier with read-only access to student lists.

### Example 4: Custom Permission Definitions

Define custom permissions with subscopes:

```yaml
roles:
  student:
    priority: 100
    scopes:
      - spawn:profile!profile=student_profile
      - submit:assignment
  grader:
    priority: 200
    scopes:
      - grade:assignment
      - download:submissions

permission_definitions:
  grade:assignment:
    subscopes:
      - view:assignment
      - list:submissions
  download:submissions:
    subscopes:
      - list:submissions
```

**Key Points**:
- Custom permissions for domain-specific actions
- Grading automatically grants viewing and listing
- Permission definitions create logical groupings

## Permission Checking

The system checks permissions by:

1. **Collecting all roles** - Gather user's assigned roles
2. **Finding inherited roles** - Include all roles with lower priority
3. **Gathering permissions** - Collect all permissions from all applicable roles
4. **Expanding subscopes** - Add implied permissions from permission definitions
5. **Matching constraints** - Check if permission matches requested action/resource/constraints

### Constraint Matching Rules

A permission matches a request if:
- **Action and resource match exactly**
- **Either**: Permission has no constraints (grants access to all), **OR**
- **All** requested constraints match the permission's constraints

**Examples**:

| Permission | Request | Matches? | Reason |
|------------|---------|----------|---------|
| `add:course-members` | `add:course-members!role=student` | ✅ Yes | No constraints = all access |
| `add:course-members!role=student` | `add:course-members!role=student` | ✅ Yes | Exact match |
| `add:course-members!role=student` | `add:course-members!role=grader` | ❌ No | Constraint mismatch |
| `add:course-members!role=student` | `add:course-members` | ❌ No | Request broader than granted |

## Role Assignment

Role assignment is managed through course membership:

1. **Course member API** - Add users to courses with specific roles
2. **External systems** - Integrate with LMS or directory services
3. **Manual assignment** - Through the Course Hub API or UI

When a user accesses a course, the system:
- Retrieves their role(s) in that course
- Resolves effective permissions
- Filters available actions and profiles accordingly

## Best Practices

### Role Design

- **Start simple** - Begin with student/grader/admin, add complexity as needed
- **Use priority gaps** - Leave space between priorities (100, 200, 300) for future roles
- **Name clearly** - Use role names that reflect actual responsibilities
- **Document permissions** - Comment why specific permissions are granted

### Permission Scope

- **Be specific with constraints** - Use constraints to limit access appropriately
- **Grant minimum necessary** - Don't give broad permissions when specific ones work
- **Use subscopes** - Define implied permissions to reduce configuration
- **Test permission resolution** - Verify effective permissions match expectations

### Priority Assignment

- **100-199**: Basic users (students, read-only access)
- **200-299**: Management roles (graders, TAs, course staff)
- **300-399**: Administrative roles (course admins, instructors)
- **400+**: System administrators (platform-wide access)

### Security Considerations

- **Validate constraints** - Ensure constraint values are validated
- **Audit permissions** - Regularly review role definitions
- **Principle of least privilege** - Grant only necessary permissions
- **Test thoroughly** - Verify permission checks work as expected

## Permission Factory Methods

The `Permission` class provides factory methods for common permissions:

```python
# Add course members
Permission.add_course_members(role='student')
Permission.remove_course_members(role='grader')

# List members
Permission.list_course_members()  # All roles
Permission.list_course_members(role='student')  # Specific role

# Profile spawning
Permission.spawn_profile(profile='student_profile')

# Course access
Permission.view_course_metadata()
Permission.leave_course()
```

These provide type safety and prevent typos when checking permissions programmatically.

## Integration with Profiles

Roles control which profiles users can spawn:

1. **Profile definition** - Profile exists in configuration
2. **Course configuration** - Profile is in `allowed_profiles` for the term
3. **Role permission** - User has `spawn:profile!profile=profile_name` permission

All three conditions must be met for a user to spawn a profile.

**Example Flow**:
```
User: alice, Role: grader, Course: Math101, Term: WS25

1. Check course config: WS25.allowed_profiles includes 'grader_profile' ✅
2. Check role permission: grader has 'spawn:profile!profile=grader_profile' ✅
3. Check profile exists: grader_profile is defined ✅

Result: Alice can spawn grader_profile
```

## API Usage

When building applications on top of the Course Hub:

```python
from e2x_course_hub.schema.roles import Roles, Permission

# Load roles configuration
roles = Roles(**yaml_config)

# Check if user can add students
can_add_students = roles.has_permission(
    actor_roles='grader',
    permission=Permission.add_course_members(role='student')
)

# List all effective permissions for a role
grader_permissions = roles.list_permissions('grader')

# Find strongest role when user has multiple
strongest = roles.get_strongest_role(['student', 'grader', 'course_admin'])
# Returns: 'course_admin'
```

## Troubleshooting

### User cannot spawn profile

**Check**:
1. Profile is in course's `allowed_profiles` for the term
2. User's role has `spawn:profile!profile=profile_name` permission
3. Profile constraint matches exactly (case-sensitive)

### User cannot manage course members

**Check**:
1. User's role has `add:course-members` or `remove:course-members` permission
2. If constrained (e.g., `!role=student`), ensure they're trying to add/remove that role
3. Check priority - ensure role priority is appropriate for management

### Permissions not inheriting

**Check**:
1. Priority values are set correctly (higher priority roles have higher numbers)
2. Roles are defined in the configuration
3. No duplicate priority values (can cause ambiguity)

## Complete Workflow

1. **Define roles** in server configuration with priorities and permissions
2. **Optionally define custom permission definitions** with subscopes
3. **Assign roles to users** when they're added to courses
4. **System resolves permissions** when users access course features
5. **Access control applied** - users see only allowed profiles and actions

