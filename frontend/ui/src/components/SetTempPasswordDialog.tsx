// src/components/SetTempPasswordDialog.tsx
import * as React from "react";
import {
  Box,
  Button,
  Checkbox,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  IconButton,
  InputAdornment,
  LinearProgress,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import {
  Visibility,
  VisibilityOff,
  LockReset as LockResetIcon,
} from "@mui/icons-material";

type Props = {
  open: boolean;
  email?: string; // for context text (optional)
  onClose: () => void;
  onSubmit: (payload: {
    password: string;
    expiresInMins: number;
    mustChange: boolean;
  }) => void;
};

const EXPIRES = [
  { label: "24 hours", value: 60 * 24 },
  { label: "72 hours", value: 60 * 72 },
  { label: "7 days", value: 60 * 24 * 7 },
];

// ----- Pure helpers (NO setState here) -----
function scorePassword(pw: string) {
  let score = 0;
  if (pw.length >= 8) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[a-z]/.test(pw)) score++;
  if (/\d/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  return Math.min(100, (score / 5) * 100);
}
function strengthLabel(pw: string) {
  const s = scorePassword(pw);
  if (s >= 80) return "Strong";
  if (s >= 60) return "Good";
  if (s >= 40) return "Fair";
  if (s > 0) return "Weak";
  return "Very weak";
}
function meetsPolicy(pw: string) {
  const v = pw.trim();
  const classes =
    (/[A-Z]/.test(v) ? 1 : 0) +
    (/[a-z]/.test(v) ? 1 : 0) +
    (/\d/.test(v) ? 1 : 0) +
    (/[^A-Za-z0-9]/.test(v) ? 1 : 0);
  return v.length >= 8 && classes >= 3;
}

const SetTempPasswordDialog: React.FC<Props> = ({
  open,
  email,
  onClose,
  onSubmit,
}) => {
  const titleId = React.useId();
  const descId = React.useId();

  const [password, setPassword] = React.useState("");
  const [confirm, setConfirm] = React.useState("");
  const [showPw, setShowPw] = React.useState(false);
  const [showConfirm, setShowConfirm] = React.useState(false);
  const [expiresIn, setExpiresIn] = React.useState(EXPIRES[0].value);
  const [mustChange, setMustChange] = React.useState(true);

  const [pErr, setPErr] = React.useState<string | null>(null);
  const [cErr, setCErr] = React.useState<string | null>(null);

  // Reset state on open
  React.useEffect(() => {
    if (!open) return;
    setPassword("");
    setConfirm("");
    setExpiresIn(EXPIRES[0].value);
    setMustChange(true);
    setPErr(null);
    setCErr(null);
  }, [open]);

  // Validators (call only in handlers, not during render)
  const validatePassword = (val = password) => {
    const v = val.trim();
    if (v.length < 8) {
      setPErr("Minimum 8 characters");
      return false;
    }
    if (!meetsPolicy(v)) {
      setPErr("Use upper, lower, number, symbol (any 3 of 4)");
      return false;
    }
    setPErr(null);
    return true;
  };

  const validateConfirm = (val = confirm) => {
    if (val !== password) {
      setCErr("Passwords do not match");
      return false;
    }
    setCErr(null);
    return true;
  };

  // Pure validity (no setState inside)
  const isValid = React.useMemo(
    () =>
      password.trim().length > 0 &&
      confirm.trim().length > 0 &&
      meetsPolicy(password) &&
      confirm === password &&
      !pErr &&
      !cErr,
    [password, confirm, pErr, cErr]
  );

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    const ok = validatePassword() && validateConfirm();
    if (!ok) return;
    onSubmit({
      password: password.trim(),
      expiresInMins: expiresIn,
      mustChange,
    });
  };

  const score = scorePassword(password);
  const scoreText = strengthLabel(password);

  return (
    <Dialog
      open={open}
      onClose={onClose}
      fullWidth
      maxWidth="sm"
      aria-labelledby={titleId}
      aria-describedby={descId}
    >
      <DialogTitle id={titleId}>
        <LockResetIcon sx={{ mr: 1, verticalAlign: "bottom" }} />
        Set temporary password
      </DialogTitle>

      {/* autoComplete="off" nudges some password managers to back off */}
      <Box component="form" autoComplete="off" onSubmit={handleSubmit}>
        <DialogContent id={descId} sx={{ pt: 2 }}>
          <Stack spacing={2}>
            {email && (
              <Typography variant="body2" color="text.secondary">
                This will set a one-time password for <b>{email}</b>.
              </Typography>
            )}

            {/* Password */}
            <TextField
              label="Temporary password"
              type={showPw ? "text" : "password"}
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (pErr) validatePassword(e.target.value); // live revalidate if error showing
                if (confirm) validateConfirm(confirm); // keep match check in sync
              }}
              onBlur={(e) => validatePassword(e.target.value)}
              error={!!pErr}
              helperText={pErr ?? " "}
              required
              inputProps={{
                name: "temp-password", // avoid generic "password"
                autoComplete: "new-password",
                "data-1p-ignore": "true",
                "data-lpignore": "true",
                "data-bwignore": "true",
                autoCapitalize: "off",
                autoCorrect: "off",
                spellCheck: "false",
              }}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label={showPw ? "Hide password" : "Show password"}
                      onClick={() => setShowPw((s) => !s)}
                      edge="end"
                    >
                      {showPw ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            {/* Strength meter */}
            <Box aria-live="polite">
              <LinearProgress variant="determinate" value={score} />
              <Typography variant="caption" sx={{ mt: 0.5, display: "block" }}>
                Strength: {scoreText}
              </Typography>
            </Box>

            {/* Confirm */}
            <TextField
              label="Confirm password"
              type={showConfirm ? "text" : "password"}
              value={confirm}
              onChange={(e) => {
                setConfirm(e.target.value);
                if (cErr) validateConfirm(e.target.value); // live revalidate if error showing
              }}
              onBlur={(e) => validateConfirm(e.target.value)}
              error={!!cErr}
              helperText={cErr ?? " "}
              required
              inputProps={{
                name: "temp-password-confirm",
                autoComplete: "new-password",
                "data-1p-ignore": "true",
                "data-lpignore": "true",
                "data-bwignore": "true",
                autoCapitalize: "off",
                autoCorrect: "off",
                spellCheck: "false",
              }}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label={
                        showConfirm ? "Hide password" : "Show password"
                      }
                      onClick={() => setShowConfirm((s) => !s)}
                      edge="end"
                    >
                      {showConfirm ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            {/* Expiry */}
            <TextField
              select
              label="Expires in"
              value={expiresIn}
              onChange={(e) => setExpiresIn(Number(e.target.value))}
            >
              {EXPIRES.map((opt) => (
                <MenuItem key={opt.value} value={opt.value}>
                  {opt.label}
                </MenuItem>
              ))}
            </TextField>

            {/* Must change */}
            <FormControlLabel
              control={
                <Checkbox
                  checked={mustChange}
                  onChange={(e) => setMustChange(e.target.checked)}
                />
              }
              label="Require user to change password at next login"
            />
          </Stack>
        </DialogContent>

        <DialogActions>
          <Button onClick={onClose} aria-label="Cancel setting temporary password">
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={!isValid}
            aria-label="Set temporary password"
          >
            Set password
          </Button>
        </DialogActions>
      </Box>
    </Dialog>
  );
};

export default SetTempPasswordDialog;
