import { useState, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import { useCourseDetails } from "../hooks";
import CourseMemberTable, {
  type CourseMemberTableRef,
} from "./CourseMemberTable";
import { AddUsersToCourseDialog } from "./dialogs";
import { CourseDetailCard } from "./CourseDetailCard";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";

const CourseDetailPage = () => {
  const { courseId, termId } = useParams<{
    courseId: string;
    termId: string;
  }>();

  const { courseDetails, loading } = useCourseDetails({
    courseId: courseId || "",
    termId: termId || "",
  });

  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedRole, setSelectedRole] = useState<string>("");
  const memberTableRef = useRef<CourseMemberTableRef>(null);

  const handleAddMembers = (role: string) => {
    setSelectedRole(role);
    setShowAddModal(true);
  };

  const handleCloseModal = () => {
    setShowAddModal(false);
  };

  const handleAddSuccess = () => {
    // Refresh the member table
    memberTableRef.current?.refresh();
  };

  if (!courseId || !termId) {
    return (
      <div className="p-10 text-center text-destructive">
        Invalid course parameters
      </div>
    );
  }

  return (
    <div className="max-w-[1400px] mx-auto p-5 grid gap-6">
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink asChild>
              <Link to="/">Courses</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>
              {courseDetails
                ? `${courseDetails.course_name} - ${courseDetails.term_id}`
                : "Course Details"}
            </BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      {loading ? (
        <div className="p-10 text-center text-muted-foreground">
          Loading course details...
        </div>
      ) : (
        <>
          {courseDetails && <CourseDetailCard courseDetails={courseDetails} />}

          <CourseMemberTable
            ref={memberTableRef}
            courseId={courseId}
            termId={termId}
            onAddMembers={handleAddMembers}
          />
        </>
      )}

      {showAddModal && courseId && termId && selectedRole && (
        <AddUsersToCourseDialog
          courseId={courseId}
          termId={termId}
          role={selectedRole}
          open={showAddModal}
          onClose={handleCloseModal}
          onSuccess={handleAddSuccess}
        />
      )}
    </div>
  );
};

export default CourseDetailPage;
