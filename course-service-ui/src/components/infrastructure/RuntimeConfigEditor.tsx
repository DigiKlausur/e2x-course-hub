import { useState } from "react";
import { Card, CardTitle } from "@components/ui/Card";
import { SelectionBox } from "@components/ui/SelectionBox";
import { ImageSelectionDialog } from "@components/dialogs/ImageSelectionDialog";
import { ResourceSelectionDialog } from "@components/dialogs/ResourceSelectionDialog";
import type {
  ImageCatalog,
  ImageSelection,
  ResourceCatalog,
  ResourcesSelection,
} from "@api/types";

type Dialog = "image" | "student" | "grader" | null;

interface Props {
  title: string;
  description?: string;
  imageSelection: ImageSelection | null | undefined;
  resourcesSelection: ResourcesSelection | null | undefined;
  imageCatalog: ImageCatalog | undefined;
  resourceCatalog: ResourceCatalog | undefined;
  showTag?: boolean;
  onImageConfirm: (selection: ImageSelection) => void;
  onResourceConfirm: (role: "student" | "grader", tier: string) => void;
}

export function RuntimeConfigEditor({
  title,
  description,
  imageSelection,
  resourcesSelection,
  imageCatalog,
  resourceCatalog,
  showTag = true,
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
    tier
      ? `${tier.resources.cpu_limit} CPU · ${tier.resources.mem_limit} RAM`
      : undefined;

  return (
    <div className="max-w-2xl">
      <Card>
        <CardTitle>{title}</CardTitle>
        {description && (
          <p className="text-sm text-gray-500 mb-6">{description}</p>
        )}

        <SelectionBox
          label="Notebook Image"
          title={imageName}
          description={imageFamily?.description}
          onChangeClick={() => setOpenDialog("image")}
        />

        <SelectionBox
          label="Student Resources"
          title={
            studentTier?.display_name ?? resourcesSelection?.student ?? "—"
          }
          description={resourceDescription(studentTier)}
          onChangeClick={() => setOpenDialog("student")}
          infoContent={studentTier?.warning}
        />

        <SelectionBox
          label="Grader Resources"
          title={graderTier?.display_name ?? resourcesSelection?.grader ?? "—"}
          description={resourceDescription(graderTier)}
          onChangeClick={() => setOpenDialog("grader")}
          infoContent={graderTier?.warning}
        />
      </Card>

      {imageCatalog && (
        <ImageSelectionDialog
          open={openDialog === "image"}
          onClose={() => setOpenDialog(null)}
          imageSelection={imageSelection ?? null}
          imageCatalog={imageCatalog}
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
