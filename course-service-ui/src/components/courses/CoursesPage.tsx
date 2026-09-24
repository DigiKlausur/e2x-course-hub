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
import { Alert } from "@components/ui/Alert";
import { DataTable } from "@components/ui/DataTable";
import type { DataTableColumn } from "@components/ui/DataTable";
import { CreateCourseDialog } from "@components/dialogs/CreateCourseDialog";
import { getErrorMessage } from "@/lib/errorMessage";
import { courseCollectionCapabilityText } from "@domain/capabilities";
import type { CourseSummaryResponse } from "@/api/types";

const PAGE_SIZE_KEY = "course-table-page-size";

const columns: DataTableColumn<CourseSummaryResponse>[] = [
  {
    id: "course_id",
    header: "Course ID",
    cell: (course) => (
      <Link
        to={`/course/${course.metadata.course_id}`}
        className="font-semibold text-hbrs-dark-blue hover:text-hbrs-medium-blue hover:underline"
      >
        {course.metadata.course_id}
      </Link>
    ),
    sortAccessor: (course) => course.metadata.course_id.toLowerCase(),
  },
  {
    id: "course_name",
    header: "Name",
    cell: (course) => (
      <span className="text-gray-800">{course.metadata.course_name}</span>
    ),
  },
  {
    id: "description",
    header: "Description",
    cell: (course) => (
      <span className="text-gray-500">
        {course.metadata.description ?? "—"}
      </span>
    ),
  },
];

function matchesQuery(course: CourseSummaryResponse, query: string): boolean {
  return (
    course.metadata.course_id.toLowerCase().includes(query) ||
    course.metadata.course_name.toLowerCase().includes(query) ||
    (course.metadata.description?.toLowerCase().includes(query) ?? false)
  );
}

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
  const canCreateCourse = capabilities?.createCourse ?? false;

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
        <h1 className="text-3xl font-bold text-gray-900 m-0">Courses</h1>
        <p className="mt-1 text-gray-500">Manage your courses and terms</p>
      </header>

      <CreateCourseDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        existingCourseIds={courses?.map((c) => c.metadata.course_id) ?? []}
        onCreate={handleCreate}
        isSubmitting={createCourse.isPending}
      />

      <div className="max-w-5xl mx-auto px-10 py-8">
        {createCourse.error && (
          <Alert className="mb-6" title="Could not create the course">
            {getErrorMessage(createCourse.error)}
          </Alert>
        )}
        {isLoading && <p className="text-gray-500">Loading courses…</p>}
        {error && (
          <Alert className="mb-6" title="Failed to load courses">
            {getErrorMessage(error)}
          </Alert>
        )}
        {courses && (
          <div className="bg-white border border-gray-200 rounded-xl overflow-hidden p-4">
            {canCreateCourse && (
              <div className="mb-4 flex justify-end">
                <Button
                  variant="primary"
                  onClick={() => setDialogOpen(true)}
                  title={
                    courseCollectionCapabilityText.createCourse.description
                  }
                  className="px-3 py-2 text-xs"
                >
                  + {courseCollectionCapabilityText.createCourse.label}
                </Button>
              </div>
            )}
            <DataTable
              rows={courses}
              getRowId={(course) => course.metadata.course_id}
              columns={columns}
              pageSizeStorageKey={PAGE_SIZE_KEY}
              defaultSort={{ columnId: "course_id", direction: "asc" }}
              emptyMessage="No courses found."
              noMatchMessage="No matching courses."
              filter={{
                placeholder: "Search courses...",
                predicate: matchesQuery,
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
}
