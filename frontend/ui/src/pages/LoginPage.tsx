import React from "react";
import {
  Avatar,
  Box,
  Button,
  Paper,
  Stack,
  TextField,
  Typography,
  Alert,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import { setRole } from "../lib/session";
import type { Role } from "../lib/session";

const CREDENTIALS: Record<string, { password: string; role: Role; home: string }> = {
  admin:   { password: "admin",   role: "admin",   home: "/admin" },
  creator: { password: "creator", role: "creator", home: "/creator" },
  reviewer:{ password: "reviewer",role: "reviewer",home: "/reviewer" },
  viewer:  { password: "viewer",  role: "viewer",  home: "/viewer" },
};

const LoginPage: React.FC = () => {
  const [username, setUsername] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [usernameError, setUsernameError] = React.useState<string | null>(null);
  const [passwordError, setPasswordError] = React.useState<string | null>(null);
  const [formError, setFormError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);

  const navigate = useNavigate();

  const validate = () => {
    let ok = true;
    if (!username.trim()) {
      setUsernameError("Please enter your username.");
      ok = false;
    } else setUsernameError(null);

    if (!password) {
      setPasswordError("Please enter your password.");
      ok = false;
    } else setPasswordError(null);

    return ok;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    if (!validate()) return;

    setLoading(true);

    setTimeout(() => {
      const entry = CREDENTIALS[username];
      if (entry && entry.password === password) {
        setRole(entry.role);
        navigate(entry.home, { replace: true });
      } else {
        setFormError("Incorrect username or password.");
      }
      setLoading(false);
    }, 250);
  };

  return (
    <Box
      sx={{
        minHeight: "100dvh",
        display: "grid",
        placeItems: "center",
        p: 2,
        background:
          "radial-gradient(900px 600px at 0% 0%, #e0f2fe 0%, transparent 60%), radial-gradient(900px 600px at 100% 100%, #e9d5ff 0%, transparent 60%)",
      }}
    >
      <Paper
        elevation={6}
        sx={{ width: "100%", maxWidth: 420, p: { xs: 3, sm: 4 }, borderRadius: 3 }}
      >
        <Stack spacing={3} alignItems="center" textAlign="center">
          <Avatar
            src="/logo.svg"
            alt="ERP Logo"
            sx={{ width: 64, height: 64, bgcolor: "transparent" }}
            variant="rounded"
          />
          <Typography variant="h4" fontWeight={800}>
            Sign in
          </Typography>

          {formError && (
            <Alert severity="error" sx={{ width: "100%" }}>
              {formError}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} noValidate sx={{ width: "100%" }}>
            <Stack spacing={2.5}>
              <TextField
                label="Username"
                autoComplete="username"
                autoFocus
                fullWidth
                value={username}
                onChange={(e) => {
                  setUsername(e.target.value);
                  if (usernameError) setUsernameError(null);
                  if (formError) setFormError(null);
                }}
                error={!!usernameError}
                helperText={usernameError ?? " "}
                required
              />

              <TextField
                label="Password"
                type="password"
                autoComplete="current-password"
                fullWidth
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (passwordError) setPasswordError(null);
                  if (formError) setFormError(null);
                }}
                error={!!passwordError}
                helperText={passwordError ?? " "}
                required
              />

              <Button type="submit" variant="contained" size="large" fullWidth disabled={loading}>
                {loading ? "Signing in…" : "Sign in"}
              </Button>
            </Stack>
          </Box>
        </Stack>
      </Paper>
    </Box>
  );
};

export default LoginPage;
