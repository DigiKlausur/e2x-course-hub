import { useCourse, useUpdateCourseEnvironment } from "@hooks/course";

import { useImageCatalog, useResourceCatalog } from "@hooks/catalog";
import { RuntimeConfigEditor } from "@components/infrastructure/RuntimeConfigEditor";
import { getErrorMessage } from "@/lib/errorMessage";
import type { ImageSelection, SpawnRole } from "@api/types";

interface Props {
  courseId: string;
}

export function CourseTemplateTab({ courseId }: Props) {
  const { data: course } = useCourse(courseId);
  const environment = course?.environment;
  const canEdit = course?.capabilities.selectEnvironment ?? false;

  const { data: imageCatalog } = useImageCatalog();
  const { data: resourceCatalog } = useResourceCatalog();

  const updateEnvironment = useUpdateCourseEnvironment(courseId);

  const handleImageConfirm = (selection: ImageSelection) => {
    updateEnvironment.mutate({ image: selection });
  };

  const handleResourceConfirm = (role: SpawnRole, tier: string) => {
    updateEnvironment.mutate({ resources: { [role]: tier } });
  };

  return (
    <RuntimeConfigEditor
      title="Term Runtime Template"
      description="These settings are copied when creating a new term. Existing terms are not changed."
      imageSelection={environment?.image}
      resourcesSelection={environment?.resources}
      imageCatalog={imageCatalog?.catalog}
      resourceCatalog={resourceCatalog?.catalog}
      canEdit={canEdit}
      errorMessage={
        updateEnvironment.error
          ? getErrorMessage(updateEnvironment.error)
          : undefined
      }
      onImageConfirm={handleImageConfirm}
      onResourceConfirm={handleResourceConfirm}
      showTag={false}
    />
  );
}
