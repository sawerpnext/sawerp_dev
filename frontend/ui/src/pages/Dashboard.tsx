import React from "react";
import { Box, Paper, Stack, Typography, Button } from "@mui/material";
import { useNavigate } from "react-router-dom";

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3, maxWidth: 720 }}>
        <Stack spacing={2}>
          <Typography variant="h5" fontWeight={800}>
            Dashboard
          </Typography>
          <Typography>
            You’re in! (Hardcoded login with admin/admin)
          </Typography>
          <Button variant="outlined" onClick={() => navigate("/login")}>
            Back to Login
          </Button>
        </Stack>
      </Paper>
    </Box>
  );
};

export default Dashboard;
