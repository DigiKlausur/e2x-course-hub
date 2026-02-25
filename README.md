# e2x Course Hub

A comprehensive JupyterHub extension providing advanced course management, profile configuration, and dynamic spawning capabilities for educational environments. This system enables role-based access control, flexible resource allocation, and seamless integration with KubeSpawner for Kubernetes-based deployments.

## Overview

`e2x-course-hub` is designed for educational institutions running JupyterHub in Kubernetes environments. It provides:

- **Dynamic Profile Management**: Configure and manage multiple profiles per course/term with runtime overrides
- **Course Service**: Web-based UI for managing course members and permissions
- **KubeSpawner Integration**: Custom hooks for profile lists and pre-spawn configuration
- **Role-Based Access Control**: Fine-grained permissions for students, graders, and course admins
- **Mount Management**: Flexible volume mount definitions with placeholder support
- **User Management**: Automatic JupyterHub user creation and group management

## Key Features

### Course Management
- **Multi-term Support**: Manage multiple active terms per course
- **Profile Configuration**: Define course-specific profiles with runtime overrides
- **Metadata**: Rich course information including descriptions and maintainer contacts
- **Member Management**: Add/remove students and graders with appropriate permissions

### Profile System
- **Inheritance**: Profiles can inherit from base profiles with selective overrides
- **Runtime Configuration**: Specify images, resources, environment variables, and more
- **Parameterization**: Use placeholders for dynamic value injection (username, course_id, term_id)
- **Mount Requests**: Define volume mounts per profile with flexible mount definitions

### Web Interface
- **Modern React UI**: Built with React 19, TypeScript, and TailwindCSS
- **Course Overview**: View all accessible courses and their details
- **Member Management**: Add/remove course members with role-based permissions
- **Profile Details**: View detailed profile configurations

### KubeSpawner Integration
- **Profile List Hook**: Generates dynamic profile lists based on user permissions
- **Pre-spawn Hook**: Configures volume mounts and other settings before spawning
- **Term Sorting**: Customizable sorting for term organization (WS25, SS25, etc.)

## Architecture

```
e2x_course_hub/
├── api/                    # API layer
│   ├── api.py             # Central API aggregator
│   ├── course_api.py      # Course management API
│   ├── profile_api.py     # Profile resolution API
│   └── hub_api.py         # JupyterHub API integration
├── course_service/        # Web service
│   ├── app.py            # Tornado application
│   └── handlers/         # Request handlers
├── schema/               # Pydantic models
│   ├── course.py        # Course configuration schemas
│   ├── profile.py       # Profile schemas
│   ├── runtime.py       # Runtime/resource schemas
│   ├── mount.py         # Volume mount schemas
│   └── user.py          # User/role schemas
├── kubespawner_hooks.py  # KubeSpawner integration
└── mocks/               # Mock data for testing

course-service-ui/        # React frontend
├── src/
│   ├── api/             # API client
│   ├── components/      # React components
│   └── hooks/           # Custom React hooks
```

## Installation

### From Git

```bash
pip install git+https://github.com/Digiklausur/e2x-course-hub.git
```

### For Development

```bash
git clone https://github.com/Digiklausur/e2x-course-hub
cd e2x-course-hub
pip install -e ".[dev]"
```

### Building the Frontend

```bash
cd course-service-ui
npm install
npm run build
```

The built assets are automatically included in the Python package via `hatch-jupyter-builder`.

## Configuration

### Server Configuration File

Create a YAML configuration file (e.g., `config.yml`):

```yaml
profile_dir: "/path/to/profiles"
course_config_dir: "/path/to/courses"
mount_definitions_file: "/path/to/mount_definitions.yaml"

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

### Course Configuration

Create YAML files in your `course_config_dir`:

```yaml
# courses/AMR.yaml
metadata:
  course_id: AMR
  course_name: Autonomous Mobile Robots
  description: Advanced robotics course

profile_runtime_overrides:
  grader_profile:
    image:
      name: ghcr.io/my-org/teacher-notebook
      tag: latest

terms:
  WS25:
    allowed_profiles:
      - grader_profile
      - student_profile
    profile_runtime_overrides:
      student_profile:
        resources:
          limits:
            memory: "2Gi"
```

### Profile Configuration

Create YAML files in your `profile_dir`:

```yaml
# profiles/student.yaml
name: student_profile
display_name: "Student Profile"
inherits: base_profile

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
    name: jupyter/datascience-notebook
    tag: latest
  environment:
    NBGRADER_COURSE_ID: "${{inputs.course_id}}-${{inputs.term_id}}"
  resources:
    limits:
      memory: "1Gi"
      cpu: "1"

mount_requests:
  home:
    id: student_home
    args:
      username: "${{ inputs.username }}"
      course_id: "${{ inputs.course_id }}"
```

### Mount Definitions

Define reusable mount patterns:

```yaml
# mount_definitions.yaml
student_home:
  inputs: 
    username:
      required: true
      type: string
    course_id:
      required: true
      type: string
  description: "Student home directory"
  name: "home-${{inputs.username}}"
  mountPath: "/home/jovyan"
  subPath: "${{inputs.course_id}}/${{inputs.username}}"
```

## Usage

### As a JupyterHub Service

```python
# jupyterhub_config.py
c.JupyterHub.services = [
    {
        'name': 'course-service',
        'url': 'http://localhost:10101',
        'command': [
            'python', '-m', 'e2x_course_hub.course_service.app',
            '--CourseServiceApp.server_config_file=/etc/jupyterhub/config.yml',
            '--CourseServiceApp.port=10101',
            '--CourseServiceApp.add_users_to_hub=True'
        ],
        'environment': {
            'E2X_COURSE_HUB_CONFIG': '/etc/jupyterhub/config.yml'
        }
    }
]

