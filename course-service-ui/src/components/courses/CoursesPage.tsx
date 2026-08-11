import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useCourses, useCreateCourse } from "@hooks/course";
import {
  useImageCatalog,
  useProfileCatalog,
  useResourceCatalog,
} from "@hooks/catalog";
import { buildDefaultCourseConfig } from "../../lib/buildDefaultCourseConfig";
import { Button } from "@components/ui/Button";
import { CreateCourseDialog } from "@components/dialogs/CreateCourseDialog";

export function CoursesPage() {
  const navigate = useNavigate();
  const {
    data: { courses, capabilities } = {},
    isLoading,
    error,
  } = useCourses();
  const createCourse = useCreateCourse();
  const imageCatalog = useImageCatalog();
  const resourceCatalog = useResourceCatalog();
  const profileCatalog = useProfileCatalog();

  const [dialogOpen, setDialogOpen] = useState(false);

  const handleCreate = async (data: {
    courseId: string;
    courseName: string;
    description: string;
  }) => {
    const config = buildDefaultCourseConfig({
      ...data,
      imageCatalog: imageCatalog.data?.catalog,
      resourceCatalog: resourceCatalog.data?.catalog,
      profileCatalog: profileCatalog.data?.catalog,
    });
    if (!config) return;
    await createCourse.mutateAsync(config);
    navigate(`/course/${data.courseId}`);
  };

  return (
    <div>
      <header className="bg-white border-b border-gray-200 px-10 py-8">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 m-0">Courses</h1>
            <p className="mt-1 text-gray-500">Manage your courses and terms</p>
          </div>
          <Button variant="primary" onClick={() => setDialogOpen(true)}>
            + Create Course
          </Button>
        </div>
      </header>

      {capabilities?.createCourse === false ? (
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3">
          <p>You are not allowed to create courses.</p>
        </div>
      ) : (
        <CreateCourseDialog
          open={dialogOpen}
          onClose={() => setDialogOpen(false)}
          existingCourseIds={courses?.map((c) => c.metadata.course_id) ?? []}
          onCreate={handleCreate}
          isSubmitting={createCourse.isPending}
        />
      )}

      <div className="max-w-5xl mx-auto px-10 py-8">
        {isLoading && <p className="text-gray-500">Loading courses…</p>}
        {error && <p className="text-red-600">Failed to load courses.</p>}
        {courses && (
          <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-sky-50 text-left">
                  <th className="px-6 py-3 font-semibold text-gray-700">
                    Course ID
                  </th>
                  <th className="px-6 py-3 font-semibold text-gray-700">
                    Name
                  </th>
                  <th className="px-6 py-3 font-semibold text-gray-700">
                    Description
                  </th>
                </tr>
              </thead>
              <tbody>
                {courses.map((course) => (
                  <tr
                    key={course.metadata.course_id}
                    className="border-t border-gray-100 hover:bg-gray-50 transition-colors"
                  >
                    <td className="px-6 py-4 font-semibold">
                      <Link
                        to={`/course/${course.metadata.course_id}`}
                        className="text-hbrs-dark-blue hover:text-hbrs-medium-blue hover:underline"
                      >
                        {course.metadata.course_id}
                      </Link>
                    </td>
                    <td className="px-6 py-4 text-gray-800">
                      {course.metadata.course_name}
                    </td>
                    <td className="px-6 py-4 text-gray-500">
                      {course.metadata.description ?? "—"}
                    </td>
                  </tr>
                ))}
                {courses.length === 0 && (
                  <tr>
                    <td
                      colSpan={3}
                      className="px-6 py-8 text-center text-gray-400"
                    >
                      No courses found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
