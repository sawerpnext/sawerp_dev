import * as React from "react";
import { Box, Paper, Stack, Typography } from "@mui/material";

export default function AdminHome() {
  return (
    <Box>
      <Paper sx={{ p: 3 }}>
        <Stack spacing={1}>
          <Typography variant="h5" fontWeight={800}>
            Admin Overview
          </Typography>
          <Typography color="text.secondary">
            This is your admin home. Use the left navigation to access modules.
          </Typography>
        </Stack>
      </Paper>
    </Box>
  );
}
