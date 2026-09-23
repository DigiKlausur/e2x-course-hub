import { Link, Routes, Route, Navigate, useParams } from "react-router-dom";
import { TabBar } from "@components/ui/TabBar";
import { useCourseMetadata, useTerm } from "@hooks/course";
import { TermOverviewTab } from "./tabs/TermOverviewTab";
import { TermSettingsTab } from "./tabs/TermSettingsTab";

export function TermPage() {
  const { courseId, termId } = useParams<{
    courseId: string;
    termId: string;
  }>();

  const { data: courseMetadata } = useCourseMetadata(courseId!);
  const { data: term } = useTerm(courseId!, termId!);
  const capabilities = term?.capabilities;

  const base = `/course/${courseId}/term/${termId}`;
  // Same rule as CoursePage: only offer a tab the user can use.
  const tabs = [
    { label: "Overview", to: base, show: true },
    {
      label: "Settings",
      to: `${base}/settings`,
      show: capabilities?.removeTerm ?? false,
    },
  ].filter((tab) => tab.show);

  return (
    <div>
      <header className="bg-white border-b border-gray-200 px-10 py-8">
        <div className="text-sm text-gray-400 mb-1">
          <Link to="/" className="hover:text-hbrs-dark-blue hover:underline">
            Courses
          </Link>
          {" / "}
          <Link
            to={`/course/${courseId}`}
            className="hover:text-hbrs-dark-blue hover:underline"
          >
            {courseId}
          </Link>
          {" / "}
          <span className="text-gray-700 font-medium">{termId}</span>
        </div>
        <h1 className="text-3xl font-bold text-gray-900 m-0">
          {courseId} · {termId}
        </h1>
        {courseMetadata?.course_name && (
          <p className="mt-1 text-gray-500">{courseMetadata.course_name}</p>
        )}
      </header>

      <TabBar tabs={tabs} />

      <div className="px-10 py-8">
        <Routes>
          <Route
            index
            element={<TermOverviewTab courseId={courseId!} termId={termId!} />}
          />
          <Route
            path="settings"
            element={<TermSettingsTab courseId={courseId!} termId={termId!} />}
          />
          <Route path="*" element={<Navigate to={base} replace />} />
        </Routes>
      </div>
    </div>
  );
}
