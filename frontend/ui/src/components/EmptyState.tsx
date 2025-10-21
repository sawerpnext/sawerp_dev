import * as React from "react";
import { Box, Button, Paper, Stack, Typography } from "@mui/material";

type Props = {
  title: string;
  description?: string;
  actionText?: string;
  onAction?: () => void;
};

const EmptyState: React.FC<Props> = ({
  title,
  description,
  actionText,
  onAction,
}) => {
  return (
    <Paper
      variant="outlined"
      role="region"
      aria-label="Empty state"
      sx={{
        height: 520,
        display: "grid",
        placeItems: "center",
        bgcolor: "background.default",
      }}
    >
      <Box sx={{ textAlign: "center", px: 3, maxWidth: 520 }}>
        <Stack spacing={1.5} alignItems="center">
          <Typography component="h2" variant="h6" fontWeight={800}>
            {title}
          </Typography>
          {description && (
            <Typography color="text.secondary">{description}</Typography>
          )}
          {actionText && onAction && (
            <Button variant="contained" onClick={onAction} aria-label={actionText}>
              {actionText}
            </Button>
          )}
        </Stack>
      </Box>
    </Paper>
  );
};

export default EmptyState;
