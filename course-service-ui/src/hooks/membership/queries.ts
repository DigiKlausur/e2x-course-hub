import { useQuery } from "@tanstack/react-query";
import { membershipAPI } from "@api";
import type { MembershipCollectionResponse } from "@api/types";
import { membershipQueryKeys } from "./keys";
import { MembershipRole } from "@domain/roles";

export function useLMSAdmins() {
  return useQuery<MembershipCollectionResponse>({
    queryKey: [...membershipQueryKeys.lms.roles[MembershipRole.Admin]()],
    queryFn: () => membershipAPI.lms.fetchLMSAdmins(),
  });
}

export function useCourseCreators() {
  return useQuery<MembershipCollectionResponse>({
    queryKey: [
      ...membershipQueryKeys.lms.roles[MembershipRole.CourseCreator](),
    ],
    queryFn: () => membershipAPI.lms.fetchCourseCreators(),
  });
}

/**
 * Like the term membership endpoints below, this is permission guarded and
 * answers 403 rather than an empty list, so callers pass `enabled` from the
 * course's `capabilities.viewCourseOwners`.
 */
export function useCourseOwners(courseId: string, enabled = true) {
  return useQuery<MembershipCollectionResponse>({
    queryKey: [
      ...membershipQueryKeys.courses.roles[MembershipRole.CourseOwner](
        courseId,
      ),
    ],
    queryFn: () => membershipAPI.course.fetchOwners(courseId),
    enabled,
  });
}

/**
 * The term membership endpoints are permission guarded and answer 403 rather
 * than an empty list when the caller may not see a role. Callers therefore pass
 * `enabled` from the term's `capabilities.membership` flags, so a request is
 * only made when it can succeed.
 */
export function useInstructors(
  courseId: string,
  termId: string,
  enabled = true,
) {
  return useQuery<MembershipCollectionResponse>({
    queryKey: [
      ...membershipQueryKeys.terms.roles[MembershipRole.Instructor](
        courseId,
        termId,
      ),
    ],
    queryFn: () => membershipAPI.term.fetchInstructors(courseId, termId),
    enabled,
  });
}

export function useObservers(courseId: string, termId: string, enabled = true) {
  return useQuery<MembershipCollectionResponse>({
    queryKey: [
      ...membershipQueryKeys.terms.roles[MembershipRole.Observer](
        courseId,
        termId,
      ),
    ],
    queryFn: () => membershipAPI.term.fetchObservers(courseId, termId),
    enabled,
  });
}

export function useStudents(courseId: string, termId: string, enabled = true) {
  return useQuery<MembershipCollectionResponse>({
    queryKey: [
      ...membershipQueryKeys.terms.roles[MembershipRole.Student](
        courseId,
        termId,
      ),
    ],
    queryFn: () => membershipAPI.term.fetchStudents(courseId, termId),
    enabled,
  });
}

export function useTeachingAssistants(
  courseId: string,
  termId: string,
  enabled = true,
) {
  return useQuery<MembershipCollectionResponse>({
    queryKey: [
      ...membershipQueryKeys.terms.roles[MembershipRole.TeachingAssistant](
        courseId,
        termId,
      ),
    ],
    queryFn: () => membershipAPI.term.fetchTeachingAssistants(courseId, termId),
    enabled,
  });
}
