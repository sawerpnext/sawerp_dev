import * as React from "react";
import {
  Box,
  Stack,
  TextField,
  MenuItem,
  Button,
  Typography,
} from "@mui/material";
import { ROLES } from "../../../lib/session";

export type UsersFilters = {
  search: string;
  role: "all" | (typeof ROLES)[number];
  status: "all" | "Active" | "Inactive";
};

type Props = {
  filters: UsersFilters;
  onChange: (next: UsersFilters) => void;
  onReset: () => void;
  total: number;
  showing: number;
};

const UsersToolbar: React.FC<Props> = ({ filters, onChange, onReset, total, showing }) => {
  const liveId = React.useId();

  return (
    <Box
      role="region"
      aria-label="Users filters"
      sx={{
        p: 1.5,
        mb: 1,
        border: 1,
        borderColor: "divider",
        borderRadius: 2,
        bgcolor: "background.paper",
      }}
    >
      <Stack
        direction={{ xs: "column", sm: "row" }}
        spacing={1.5}
        alignItems={{ xs: "stretch", sm: "center" }}
      >
        <TextField
          size="small"
          label="Search users"
          placeholder="username, name, email"
          value={filters.search}
          onChange={(e) => onChange({ ...filters, search: e.target.value })}
          sx={{ minWidth: 220, flex: 1 }}
          inputProps={{ "aria-label": "Search users by username name or email" }}
        />

        <TextField
          select
          size="small"
          label="Role"
          value={filters.role}
          onChange={(e) =>
            onChange({ ...filters, role: e.target.value as Props["filters"]["role"] })
          }
          sx={{ minWidth: 160 }}
        >
          <MenuItem value="all">All roles</MenuItem>
          {ROLES.map((r) => (
            <MenuItem key={r} value={r}>
              {r}
            </MenuItem>
          ))}
        </TextField>

        <TextField
          select
          size="small"
          label="Status"
          value={filters.status}
          onChange={(e) =>
            onChange({
              ...filters,
              status: e.target.value as Props["filters"]["status"],
            })
          }
          sx={{ minWidth: 160 }}
        >
          <MenuItem value="all">All statuses</MenuItem>
          <MenuItem value="Active">Active</MenuItem>
          <MenuItem value="Inactive">Inactive</MenuItem>
        </TextField>

        <Box sx={{ flex: 1 }} />

        <Stack direction="row" spacing={1} alignItems="center">
          <Typography
            id={liveId}
            variant="body2"
            color="text.secondary"
            aria-live="polite"
          >
            Showing <b>{showing}</b> of {total}
          </Typography>
          <Button variant="text" onClick={onReset} aria-label="Reset filters">
            Reset
          </Button>
        </Stack>
      </Stack>
    </Box>
  );
};

export default UsersToolbar;
