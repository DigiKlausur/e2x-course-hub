import { useTermEnvironment, useUpdateTermEnvironment } from "@hooks/course";
import { useImageCatalog, useResourceCatalog } from "@hooks/catalog";
import { RuntimeConfigEditor } from "@components/infrastructure/RuntimeConfigEditor";
import type { ImageSelection, SpawnRole } from "@api/types";

interface Props {
  courseId: string;
  termId: string;
}

export function TermRuntimeTab({ courseId, termId }: Props) {
  const { data: termEnvironment } = useTermEnvironment(courseId, termId);
  const { data: imageCatalog } = useImageCatalog();
  const { data: resourceCatalog } = useResourceCatalog();

  const updateTermEnvironment = useUpdateTermEnvironment(courseId, termId);

  // Send only what changed: the backend merges each key it receives and leaves
  // the rest alone, so echoing the whole fetched environment back would only
  // risk overwriting a concurrent edit with stale values.
  const handleImageConfirm = (selection: ImageSelection) => {
    updateTermEnvironment.mutate({ image: selection });
  };

  const handleResourceConfirm = (role: SpawnRole, tier: string) => {
    updateTermEnvironment.mutate({ resources: { [role]: tier } });
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
