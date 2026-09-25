import { MemberListCard } from "@components/membership/MemberListCard";
import { useCourseCreators, useUpdateCourseCreators } from "@hooks/membership";
import { useCourses } from "@hooks/course";
import { MembershipRole, memberLabels } from "@domain/roles";

const NO_CAPABILITIES = { view: false, add: false, remove: false };

export function CourseCreatorsTab() {
  // Listing course creators is permission guarded and answers 403, so the
  // course collection's capability decides whether the request is made at all.
  const { data: collection, isLoading: collectionLoading } = useCourses();
  const capabilities =
    collection?.capabilities.courseCreators ?? NO_CAPABILITIES;

  const { data, isLoading } = useCourseCreators(capabilities.view);
  const update = useUpdateCourseCreators();

  if (collectionLoading) return <p className="text-gray-500">Loading…</p>;

  return (
    <MemberListCard
      labels={memberLabels[MembershipRole.CourseCreator]}
      capabilities={capabilities}
      usernames={data?.usernames ?? []}
      isLoading={isLoading}
      update={update}
      notAllowedMessage="You are not allowed to view the course creators."
    />
  );
}
