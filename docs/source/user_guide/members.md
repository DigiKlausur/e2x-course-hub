# Members

What a user can do in the course service depends on their roles. A user can hold
several roles, for example be an instructor in one course and a student in another.

| Role                   | Held for     | Managed on                               |
| ---------------------- | ------------ | ---------------------------------------- |
| **LMS Admin**          | everything   | Courses page, **LMS Admins** tab         |
| **Course Creator**     | everything   | Courses page, **Course Creators** tab    |
| **Course Owner**       | one course   | Course page, **Course Owners** tab       |
| **Instructor**         | one semester | Semester page, **Instructors** tab       |
| **Teaching Assistant** | one semester | Semester page, **Teaching Assistants** tab |
| **Observer**           | one semester | Semester page, **Observers** tab         |
| **Student**            | one semester | Semester page, **Students** tab          |

You only see the tabs for the roles you are allowed to view. The full list of what
each role may do is in {doc}`../reference/roles`.

## Add members

Open the tab of the role, for example **Students** on a semester page, and click the
add button. Enter the usernames, one per line. Commas and spaces also work as
separators, so you can paste a list.

```{image} ../images/term_add_students.png
:align: center
:alt: Adding students to a semester
:class: screenshot shadow
```

Usernames are JupyterHub usernames. Whether a username that has never logged in to
JupyterHub can be added depends on the deployment (see `E2X_ADD_USERS_TO_HUB` in
{doc}`../reference/configuration`).

## Remove members

Select one or more members in the table and remove them with the button above the
table. Removing a user from a role does not delete the user from JupyterHub.

## What can a role do?

Next to every member list there is a **What can … do?** link. It shows what a member
of that role is allowed to do, so you can check before you add someone.

```{image} ../images/term_what_can_a_student_do.png
:align: center
:alt: What a student can do in a semester
:class: screenshot shadow
```

Turn on **Show restrictions** to also see what the role is not allowed to do.
