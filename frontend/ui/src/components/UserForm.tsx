import * as React from "react";
import {
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Button,
  Stack,
} from "@mui/material";
import { ROLES } from "../lib/session";
import type { Role } from "../lib/session";

export type UserFormValues = {
  username: string;
  name: string;
  email: string;
  role: Role;
  status: "Active" | "Inactive";
};

type Props = {
  open: boolean;
  mode: "create" | "edit";
  initial?: Partial<UserFormValues>;
  existingUsernames: string[]; // lowercased
  onClose: () => void;
  onSubmit: (values: UserFormValues) => void;
};

const DEFAULTS: UserFormValues = {
  username: "",
  name: "",
  email: "",
  role: "viewer",
  status: "Active",
};

const emailOk = (val: string) => /^\S+@\S+\.\S+$/.test(val.trim());

const UserForm: React.FC<Props> = ({
  open,
  mode,
  initial,
  existingUsernames,
  onClose,
  onSubmit,
}) => {
  const [values, setValues] = React.useState<UserFormValues>({
    ...DEFAULTS,
    ...initial,
  } as UserFormValues);

  const [uErr, setUErr] = React.useState<string | null>(null);
  const [nErr, setNErr] = React.useState<string | null>(null);
  const [eErr, setEErr] = React.useState<string | null>(null);

  const usernameRef = React.useRef<HTMLInputElement>(null);
  const nameRef = React.useRef<HTMLInputElement>(null);
  const emailRef = React.useRef<HTMLInputElement>(null);

  const titleId = React.useId();
  const descId = React.useId();

  React.useEffect(() => {
    setValues({ ...DEFAULTS, ...initial } as UserFormValues);
    setUErr(null);
    setNErr(null);
    setEErr(null);
    const t = setTimeout(() => {
      if (mode === "create") usernameRef.current?.focus();
      else nameRef.current?.focus();
    }, 0);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, mode, JSON.stringify(initial)]);

  const usernameUnique = (val: string) => {
    if (mode === "edit") return true;
    const v = val.trim().toLowerCase();
    return !existingUsernames.includes(v);
  };

  const validateUsername = (val = values.username) => {
    const v = val.trim();
    if (!v) return setUErr("Required"), false;
    if (!usernameUnique(v)) return setUErr("Username already exists"), false;
    setUErr(null);
    return true;
  };
  const validateName = (val = values.name) => {
    const v = val.trim();
    if (!v) return setNErr("Required"), false;
    setNErr(null);
    return true;
  };
  const validateEmail = (val = values.email) => {
    const v = val.trim();
    if (!v) return setEErr("Required"), false;
    if (!emailOk(v)) return setEErr("Invalid email"), false;
    setEErr(null);
    return true;
  };

  const isValid =
    values.username.trim() &&
    values.name.trim() &&
    values.email.trim() &&
    emailOk(values.email) &&
    usernameUnique(values.username) &&
    !uErr &&
    !nErr &&
    !eErr;

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    const okU = validateUsername();
    const okN = validateName();
    const okE = validateEmail();
    if (!(okU && okN && okE)) {
      if (uErr) usernameRef.current?.focus();
      else if (nErr) nameRef.current?.focus();
      else if (eErr) emailRef.current?.focus();
      return;
    }
    onSubmit({
      username: values.username.trim(),
      name: values.name.trim(),
      email: values.email.trim(),
      role: values.role,
      status: values.status,
    });
  };

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
        {mode === "create" ? "New user" : "Edit user"}
      </DialogTitle>

      <Box component="form" onSubmit={handleSubmit}>
        <DialogContent id={descId} sx={{ pt: 2 }}>
          <Stack spacing={2}>
            <TextField
              inputRef={usernameRef}
              label="Username"
              value={values.username}
              onChange={(e) => {
                const v = e.target.value;
                setValues((s) => ({ ...s, username: v }));
                if (uErr) validateUsername(v);
              }}
              onBlur={(e) => validateUsername(e.target.value)}
              error={!!uErr}
              helperText={uErr ?? " "}
              required
              inputProps={{ "aria-required": true, autoComplete: "username" }}
              autoFocus
              disabled={mode === "edit"}
            />
            <TextField
              inputRef={nameRef}
              label="Full name"
              value={values.name}
              onChange={(e) => {
                const v = e.target.value;
                setValues((s) => ({ ...s, name: v }));
                if (nErr) validateName(v);
              }}
              onBlur={(e) => validateName(e.target.value)}
              error={!!nErr}
              helperText={nErr ?? " "}
              required
              inputProps={{ "aria-required": true, autoComplete: "name" }}
            />
            <TextField
              inputRef={emailRef}
              label="Email"
              value={values.email}
              onChange={(e) => {
                const v = e.target.value;
                setValues((s) => ({ ...s, email: v }));
                if (eErr) validateEmail(v);
              }}
              onBlur={(e) => validateEmail(e.target.value)}
              error={!!eErr}
              helperText={eErr ?? " "}
              required
              inputProps={{ "aria-required": true, autoComplete: "email" }}
            />
            <TextField
              select
              label="Role"
              value={values.role}
              onChange={(e) =>
                setValues((s) => ({ ...s, role: e.target.value as Role }))
              }
            >
              {ROLES.map((r) => (
                <MenuItem key={r} value={r}>
                  {r}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="Status"
              value={values.status}
              onChange={(e) =>
                setValues((s) => ({
                  ...s,
                  status: e.target.value as "Active" | "Inactive",
                }))
              }
            >
              <MenuItem value="Active">Active</MenuItem>
              <MenuItem value="Inactive">Inactive</MenuItem>
            </TextField>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} aria-label="Cancel and close">
            Cancel (Esc)
          </Button>
          <Button type="submit" variant="contained" disabled={!isValid} aria-label="Submit form">
            {mode === "create" ? "Create" : "Save changes"}
          </Button>
        </DialogActions>
      </Box>
    </Dialog>
  );
};

export default UserForm;
