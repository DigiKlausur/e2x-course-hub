import { useParams, Link } from "react-router-dom";
import { useCourseDetails, useProfiles } from "../hooks";
import { ProfileCard } from "./ProfileCard";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Button } from "./ui/button";

const ProfileDetailsPage = () => {
  const { courseId, termId } = useParams<{
    courseId: string;
    termId: string;
  }>();

  const { courseDetails, loading: courseLoading } = useCourseDetails({
    courseId: courseId || "",
    termId: termId || "",
  });

  const {
    profiles,
    loading: profilesLoading,
    error,
    refresh,
  } = useProfiles({
    courseId: courseId || "",
    termId: termId || "",
    profileIds: courseDetails?.profiles || [],
  });

  const loading = courseLoading || profilesLoading;

  if (!courseId || !termId) {
    return (
      <div className="p-10 text-center text-destructive">
        Invalid course parameters
      </div>
    );
  }

  return (
    <div className="max-w-[1400px] mx-auto p-5">
      <Breadcrumb className="mb-5">
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink asChild>
              <Link to="/">Courses</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbLink asChild>
              <Link to={`/course/${courseId}/${termId}`}>
                {courseDetails
                  ? `${courseDetails.course_name} - ${courseDetails.term_id}`
                  : "Course Details"}
              </Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>Profiles</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-2">
          Profiles for {courseDetails?.course_name}
        </h2>
        {courseDetails && (
          <p className="text-muted-foreground text-sm">
            Course ID:{" "}
            <span className="font-mono">{courseDetails.course_id}</span> | Term:{" "}
            <span className="font-mono">{courseDetails.term_id}</span>
          </p>
        )}
      </div>

      {loading ? (
        <div className="p-10 text-center text-muted-foreground">
          Loading profiles...
        </div>
      ) : error ? (
        <div className="p-10 text-center">
          <p className="text-destructive mb-4">Error: {error}</p>
          <Button onClick={refresh}>Retry</Button>
        </div>
      ) : profiles.length === 0 ? (
        <div className="p-10 text-center">
          <p className="text-muted-foreground">
            No profiles configured for this course.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="text-sm text-muted-foreground mb-4">
            Showing {profiles.length} profile{profiles.length !== 1 ? "s" : ""}
          </div>
          {profiles.map((profile) => (
            <ProfileCard key={profile.name} profile={profile} />
          ))}
        </div>
      )}
    </div>
  );
};

export default ProfileDetailsPage;
