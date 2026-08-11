import {
  useCourseEnvironment,
  useUpdateCourseEnvironment,
} from "@hooks/course";

import { useImageCatalog, useResourceCatalog } from "@hooks/catalog";
import { RuntimeConfigEditor } from "@components/infrastructure/RuntimeConfigEditor";
import type { ImageSelection } from "@api/types";

interface Props {
  courseId: string;
}

export function CourseTemplateTab({ courseId }: Props) {
  const { data: environment } = useCourseEnvironment(courseId);
  const { data: imageCatalog } = useImageCatalog();
  const { data: resourceCatalog } = useResourceCatalog();

  const updateEnvironment = useUpdateCourseEnvironment(courseId);

  const handleImageConfirm = (selection: ImageSelection) => {
    updateEnvironment.mutate({ image: selection });
  };

  const handleResourceConfirm = (role: "student" | "grader", tier: string) => {
    updateEnvironment.mutate({
      resources: {
        ...environment?.resources,
        [role]: tier,
      },
    });
  };

  return (
    <RuntimeConfigEditor
      title="Term Runtime Template"
      description="These settings are copied when creating a new term. Existing terms are not changed."
      imageSelection={environment?.image}
      resourcesSelection={environment?.resources}
      imageCatalog={imageCatalog?.catalog}
      resourceCatalog={resourceCatalog?.catalog}
      onImageConfirm={handleImageConfirm}
      onResourceConfirm={handleResourceConfirm}
      showTag={false}
    />
  );
}
