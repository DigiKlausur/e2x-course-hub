# Courses

The **Courses** page is the start page of the course service. It lists every course
you can view. Depending on your role it has two more tabs, **LMS Admins** and
**Course Creators**, where you manage who holds these roles (see {doc}`members`).

```{image} ../images/course_service_courses.png
:align: center
:alt: The course list
:class: screenshot shadow
```

**Your access** in the top right corner shows everything you are allowed to do on
the current page. Every course and semester page has this button.

## Create a course

LMS admins and course creators see a **Create Course** button. A course needs:

- a **course ID**, a short identifier such as `NN`. It cannot be changed later.
- a **course name**, such as "Neural Networks".
- an optional **description**.

You become the course owner of every course you create.

## The course page

Open a course from the list to get to its page.

```{image} ../images/course_overview.png
:align: center
:alt: The overview of a course
:class: screenshot shadow
```

The **Overview** tab shows:

- **Semesters**: all semesters of the course. Course owners create new semesters
  here (see {doc}`semesters`).
- **Course Information**: the course ID, name and description.
- **Current Semester Template**: the notebook image and resources a new semester
  starts with.

The **Course Owners** tab lists the owners of the course. The **Settings** tab is where
course owners change the course name and description, or delete the course.

## The semester template

The semester template has three parts:

| Setting               | Meaning                                                           |
| --------------------- | ----------------------------------------------------------------- |
| **Notebook Image**    | The image notebook servers start from, such as a data science image. |
| **Student Resources** | The resource tier (CPU, memory, …) of the student environment.    |
| **Grader Resources**  | The resource tier of the grader environment.                      |

Click **Change** next to a setting to pick another value.

```{image} ../images/course_select_notebook_image.png
:align: center
:alt: Choosing the notebook image of a course
:class: screenshot shadow
```

```{image} ../images/course_select_student_resources.png
:align: center
:alt: Choosing the student resources of a course
:class: screenshot shadow
```

The images and resource tiers you can choose from come from the infrastructure
catalog. They are defined by the administrators of the deployment, not in the course
service.

```{note}
The semester template is only copied into a semester when the semester is created.
Changing the template does not change existing semesters. To change a running
semester, change its own runtime (see {doc}`semesters`).
```

## Delete a course

Course owners can delete a course on its **Settings** tab. Deleting a course deletes
all of its semesters and removes all of their members. This cannot be undone, so you
have to type the course ID to confirm.
