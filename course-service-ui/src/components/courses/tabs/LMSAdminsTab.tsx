import { MemberListCard } from "@components/membership/MemberListCard";
import { useLMSAdmins, useUpdateLMSAdmins } from "@hooks/membership";
import { useCourses } from "@hooks/course";
import { MembershipRole, memberLabels } from "@domain/roles";

const NO_ACTIONS = { list: false, add: false, remove: false };

export function LMSAdminsTab() {
  // Listing LMS admins is permission guarded and answers 403, so the course
  // collection's actions decide whether the request is made at all.
  const { data: collection, isLoading: collectionLoading } = useCourses();
  const actions = collection?.actions.members.lmsAdmins ?? NO_ACTIONS;

  const { data, isLoading } = useLMSAdmins(actions.list);
  const update = useUpdateLMSAdmins();

  if (collectionLoading) return <p className="text-gray-500">Loading…</p>;

  return (
    <MemberListCard
      labels={memberLabels[MembershipRole.Admin]}
      actions={actions}
      usernames={data?.usernames ?? []}
      isLoading={isLoading}
      update={update}
      notAllowedMessage="You are not allowed to view the LMS admins."
    />
  );
}
