import { useState, useEffect, useCallback } from "react";
import { courseAPI } from "../api";
import type { CourseDetails } from "../types";

interface UseCourseDetailsOptions {
  courseId: string;
  termId: string;
}

export function useCourseDetails({ courseId, termId }: UseCourseDetailsOptions) {
  const [courseDetails, setCourseDetails] = useState<CourseDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadCourseDetails = useCallback(async () => {
    if (!courseId || !termId) return;

    try {
      setLoading(true);
      setError(null);
      const data = (await courseAPI.fetchCourseDetails(
        courseId,
        termId,
      )) as CourseDetails;
      setCourseDetails(data);
    } catch (err) {
      console.error("Error loading course details:", err);
      setError(
        err instanceof Error ? err.message : "Failed to load course details",
      );
    } finally {
      setLoading(false);
    }
  }, [courseId, termId]);

  useEffect(() => {
    if (courseId && termId) {
      loadCourseDetails();
    }
  }, [courseId, termId, loadCourseDetails]);

  return {
    courseDetails,
    loading,
    error,
    refresh: loadCourseDetails,
  };
}
