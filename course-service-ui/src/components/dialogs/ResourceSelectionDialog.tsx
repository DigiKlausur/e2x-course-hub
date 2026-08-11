import { useState } from "react";
import { Modal } from "@components/ui/Modal";
import { Button } from "@components/ui/Button";
import type { ResourceCatalog } from "@api/types";

interface Props {
  open: boolean;
  onClose: () => void;
  initialTier: string;
  resourceCatalog: ResourceCatalog;
  role: "student" | "grader";
  onConfirm: (tier: string) => void;
}

export function ResourceSelectionDialog({
  open,
  onClose,
  initialTier,
  resourceCatalog,
  role,
  onConfirm,
}: Props) {
  const [selectedTier, setSelectedTier] = useState<string>(initialTier);

  const handleConfirm = () => {
    if (selectedTier) {
      onConfirm(selectedTier);
      onClose();
    }
  };

  const tiers = resourceCatalog[role].tiers;

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`Select ${role === "student" ? "Student" : "Grader"} Resources`}
      description="Choose a resource tier for this configuration."
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleConfirm}
            disabled={!selectedTier}
          >
            Save Changes
          </Button>
        </>
      }
    >
      <div className="flex flex-col gap-3">
        {Object.entries(tiers).map(([tierKey, tier]) => {
          const isSelected = selectedTier === tierKey;
          const r = tier.resources;
          return (
            <div
              key={tierKey}
              onClick={() => setSelectedTier(tierKey)}
              className={`cursor-pointer rounded-xl border-2 p-4 transition-colors ${
                isSelected
                  ? "border-hbrs-dark-blue bg-hbrs-light-blue/30"
                  : "border-gray-200 bg-white hover:border-gray-300"
              }`}
            >
              <div className="font-semibold text-gray-900">
                {tier.display_name}
              </div>
              <div className="text-sm text-gray-500 mt-0.5">
                {tier.description}
              </div>
              <div className="mt-2 text-xs text-gray-500 flex gap-4">
                <span>
                  {r.cpu_limit} CPU
                  {r.cpu_guarantee ? ` (${r.cpu_guarantee} guaranteed)` : ""}
                </span>
                <span>
                  {r.mem_limit} RAM
                  {r.mem_guarantee ? ` (${r.mem_guarantee} guaranteed)` : ""}
                </span>
              </div>
              {tier.warning && (
                <p className="mt-2 text-xs text-amber-600">⚠ {tier.warning}</p>
              )}
            </div>
          );
        })}
      </div>
    </Modal>
  );
}
