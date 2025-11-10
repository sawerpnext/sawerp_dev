import React from "react";
import { Box, Paper, Stack, Typography, Button } from "@mui/material";
import { clearRole, getRole } from "../lib/session";
import { useNavigate } from "react-router-dom";

const CreatorView: React.FC = () => {
  const navigate = useNavigate();
  const role = getRole();

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3, maxWidth: 960 }}>
        <Stack spacing={2}>
          <Typography variant="h5" fontWeight={800}>
            Creator Workspace
          </Typography>
          <Typography variant="body1">Role: {role}</Typography>
          <Typography>
            Create and edit records (e.g., bookings/containers/vendors). Pending items go to Reviewer.
          </Typography>
          <Button
            variant="outlined"
            onClick={() => {
              clearRole();
              navigate("/login", { replace: true });
            }}
          >
            Logout
          </Button>
        </Stack>
      </Paper>
    </Box>
  );
};

export default CreatorView;
