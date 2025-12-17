import { PromptDialog } from "../base/PromptDialog";

interface RemoveSelfFromCourseDialogProps {
  username: string;
  onConfirm: () => void;
  onCancel: () => void;
}

const RemoveSelfFromCourseDialog = ({
  username,
  onConfirm,
  onCancel,
}: RemoveSelfFromCourseDialogProps) => {
  return (
    <PromptDialog
      title="Remove Yourself from Course"
      message={`You are about to remove yourself from this course. This will affect your access.\n\nTo confirm, please type your username:`}
      placeholder={username}
      confirmText="Remove Myself"
      cancelText="Cancel"
      onConfirm={(value) => {
        if (value === username) {
          onConfirm();
        }
      }}
      onCancel={onCancel}
      validateInput={(value) => value === username}
      validationMessage={`Please type "${username}" to confirm`}
    />
  );
};

export { RemoveSelfFromCourseDialog };
export type { RemoveSelfFromCourseDialogProps };
