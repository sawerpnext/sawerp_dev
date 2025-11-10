import * as React from "react";
import { Snackbar, Alert } from "@mui/material";

type Sev = "success" | "error" | "info" | "warning";

export default function useSnackbar() {
  const [open, setOpen] = React.useState(false);
  const [msg, setMsg] = React.useState("");
  const [sev, setSev] = React.useState<Sev>("success");

  const show = (message: string, severity: Sev = "success") => {
    setMsg(message);
    setSev(severity);
    setOpen(true);
  };

  const showSuccess = (m: string) => show(m, "success");
  const showError = (m: string) => show(m, "error");
  const showInfo = (m: string) => show(m, "info");
  const showWarning = (m: string) => show(m, "warning");

  const SnackbarOutlet = (
    <Snackbar
      open={open}
      autoHideDuration={2000}
      onClose={() => setOpen(false)}
      anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
    >
      {/* MUI Alert already has role="alert" for SR announcement */}
      <Alert severity={sev} variant="filled">
        {msg}
      </Alert>
    </Snackbar>
  );

  return { showSuccess, showError, showInfo, showWarning, SnackbarOutlet };
}
