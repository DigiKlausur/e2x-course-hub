import { Link, Routes, Route, Navigate, useParams } from "react-router-dom";
import { TabBar } from "@components/ui/TabBar";
import { useCourseMetadata } from "@hooks/course";
import { CourseOverviewTab } from "./tabs/CourseOverviewTab";
import { CourseTermsTab } from "./tabs/CourseTermsTab";
import { CourseOwnersTab } from "./tabs/CourseOwnersTab";
import { CourseTemplateTab } from "./tabs/CourseTemplateTab";
import { CourseSettingsTab } from "./tabs/CourseSettingsTab";

export function CoursePage() {
  const { courseId } = useParams<{ courseId: string }>();

  const { data: metadata, isLoading } = useCourseMetadata(courseId!);

  const base = `/course/${courseId}`;
  const tabs = [
    { label: "Overview", to: base },
    { label: "Course Owners", to: `${base}/owners` },
    { label: "Semesters", to: `${base}/terms` },
    { label: "Image & Resource Defaults", to: `${base}/template` },
    { label: "Settings", to: `${base}/settings` },
  ];

  return (
    <div>
      <header className="bg-white border-b border-gray-200 px-10 py-8">
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
      </header>

      <TabBar tabs={tabs} />

      <div className="px-10 py-8">
        <Routes>
          <Route index element={<CourseOverviewTab courseId={courseId!} />} />
          <Route
            path="terms"
            element={<CourseTermsTab courseId={courseId!} />}
          />
          <Route
            path="owners"
            element={<CourseOwnersTab courseId={courseId!} />}
          />
          <Route
            path="template"
            element={<CourseTemplateTab courseId={courseId!} />}
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
