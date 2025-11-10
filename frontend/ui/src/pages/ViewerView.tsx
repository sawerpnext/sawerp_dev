import React from "react";
import { Box, Paper, Stack, Typography, Button } from "@mui/material";
import { clearRole, getRole } from "../lib/session";
import { useNavigate } from "react-router-dom";

const ViewerView: React.FC = () => {
  const navigate = useNavigate();
  const role = getRole();

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3, maxWidth: 960 }}>
        <Stack spacing={2}>
          <Typography variant="h5" fontWeight={800}>
            Viewer Portal
          </Typography>
          <Typography variant="body1">Role: {role}</Typography>
          <Typography>
            Read-only access. Browse records, run allowed reports, and export data.
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

export default ViewerView;
