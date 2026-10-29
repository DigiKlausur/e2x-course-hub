import { useState } from "react";
import { Alert } from "@components/ui/Alert";
import { Card, CardTitle } from "@components/ui/Card";
import { SelectionBox } from "@components/ui/SelectionBox";
import { ImageSelectionDialog } from "@components/dialogs/ImageSelectionDialog";
import { ResourceSelectionDialog } from "@components/dialogs/ResourceSelectionDialog";
import { spawnRoleLabels } from "@domain/roles";
import { describeUnavailable, isChangeableInUi } from "@domain/unavailable";
import type {
  ImageCatalog,
  ImageSelection,
  ResourceCatalog,
  ResourcesSelection,
  SpawnRole,
  UnavailableSelection,
} from "@api/types";

type Dialog = "image" | SpawnRole | null;

interface Props {
  title: string;
  description?: string;
  imageSelection: ImageSelection | null | undefined;
  resourcesSelection: ResourcesSelection | null | undefined;
  imageCatalog: ImageCatalog | undefined;
  resourceCatalog: ResourceCatalog | undefined;
  showTag?: boolean;
  /** When false the configuration is shown read-only, with no way to open a dialog. */
  canEdit?: boolean;
  errorMessage?: string;
  /** Selections no longer in the catalog, listed in a warning under `unavailableTitle`. */
  unavailable?: UnavailableSelection[];
  unavailableTitle?: string;
  onImageConfirm: (selection: ImageSelection) => void;
  onResourceConfirm: (role: SpawnRole, tier: string) => void;
}

export function RuntimeConfigEditor({
  title,
  description,
  imageSelection,
  resourcesSelection,
  imageCatalog,
  resourceCatalog,
  showTag = true,
  canEdit = true,
  errorMessage,
  unavailable = [],
  unavailableTitle,
  onImageConfirm,
  onResourceConfirm,
}: Props) {
  const [openDialog, setOpenDialog] = useState<Dialog>(null);

  const imageFamily = imageSelection?.family
    ? imageCatalog?.families[imageSelection.family]
    : undefined;
  const studentTier = resourcesSelection?.student
    ? resourceCatalog?.student.tiers[resourcesSelection.student]
    : undefined;
  const graderTier = resourcesSelection?.grader
    ? resourceCatalog?.grader.tiers[resourcesSelection.grader]
    : undefined;

  let imageName = imageFamily?.display_name ?? imageSelection?.family ?? "—";
  if (showTag) {
    const tag = imageSelection?.tag ?? imageFamily?.default_tag;
    if (tag) {
      imageName += ` (${tag})`;
    }
  }

  const resourceDescription = (tier: typeof studentTier) =>
    tier?.metadata
      ? Object.entries(tier.metadata)
          .map(([key, value]) => `${key}: ${value}`)
          .join(" · ")
      : undefined;

  return (
    <div>
      <Card>
        <CardTitle>{title}</CardTitle>
        {description && (
          <p className="text-sm text-gray-500 mb-6">{description}</p>
        )}

        {errorMessage && (
          <Alert className="mb-5" title="Could not save the change">
            {errorMessage}
          </Alert>
        )}

        {unavailable.length > 0 && (
          <Alert variant="warning" className="mb-5" title={unavailableTitle}>
            <ul className="list-disc pl-5">
              {unavailable.map((item) => (
                <li key={`${item.kind}-${item.spawn_role}`}>
                  {describeUnavailable(item)}
                </li>
              ))}
            </ul>
            {canEdit && unavailable.some(isChangeableInUi) && (
              <p className="mt-1">Choose a new one below.</p>
            )}
          </Alert>
        )}

        {!canEdit && (
          <Alert variant="info" className="mb-5">
            You do not have permission to change this configuration.
          </Alert>
        )}

        <SelectionBox
          label="Notebook Image"
          title={imageName}
          description={imageFamily?.description}
          onChangeClick={() => setOpenDialog("image")}
          canChange={canEdit}
        />

        <SelectionBox
          label={`${spawnRoleLabels.student} Resources`}
          title={
            studentTier?.display_name ?? resourcesSelection?.student ?? "—"
          }
          description={resourceDescription(studentTier)}
          onChangeClick={() => setOpenDialog("student")}
          infoContent={studentTier?.warning}
          canChange={canEdit}
        />

        <SelectionBox
          label={`${spawnRoleLabels.grader} Resources`}
          title={graderTier?.display_name ?? resourcesSelection?.grader ?? "—"}
          description={resourceDescription(graderTier)}
          onChangeClick={() => setOpenDialog("grader")}
          infoContent={graderTier?.warning}
          canChange={canEdit}
        />
      </Card>

      {imageCatalog && (
        <ImageSelectionDialog
          open={openDialog === "image"}
          onClose={() => setOpenDialog(null)}
          imageSelection={imageSelection ?? null}
          imageCatalog={imageCatalog}
          showTag={showTag}
          onConfirm={(sel) => {
            onImageConfirm(sel);
            setOpenDialog(null);
          }}
        />
      )}

      {resourceCatalog &&
        (openDialog === "student" || openDialog === "grader") && (
          <ResourceSelectionDialog
            open={true}
            onClose={() => setOpenDialog(null)}
            initialTier={
              openDialog === "student"
                ? (resourcesSelection?.student ??
                  resourceCatalog.student.default_tier)
                : (resourcesSelection?.grader ??
                  resourceCatalog.grader.default_tier)
            }
            resourceCatalog={resourceCatalog}
            role={openDialog}
            onConfirm={(tier) => {
              onResourceConfirm(openDialog, tier);
              setOpenDialog(null);
            }}
          />
        )}
    </div>
  );
}
