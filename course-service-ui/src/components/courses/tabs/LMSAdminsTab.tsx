import { MemberListCard } from "@components/membership/MemberListCard";
import { useLMSAdmins, useUpdateLMSAdmins } from "@hooks/membership";
import { useCourses } from "@hooks/course";
import { MembershipRole, memberLabels } from "@domain/roles";

const NO_CAPABILITIES = { view: false, add: false, remove: false };

export function LMSAdminsTab() {
  // Listing LMS admins is permission guarded and answers 403, so the course
  // collection's capability decides whether the request is made at all.
  const { data: collection, isLoading: collectionLoading } = useCourses();
  const capabilities = collection?.capabilities.lmsAdmins ?? NO_CAPABILITIES;

  const { data, isLoading } = useLMSAdmins(capabilities.view);
  const update = useUpdateLMSAdmins();

  if (collectionLoading) return <p className="text-gray-500">Loading…</p>;

  return (
    <MemberListCard
      labels={memberLabels[MembershipRole.Admin]}
      capabilities={capabilities}
      usernames={data?.usernames ?? []}
      isLoading={isLoading}
      update={update}
      notAllowedMessage="You are not allowed to view the LMS admins."
    />
  );
}
