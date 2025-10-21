import * as React from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
} from "@mui/material";

type Props = {
  open: boolean;
  title?: string;
  message?: React.ReactNode;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  onClose: () => void;
  destructive?: boolean;
};

const ConfirmDialog: React.FC<Props> = ({
  open,
  title = "Are you sure?",
  message,
  confirmText = "Delete",
  cancelText = "Cancel",
  onConfirm,
  onClose,
  destructive = true,
}) => {
  const titleId = React.useId();
  const descId = React.useId();

  return (
    <Dialog
      open={open}
      onClose={onClose}
      fullWidth
      maxWidth="xs"
      aria-labelledby={titleId}
      aria-describedby={message ? descId : undefined}
    >
      <DialogTitle id={titleId}>{title}</DialogTitle>
      {message && (
        <DialogContent>
          <Typography id={descId}>{message}</Typography>
        </DialogContent>
      )}
      <DialogActions>
        <Button onClick={onClose} aria-label="Cancel deletion">
          {cancelText}
        </Button>
        <Button
          variant="contained"
          color={destructive ? "error" : "primary"}
          onClick={() => {
            onConfirm();
            onClose();
          }}
          autoFocus
          aria-label={confirmText}
        >
          {confirmText}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ConfirmDialog;
