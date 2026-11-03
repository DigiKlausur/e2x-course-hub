# Semesters

A course runs in one or more semesters, such as `WS23`. Students, teaching
assistants, instructors and observers are members of a semester, not of the course,
and every semester has its own notebook image and resources.

## Create a semester

Course owners click **Create Semester** on the course's **Overview** tab and enter a
semester ID such as `WS23`. The new semester starts with the course's semester
template and the current default version of its image family (see {doc}`courses`).
Under **Student access**, choose **Unrestricted** to let students start notebook
servers at any time, or **Restricted** to set when it opens or closes (see **Set the
student access period** below).

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
- **General Information**: the course, the semester, when it was created and, under
  **Student access**, whether and until when students can start notebook servers.
- **Student join link**: the link with which students join the semester themselves
  (see **Invite students with a join link** below). Only course owners and
  instructors see it.
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

## Set the student access period

Course owners and instructors can limit when students can start notebook servers for a
semester, either
when creating it or later: on the semester's **Overview** tab, click **Change** next to
**Student access** under **General Information**. Choose **Restricted** and set
**Opens**, **Closes** or both. Times are entered in your browser's time zone. Choosing
**Unrestricted** lets students start notebook servers for the semester at any time
again.

- Leave **Opens** empty to open the semester immediately.
- Leave **Closes** empty to keep it open indefinitely.
- **Closes** must be after **Opens**.

Outside the access period, the semester does not appear on the spawn page for
students. Teaching assistants, instructors and observers are not restricted, so they
can prepare the semester before it opens and grade after it closes.

```{note}
**Known limitation:** the access period only controls *starting* a notebook server.
A student who started a server before the closing time keeps it until it is stopped,
for example by JupyterHub's idle culler. Running servers are not stopped when the
access period closes.
```

## Invite students with a join link

Instead of adding students by username, course owners and instructors can share a
link with which students join the semester themselves. Each semester has at most one
link, and it only ever makes people students. The link contains a random token
instead of the course or semester name.

The link is managed in the **Student join link** card on the semester's **Overview**
tab:

- **Turn on link** creates the link. Choose when it expires, or leave **Expires**
  empty to keep it working until you turn it off. The expiry starts out as the closing
  time of the student access period, if there is one.
- **Copy** copies the link, for example to post it in your learning platform.
- **Change** next to the expiry sets a new expiry. The link itself stays the same.
- **Regenerate** replaces the link with a new one. The old link stops working
  immediately, so use this if the link reached people it was not meant for.
- **Turn off** stops the link from working. Turning it on again creates a new link.

A student who opens the link logs in to JupyterHub if needed and is then asked
whether to join the semester. Nobody is added just by opening the link, so link
previews in chat or mail programs cannot join anyone. After clicking **Join**:

- if students can start notebook servers right now, the student is taken to the
  spawn page.
- if the student access period has not opened yet, the page says from when they can
  start notebook servers. They are already a member and do not need the link again.

The link cannot be used once the student access period has closed. Users who already
have a role in the semester or course, such as instructors, are told so and are not
added as students. An expired, regenerated, turned-off or mistyped link shows the same
message, which does not reveal whether the link ever existed.

## Delete a semester

Course owners and instructors can delete a semester on its **Settings** tab. Deleting a
semester removes all of its members. This cannot be undone, so you have to type
`<course ID>-<semester ID>` (for example `NN-WS23`) to confirm.
