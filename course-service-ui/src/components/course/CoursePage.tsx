import { Link, Routes, Route, Navigate, useParams } from "react-router-dom";
import { TabBar } from "@components/ui/TabBar";
import { YourAccessButton } from "@components/actions/YourAccessButton";
import { useCourse } from "@hooks/course";
import { courseActionText } from "@domain/actions";
import { MembershipRole, memberLabels } from "@domain/roles";
import { CourseOverviewTab } from "./tabs/CourseOverviewTab";
import { CourseOwnersTab } from "./tabs/CourseOwnersTab";
import { CourseSettingsTab } from "./tabs/CourseSettingsTab";

export function CoursePage() {
  const { courseId } = useParams<{ courseId: string }>();

  const { data: course, isLoading } = useCourse(courseId!);
  const metadata = course?.metadata;
  const actions = course?.actions;

  const base = `/course/${courseId}`;
  // Only offer a tab the user can actually use. The routes below stay mounted
  // regardless, so a bookmarked URL still resolves — each tab does its own
  // permission check and explains itself rather than 404ing.
  const tabs = [
    { label: "Overview", to: base, show: true },
    {
      label: memberLabels[MembershipRole.CourseOwner].plural,
      to: `${base}/owners`,
      show: actions?.members.courseOwners.list ?? false,
    },
    {
      label: "Settings",
      to: `${base}/settings`,
      show: (actions?.metadata.edit || actions?.remove) ?? false,
    },
  ].filter((tab) => tab.show);

  return (
    <div>
      <header className="bg-white border-b border-gray-200 px-10 py-8 flex items-start justify-between gap-4">
        <div>
          <div className="text-sm text-gray-400 mb-1">
            <Link to="/" className="hover:text-hbrs-dark-blue hover:underline">
              Courses
            </Link>
            {" / "}
            <span className="text-gray-700 font-medium">{courseId}</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 m-0">
            {isLoading ? courseId : (metadata?.course_name ?? courseId)}
          </h1>
          {metadata?.description && (
            <p className="mt-1 text-gray-500">{metadata.description}</p>
          )}
        </div>
        {actions && (
          <YourAccessButton
            actions={actions}
            texts={courseActionText}
            scope="in this course"
          />
        )}
      </header>

      <TabBar tabs={tabs} />

      <div className="px-10 py-8">
        <Routes>
          <Route index element={<CourseOverviewTab courseId={courseId!} />} />
          <Route
            path="owners"
            element={<CourseOwnersTab courseId={courseId!} />}
          />
          <Route
            path="settings"
            element={<CourseSettingsTab courseId={courseId!} />}
          />
          <Route path="*" element={<Navigate to={base} replace />} />
        </Routes>
      </div>
    </div>
  );
}
