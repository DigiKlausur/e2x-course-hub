import { Routes, Route, Navigate } from "react-router-dom";
import { TabBar } from "@components/ui/TabBar";
import { YourAccessButton } from "@components/actions/YourAccessButton";
import { useCourses } from "@hooks/course";
import { lmsActionText } from "@domain/actions";
import { MembershipRole, memberLabels } from "@domain/roles";
import { CourseListTab } from "./tabs/CourseListTab";
import { LMSAdminsTab } from "./tabs/LMSAdminsTab";
import { CourseCreatorsTab } from "./tabs/CourseCreatorsTab";

export function CoursesPage() {
  const { data: { actions } = {} } = useCourses();

  // Only offer a tab the user can actually use. As on the course page, the
  // routes below stay mounted so a bookmarked URL still resolves, and each tab
  // explains itself when the user may not view it.
  const tabs = [
    { label: "Courses", to: "/", show: true },
    {
      label: memberLabels[MembershipRole.Admin].plural,
      to: "/lms-admins",
      show: actions?.members.lmsAdmins.list ?? false,
    },
    {
      label: memberLabels[MembershipRole.CourseCreator].plural,
      to: "/course-creators",
      show: actions?.members.courseCreators.list ?? false,
    },
  ].filter((tab) => tab.show);

  return (
    <div>
      <header className="bg-white border-b border-gray-200 px-10 py-8 flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 m-0">Courses</h1>
          <p className="mt-1 text-gray-500">
            Manage your courses and semesters
          </p>
        </div>
        {actions && (
          <YourAccessButton
            actions={actions}
            texts={lmsActionText}
            scope="across the LMS"
          />
        )}
      </header>

      <TabBar tabs={tabs} />

      <div className="max-w-5xl mx-auto px-10 py-8">
        <Routes>
          <Route index element={<CourseListTab />} />
          <Route path="lms-admins" element={<LMSAdminsTab />} />
          <Route path="course-creators" element={<CourseCreatorsTab />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </div>
  );
}
