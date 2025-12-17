import { useState, useEffect, useCallback } from "react";
import { profileAPI } from "../api";
import type { Profile } from "../types";

interface UseProfilesOptions {
  courseId: string;
  termId: string;
  profileIds: string[];
}

export function useProfiles({ courseId, termId, profileIds }: UseProfilesOptions) {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadProfiles = useCallback(async () => {
    if (!courseId || !termId || profileIds.length === 0) {
      setProfiles([]);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const profilePromises = profileIds.map((profileId) =>
        profileAPI.fetchProfile(courseId, termId, profileId),
      );

      const fetchedProfiles = await Promise.all(profilePromises);
      setProfiles(fetchedProfiles);
    } catch (err) {
      console.error("Error loading profiles:", err);
      setError(err instanceof Error ? err.message : "Failed to load profiles");
    } finally {
      setLoading(false);
    }
  }, [courseId, termId, profileIds]);

  useEffect(() => {
    loadProfiles();
  }, [loadProfiles]);

  return {
    profiles,
    loading,
    error,
    refresh: loadProfiles,
  };
}