c.JupyterHub.load_roles = [
    {
        'name': 'course-service',
        'services': ['course-service'],
        'scopes': [
            'access:services!service=course-service',
            'admin:users',
            'list:users',
            'read:users',
            'admin:groups',
        ]
    }
]
```

### KubeSpawner Integration

```python
# jupyterhub_config.py
from e2x_course_hub.kubespawner_hooks import (
    get_profile_list_hook,
    get_pre_spawn_hook,
    configure_autospawn
)

from e2x_course_hub.course_service._data import KUBESPAWNER_TEMPLATE_PATH, JUPYTERHUB_TEMPLATE_PATH

# Configure KubeSpawner
c.JupyterHub.spawner_class = 'kubespawner.KubeSpawner'

# Add hooks
c.KubeSpawner.profile_list = get_profile_list_hook(
    server_config_file='/etc/jupyterhub/config.yml'
)
c.KubeSpawner.pre_spawn_hook = get_pre_spawn_hook(
    server_config_file='/etc/jupyterhub/config.yml'
)

# Configure JupyterHub and the KubeSpawner to use the templates from e2x_course_hub
c.KubeSpawner.additional_profile_form_template_paths = [KUBESPAWNER_TEMPLATE_PATH]

c.JupyterHub.template_paths = [JUPYTERHUB_TEMPLATE_PATH]

# Optional: Configure autospawn behavior
# Automatically spawns the server if only one course/profile is available
configure_autospawn(
    c,
    auto_spawn_single_course=True,  # Enable auto-spawn for single course
    auto_spawn_countdown=5           # Countdown in seconds before spawning
)
```

#### Autospawn Configuration

The `configure_autospawn` function adds template variables to control automatic server spawning behavior:

- **`auto_spawn_single_course`** (bool): When `True`, automatically spawns the server if the user has access to only one course/profile. Default: `False`
- **`auto_spawn_countdown`** (int): Number of seconds to show a countdown before auto-spawning. Gives users time to cancel if needed. Default: `5`

This function safely merges with any existing `template_vars` in your configuration, preserving other template variables you may have set.

**Note**: For autospawn to work, you need custom JupyterHub templates that implement the autospawn logic using these template variables.

### Standalone Course Service

```python
from e2x_course_hub.course_service.app import CourseServiceApp

app = CourseServiceApp()
app.server_config_file = "/path/to/config.yml"
app.port = 10101
app.add_users_to_hub = True
app.initialize()
app.start()
```

## API Reference

### Course Service REST API

#### Courses
- `GET /api/courses` - List courses accessible to current user
- `GET /api/courses/<course_id>/<term_id>` - Get course details
- `POST /api/courses/<course_id>/<term_id>/leave` - Leave a course

#### Course Members
- `GET /api/courses/<course_id>/<term_id>/members` - List course members
- `POST /api/courses/<course_id>/<term_id>/members` - Add members to course
- `DELETE /api/courses/<course_id>/<term_id>/members` - Remove members from course

#### Profiles
- `GET /api/courses/<course_id>/<term_id>/profiles/<profile_id>` - Get profile details

#### Permissions
- `GET /api/courses/<course_id>/<term_id>/permissions` - Check user permissions
- `GET /api/courses/<course_id>/<term_id>/roles` - List assignable roles

### Python API

```python
from e2x_course_hub.api import API
from e2x_course_hub.api.hub_api import HubAPI
from e2x_course_hub.schema.user import User

# Initialize API
hub_api = HubAPI(api_token="...", api_url="...")
api = API(
    server_config_file="/path/to/config.yml",
    hub_api=hub_api,
    add_users_to_hub=True
)

# Get user's courses
user = User(username="alice", groups=["AMR.WS25.graders"])
courses = api.course_api.list_courses(user)

# Get resolved profile
profile = api.profile_api.get_profile(
    user=user,
    course_id="AMR",
    term_id="WS25",
    profile_id="student_profile"
)

# Add course members
api.course_api.add_course_members(
    user=user,
    course_id="AMR",
    term_id="WS25",
    role="student",
    usernames=["student1", "student2"]
)
```

## Development

### Running Mock Server

```bash
cd e2x_course_hub/mocks
python mock_server.py
```

Access at: http://localhost:8888

### Frontend Development

```bash
cd course-service-ui
npm run dev
```

### Code Quality

```bash
# Python linting
ruff check .

# Frontend linting
cd course-service-ui
npm run lint
npm run format
```

### Running Tests

```bash
pytest
```

## Environment Variables

- `JUPYTERHUB_SERVICE_PREFIX` - URL prefix for the service (set by JupyterHub)
- `JUPYTERHUB_API_TOKEN` - API token for JupyterHub authentication (set by JupyterHub)
- `JUPYTERHUB_API_URL` - JupyterHub API URL (set by JupyterHub)
- `E2X_COURSE_HUB_CONFIG` - Path to server configuration file

## Dependencies

### Python (>=3.8)
- `pydantic>=2.0` - Data validation and schema definition
- `jinja2` - Template rendering
- `PyYAML` - YAML configuration parsing
- `jupyterhub` - JupyterHub integration (runtime)
- `tornado` - Web framework (runtime)

### Frontend
- React 19 with TypeScript
- TailwindCSS 4 for styling
- TanStack Table for data tables
- Radix UI for accessible components
- React Router for navigation

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run linting and tests
5. Submit a pull request

## Support

- **Issues**: https://github.com/Digiklausur/e2x-course-hub/issues
- **Documentation**: https://github.com/Digiklausur/e2x-course-hub#readme