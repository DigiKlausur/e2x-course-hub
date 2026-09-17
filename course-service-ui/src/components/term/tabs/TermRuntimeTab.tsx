import { useTerm, useUpdateTermEnvironment } from "@hooks/course";
import { useImageCatalog, useResourceCatalog } from "@hooks/catalog";
import { RuntimeConfigEditor } from "@components/infrastructure/RuntimeConfigEditor";
import { getErrorMessage } from "@/lib/errorMessage";
import type { ImageSelection, SpawnRole } from "@api/types";

interface Props {
  courseId: string;
  termId: string;
}

export function TermRuntimeTab({ courseId, termId }: Props) {
  const { data: term } = useTerm(courseId, termId);
  const termEnvironment = term?.environment;

  // NOTE: there is no term-level equivalent of CourseCapabilities.selectEnvironment,
  // even though TERM_SELECT_IMAGE / _RESOURCES / _PROFILES exist as permissions.
  // Until TermCapabilities exposes one, the editor stays enabled and an
  // unauthorised change is reported by the backend instead of being prevented.

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
      errorMessage={
        updateTermEnvironment.error
          ? getErrorMessage(updateTermEnvironment.error)
          : undefined
      }
      onImageConfirm={handleImageConfirm}
      onResourceConfirm={handleResourceConfirm}
    />
  );
}
