import { useState } from "react";
import { Modal } from "@components/ui/Modal";
import { Button } from "@components/ui/Button";
import type { ImageCatalog, ImageSelection } from "@api/types";

interface Props {
  open: boolean;
  onClose: () => void;
  imageSelection: ImageSelection | null;
  imageCatalog: ImageCatalog;
  onConfirm: (selection: ImageSelection) => void;
}

export function ImageSelectionDialog({
  open,
  onClose,
  imageSelection,
  imageCatalog,
  onConfirm,
}: Props) {
  const initialFamily = imageSelection?.family || imageCatalog.default_family;
  const initialTag =
    imageSelection?.tag ||
    imageCatalog.families[initialFamily]?.default_tag ||
    "";

  const [selectedFamily, setSelectedFamily] = useState<string>(initialFamily);
  const [selectedTag, setSelectedTag] = useState<string>(initialTag);

  const handleSelectFamily = (family: string) => {
    if (family !== selectedFamily) {
      setSelectedFamily(family);
      setSelectedTag(imageCatalog.families[family]?.default_tag || "");
    }
  };

  const handleConfirm = () => {
    if (selectedFamily && selectedTag) {
      onConfirm({ family: selectedFamily, tag: selectedTag });
      onClose();
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Select Notebook Image"
      description="Choose the image family and version for this configuration."
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleConfirm}
            disabled={!selectedFamily || !selectedTag}
          >
            Save Changes
          </Button>
        </>
      }
    >
      <div className="flex flex-col gap-3">
        {Object.entries(imageCatalog.families).map(([familyKey, family]) => {
          const isSelected = selectedFamily === familyKey;
          return (
            <div
              key={familyKey}
              onClick={() => handleSelectFamily(familyKey)}
              className={`cursor-pointer rounded-xl border-2 p-4 transition-colors ${
                isSelected
                  ? "border-hbrs-dark-blue bg-hbrs-light-blue/30"
                  : "border-gray-200 bg-white hover:border-gray-300"
              }`}
            >
              <div className="font-semibold text-gray-900">
                {family.display_name}
              </div>
              <div className="text-sm text-gray-500 mt-0.5">
                {family.description}
              </div>

              {isSelected && (
                <div className="mt-3">
                  <label className="block text-xs font-semibold mb-1 text-gray-600">
                    Version
                  </label>
                  <select
                    value={selectedTag}
                    onChange={(e) => setSelectedTag(e.target.value)}
                    onClick={(e) => e.stopPropagation()}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-hbrs-dark-blue"
                  >
                    <option value="" disabled>
                      Select a version
                    </option>
                    {Object.entries(family.tags).map(([tagName, tagInfo]) => (
                      <option key={tagName} value={tagName}>
                        {tagName} ({tagInfo.status})
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </Modal>
  );
}
