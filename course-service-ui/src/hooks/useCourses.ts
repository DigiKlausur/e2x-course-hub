import { useState, useEffect, useCallback } from "react";
import { courseAPI } from "../api";
import type { Course, CoursesResponse } from "../types";

export function useCourses() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadCourses = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = (await courseAPI.fetchCourses()) as CoursesResponse;

      // Flatten the nested structure
      const coursesArray = Object.values(data.courses);

      setCourses(coursesArray);
    } catch (err) {
      console.error("Error loading courses:", err);
      setError(err instanceof Error ? err.message : "Failed to load courses");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCourses();
  }, [loadCourses]);

  return {
    courses,
    loading,
    error,
    refresh: loadCourses,
  };
}
