import { useState } from "react";
import { Card, CardTitle } from "@components/ui/Card";
import { Button } from "@components/ui/Button";
import { useCourseMetadata, useUpdateCourseMetadata } from "@hooks/course";

interface Props {
  courseId: string;
}

export function CourseSettingsTab({ courseId }: Props) {
  const { data: metadata } = useCourseMetadata(courseId);
  const updateMetadata = useUpdateCourseMetadata(courseId);

  const [name, setName] = useState<string>("");
  const [description, setDescription] = useState<string>("");

  // Populate form once metadata loads
  const currentName = name || metadata?.course_name || "";
  const currentDescription = description || metadata?.description || "";

  const handleSave = () => {
    updateMetadata.mutate({
      course_name: currentName,
      description: currentDescription,
    });
  };

  return (
    <div className="grid grid-cols-[2fr_1fr] gap-6">
      <div>
        <Card>
          <CardTitle>Course Settings</CardTitle>

          <div className="mb-5">
            <label className="block text-sm font-semibold mb-2">
              Course Name
            </label>
            <input
              value={currentName}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-hbrs-dark-blue"
            />
          </div>

          <div className="mb-5">
            <label className="block text-sm font-semibold mb-2">
              Description
            </label>
            <input
              value={currentDescription}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-hbrs-dark-blue"
            />
          </div>

          <Button
            variant="primary"
            onClick={handleSave}
            disabled={updateMetadata.isPending}
          >
            {updateMetadata.isPending ? "Saving…" : "Save Changes"}
          </Button>
        </Card>
      </div>

      <div>
        <Card>
          <CardTitle>Danger Zone</CardTitle>
          <p className="text-sm text-gray-500 mb-4">
            Permanently delete this course and all its terms.
          </p>
          <Button variant="danger">Delete Course</Button>
        </Card>
      </div>
    </div>
  );
}
