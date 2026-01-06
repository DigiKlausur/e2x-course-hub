# Course Service

E2x Course Hub comes with a JupyterHub service that allows users to manage the members of a course.

## JupyterHub Configuration

To run the service add the following to your `jupyterhub_config.py`:

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

## Configuration Options

The following configuration options for the service are available:

```{eval-rst}
.. autoclass:: e2x_course_hub.course_service.app.CourseServiceApp
   :members:
   :exclude-members: classes, aliases, flags, init_tornado_settings, init_handlers, initialize_tornado_application, initialize, start, handlers, tornado_settings
   :no-inherited-members:
```