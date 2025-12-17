import { ConfirmDialog } from "../base/ConfirmDialog";

interface RemoveUserFromCourseDialogProps {
  userName: string;
  onConfirm: () => void;
  onCancel: () => void;
}

const RemoveUserFromCourseDialog = ({
  userName,
  onConfirm,
  onCancel,
}: RemoveUserFromCourseDialogProps) => {
  return (
    <ConfirmDialog
      title={`Remove User ${userName} from Course`}
      message={`Are you sure you want to remove ${userName} from this course?`}
      confirmText="Remove User"
      cancelText="Cancel"
      onConfirm={onConfirm}
      onCancel={onCancel}
      variant="destructive"
    />
  );
};

export { RemoveUserFromCourseDialog };
export type { RemoveUserFromCourseDialogProps };
