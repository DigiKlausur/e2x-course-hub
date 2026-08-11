import { useMutation, useQueryClient } from "@tanstack/react-query";
import { membershipAPI } from "@api";
import type { MembershipPatch } from "@api/types";
import { membershipQueryKeys } from "./keys";
import { MembershipRole } from "@domain/roles";

export function useUpdateHubAdmins() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (updates: MembershipPatch) => {
      await membershipAPI.hub.updateHubAdmins(updates);
    },
    onSuccess: () => {
      // Invalidate the course admins query to refetch the updated data
      queryClient.invalidateQueries({
        queryKey: [...membershipQueryKeys.hub.roles[MembershipRole.Admin]()],
      });
    },
    onError: (error) => {
      console.error("Error updating course admins:", error);
    },
  });
}

export function useUpdateCourseCreators() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (updates: MembershipPatch) => {
      await membershipAPI.hub.updateCourseCreators(updates);
    },
    onSuccess: () => {
      // Invalidate the course creators query to refetch the updated data
      queryClient.invalidateQueries({
        queryKey: [
          ...membershipQueryKeys.hub.roles[MembershipRole.CourseCreator](),
        ],
      });
    },
    onError: (error) => {
      console.error("Error updating course creators:", error);
    },
  });
}

export function useUpdateCourseOwners(courseId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (updates: MembershipPatch) => {
      await membershipAPI.course.updateOwners(courseId, updates);
    },
    onSuccess: () => {
      // Invalidate the course owners query to refetch the updated data
      queryClient.invalidateQueries({
        queryKey: [
          ...membershipQueryKeys.courses.roles[MembershipRole.CourseOwner](
            courseId,
          ),
        ],
      });
    },
    onError: (error) => {
      console.error("Error updating course owners:", error);
    },
  });
}

export function useUpdateInstructors(courseId: string, termId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (updates: MembershipPatch) => {
      await membershipAPI.term.updateInstructors(courseId, termId, updates);
    },
    onSuccess: () => {
      // Invalidate the course instructors query to refetch the updated data
      queryClient.invalidateQueries({
        queryKey: [
          ...membershipQueryKeys.terms.roles[MembershipRole.Instructor](
            courseId,
            termId,
          ),
        ],
      });
    },
    onError: (error) => {
      console.error("Error updating course instructors:", error);
    },
  });
}

export function useUpdateObservers(courseId: string, termId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (updates: MembershipPatch) => {
      await membershipAPI.term.updateObservers(courseId, termId, updates);
    },
    onSuccess: () => {
      // Invalidate the course observers query to refetch the updated data
      queryClient.invalidateQueries({
        queryKey: [
          ...membershipQueryKeys.terms.roles[MembershipRole.Observer](
            courseId,
            termId,
          ),
        ],
      });
    },
    onError: (error) => {
      console.error("Error updating course observers:", error);
    },
  });
}

export function useUpdateStudents(courseId: string, termId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (updates: MembershipPatch) => {
      await membershipAPI.term.updateStudents(courseId, termId, updates);
    },
    onSuccess: () => {
      // Invalidate the course students query to refetch the updated data
      queryClient.invalidateQueries({
        queryKey: [
          ...membershipQueryKeys.terms.roles[MembershipRole.Student](
            courseId,
            termId,
          ),
        ],
      });
    },
    onError: (error) => {
      console.error("Error updating course students:", error);
    },
  });
}

export function useUpdateTeachingAssistants(courseId: string, termId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (updates: MembershipPatch) => {
      await membershipAPI.term.updateTeachingAssistants(
        courseId,
        termId,
        updates,
      );
    },
    onSuccess: () => {
      // Invalidate the course teaching assistants query to refetch the updated data
      queryClient.invalidateQueries({
        queryKey: [
          ...membershipQueryKeys.terms.roles[MembershipRole.TeachingAssistant](
            courseId,
            termId,
          ),
        ],
      });
    },
    onError: (error) => {
      console.error("Error updating course teaching assistants:", error);
    },
  });
}
