import { useQuery } from "@tanstack/react-query";
import { membershipAPI } from "@api";
import type { MembershipCollectionResponse } from "@api/types";
import { membershipQueryKeys } from "./keys";
import { MembershipRole } from "@domain/roles";

export function useHubAdmins() {
  return useQuery<MembershipCollectionResponse>({
    queryKey: [...membershipQueryKeys.hub.roles[MembershipRole.Admin]()],
    queryFn: () => membershipAPI.hub.fetchHubAdmins(),
  });
}

export function useCourseCreators() {
  return useQuery<MembershipCollectionResponse>({
    queryKey: [
      ...membershipQueryKeys.hub.roles[MembershipRole.CourseCreator](),
    ],
    queryFn: () => membershipAPI.hub.fetchCourseCreators(),
  });
}

export function useCourseOwners(courseId: string) {
  return useQuery<MembershipCollectionResponse>({
    queryKey: [
      ...membershipQueryKeys.courses.roles[MembershipRole.CourseOwner](
        courseId,
      ),
    ],
    queryFn: () => membershipAPI.course.fetchOwners(courseId),
  });
}

export function useInstructors(courseId: string, termId: string) {
  return useQuery<MembershipCollectionResponse>({
    queryKey: [
      ...membershipQueryKeys.terms.roles[MembershipRole.Instructor](
        courseId,
        termId,
      ),
    ],
    queryFn: () => membershipAPI.term.fetchInstructors(courseId, termId),
  });
}

export function useObservers(courseId: string, termId: string) {
  return useQuery<MembershipCollectionResponse>({
    queryKey: [
      ...membershipQueryKeys.terms.roles[MembershipRole.Observer](
        courseId,
        termId,
      ),
    ],
    queryFn: () => membershipAPI.term.fetchObservers(courseId, termId),
  });
}

export function useStudents(courseId: string, termId: string) {
  return useQuery<MembershipCollectionResponse>({
    queryKey: [
      ...membershipQueryKeys.terms.roles[MembershipRole.Student](
        courseId,
        termId,
      ),
    ],
    queryFn: () => membershipAPI.term.fetchStudents(courseId, termId),
  });
}

export function useTeachingAssistants(courseId: string, termId: string) {
  return useQuery<MembershipCollectionResponse>({
    queryKey: [
      ...membershipQueryKeys.terms.roles[MembershipRole.TeachingAssistant](
        courseId,
        termId,
      ),
    ],
    queryFn: () => membershipAPI.term.fetchTeachingAssistants(courseId, termId),
  });
}
