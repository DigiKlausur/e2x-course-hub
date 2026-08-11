import { useTermEnvironment, useUpdateTermEnvironment } from "@hooks/course";
import { useImageCatalog, useResourceCatalog } from "@hooks/catalog";
import { RuntimeConfigEditor } from "@components/infrastructure/RuntimeConfigEditor";
import type { ImageSelection } from "@api/types";

interface Props {
  courseId: string;
  termId: string;
}

export function TermRuntimeTab({ courseId, termId }: Props) {
  const { data: termEnvironment } = useTermEnvironment(courseId, termId);
  const { data: imageCatalog } = useImageCatalog();
  const { data: resourceCatalog } = useResourceCatalog();

  const updateTermEnvironment = useUpdateTermEnvironment(courseId, termId);

  const handleImageConfirm = (selection: ImageSelection) => {
    updateTermEnvironment.mutate({ ...termEnvironment, image: selection });
  };

  const handleResourceConfirm = (role: "student" | "grader", tier: string) => {
    updateTermEnvironment.mutate({
      ...termEnvironment,
      resources: { ...termEnvironment?.resources, [role]: tier },
    });
  };

  return (
    <RuntimeConfigEditor
      title="Term Runtime"
      imageSelection={termEnvironment?.image}
      resourcesSelection={termEnvironment?.resources}
      imageCatalog={imageCatalog?.catalog}
      resourceCatalog={resourceCatalog?.catalog}
      onImageConfirm={handleImageConfirm}
      onResourceConfirm={handleResourceConfirm}
    />
  );
}
