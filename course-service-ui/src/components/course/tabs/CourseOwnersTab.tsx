import { MemberListCard } from "@components/membership/MemberListCard";
import { useCourseOwners, useUpdateCourseOwners } from "@hooks/membership";
import { useCourse } from "@hooks/course";
import { MembershipRole, memberLabels } from "@domain/roles";

const NO_ACTIONS = { list: false, add: false, remove: false };

interface Props {
  courseId: string;
}

export function CourseOwnersTab({ courseId }: Props) {
  // Listing owners is permission guarded and answers 403, so the course's own
  // actions decide whether the request is made at all.
  const { data: course, isLoading: courseLoading } = useCourse(courseId);
  const actions = course?.actions.members.courseOwners ?? NO_ACTIONS;

  const { data, isLoading } = useCourseOwners(courseId, actions.list);
  const update = useUpdateCourseOwners(courseId);

  if (courseLoading) return <p className="text-gray-500">Loading…</p>;

  return (
    <MemberListCard
      labels={memberLabels[MembershipRole.CourseOwner]}
      actions={actions}
      usernames={data?.usernames ?? []}
      isLoading={isLoading}
      update={update}
      notAllowedMessage="You are not allowed to view the owners of this course."
    />
  );
}
