import { useState, useEffect, useCallback } from "react";
import { courseMemberAPI, courseAPI } from "../api";
import type { CourseMember } from "../types";

interface UseCourseMembers {
  courseId: string;
  termId: string;
}

export function useCourseMembers({ courseId, termId }: UseCourseMembers) {
  const [members, setMembers] = useState<CourseMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadMembers = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = (await courseMemberAPI.fetchCourseMembers(
        courseId,
        termId,
      )) as CourseMember[];
      setMembers(data);
    } catch (err) {
      console.error("Error loading course members:", err);
      setError(
        err instanceof Error ? err.message : "Failed to load course members",
      );
    } finally {
      setLoading(false);
    }
  }, [courseId, termId]);

  useEffect(() => {
    loadMembers();
  }, [loadMembers]);

  return {
    members,
    loading,
    error,
    refresh: loadMembers,
  };
}

export function useAssignableRoles(courseId: string, termId: string) {
  const [assignableRoles, setAssignableRoles] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadAssignableRoles = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await courseAPI.fetchAssignableRoles(courseId, termId);
      setAssignableRoles(data.roles);
    } catch (err) {
      console.error("Error loading assignable roles:", err);
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load assignable roles",
      );
    } finally {
      setLoading(false);
    }
  }, [courseId, termId]);

  useEffect(() => {
    loadAssignableRoles();
  }, [loadAssignableRoles]);

  return {
    assignableRoles,
    loading,
    error,
    refresh: loadAssignableRoles,
  };
}
