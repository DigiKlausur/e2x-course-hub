# Semesters

A course runs in one or more semesters, such as `WS23`. Students, teaching
assistants, instructors and observers are members of a semester, not of the course,
and every semester has its own notebook image and resources.

## Create a semester

Course owners click **Create Semester** on the course's **Overview** tab and enter a
semester ID such as `WS23`. The new semester starts with the course's semester
template (see {doc}`courses`).

## The semester page

Open a semester from the course's semester list.

```{image} ../images/term_overview.png
:align: center
:alt: The overview of a semester
:class: screenshot shadow
```

The **Overview** tab shows:

- the members of the semester, with one tab each for **Students**, **Teaching
  Assistants**, **Instructors** and **Observers** (see {doc}`members`).
- **General Information**: the course and the semester.
- **Semester Runtime**: the notebook image, student resources and grader resources of
  this semester.

## Change the semester runtime

Course owners and instructors can click **Change** next to a setting in **Semester
Runtime**. The change only affects this semester. It applies to notebook servers that
are started after the change. Servers that are already running keep their old
settings until they are restarted.

## Start a notebook server

The course service does not start notebook servers. Members start them from the
JupyterHub spawn page, where they pick a course and semester. Depending on their role
they can start:

| Environment                      | Meaning                                                      |
| -------------------------------- | ------------------------------------------------------------ |
| **Student environment**          | The image with the student resources.                        |
| **Grader environment**           | The image with the grader resources.                         |
| **Read-only grader environment** | The grader environment with the course directory read-only. |

Which role may start which environment is listed in {doc}`../reference/roles`.

## Delete a semester

Course owners and instructors can delete a semester on its **Settings** tab. Deleting a
semester removes all of its members. This cannot be undone, so you have to type
`<course ID>-<semester ID>` (for example `NN-WS23`) to confirm.
