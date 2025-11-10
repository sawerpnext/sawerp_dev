// src/pages/admin/permissions/PermissionMatrixPage.tsx
import * as React from "react";
import {
  Box,
  Paper,
  Stack,
  Typography,
  Tabs,
  Tab,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Checkbox,
  Tooltip,
  IconButton,
  Divider,
  Button,
} from "@mui/material";
import RestartAltIcon from "@mui/icons-material/RestartAlt";
import SaveIcon from "@mui/icons-material/Save";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import {
  ACTIONS,
  type Action,
  FEATURES,
  type FeatureKey,
  DEFAULT_POLICIES,
  type RolePolicy,
  withDependencies,
  emptyPolicy,
} from "../../../lib/permissions";
import { ROLES, type Role } from "../../../lib/session";
import useSnackbar from "../../../hooks/useSnackbar";

function a11yProps(index: number) {
  return {
    id: `role-tab-${index}`,
    "aria-controls": `role-panel-${index}`,
  };
}

export default function PermissionMatrixPage() {
  const { showSuccess, showInfo, showWarning, SnackbarOutlet } = useSnackbar();

  // In-memory store for all roles
  const [policies, setPolicies] = React.useState<Record<Role, RolePolicy>>(
    () => JSON.parse(JSON.stringify(DEFAULT_POLICIES))
  );

  const [tab, setTab] = React.useState(0);
  const role = ROLES[tab] as Role;

  const current = policies[role];

  // Toggle a single cell with dependency handling
  const toggle = (feature: FeatureKey, action: Action, value: boolean) => {
    setPolicies((prev) => ({
      ...prev,
      [role]: withDependencies(prev[role], feature, action, value),
    }));
  };

  // Row (feature) select all / none
  const setRow = (feature: FeatureKey, value: boolean) => {
    setPolicies((prev) => {
      const next: RolePolicy = JSON.parse(JSON.stringify(prev[role]));
      for (const a of ACTIONS) next[feature][a] = value;
      // enforce view dependency if enabling any
      if (value) next[feature].view = true;
      return { ...prev, [role]: next };
    });
  };

  // Column (action) select all / none
  const setCol = (action: Action, value: boolean) => {
    setPolicies((prev) => {
      const next: RolePolicy = JSON.parse(JSON.stringify(prev[role]));
      for (const f of FEATURES) {
        next[f.key][action] = value;
        if (value) {
          for (const dep of ["view"] as Action[]) next[f.key][dep] = true;
        } else if (action === "view") {
          // disabling "view" removes dependents
          for (const a of ACTIONS) {
            if (a !== "view") next[f.key][a] = false;
          }
        }
      }
      return { ...prev, [role]: next };
    });
  };

  const isRowAll = (feature: FeatureKey) =>
    ACTIONS.every((a) => current[feature][a]);

  const isColAll = (action: Action) =>
    FEATURES.every((f) => current[f.key][action]);

  const isIndeterminateRow = (feature: FeatureKey) => {
    const count = ACTIONS.filter((a) => current[feature][a]).length;
    return count > 0 && count < ACTIONS.length;
  };

  const isIndeterminateCol = (action: Action) => {
    const count = FEATURES.filter((f) => current[f.key][action]).length;
    return count > 0 && count < FEATURES.length;
  };

  const resetRoleToDefaults = () => {
    setPolicies((prev) => ({
      ...prev,
      [role]: JSON.parse(JSON.stringify(DEFAULT_POLICIES[role])),
    }));
    showInfo(`Reverted ${role} to default permissions`);
  };

  const clearRole = () => {
    setPolicies((prev) => ({
      ...prev,
      [role]: emptyPolicy(),
    }));
    showWarning(`Cleared all ${role} permissions (in-memory)`);
  };

  // Fake save (front-end only for now)
  const save = () => {
    // Later: POST /api/permissions/{role}
    console.log("Saving policy for", role, policies[role]);
    showSuccess(`Saved ${role} permissions (in-memory)`);
  };

  // A11y helper
  const gridDescId = React.useId();

  return (
    <Box>
      <span
        id={gridDescId}
        style={{
          position: "absolute",
          width: 1,
          height: 1,
          margin: -1,
          border: 0,
          padding: 0,
          clip: "rect(0 0 0 0)",
          overflow: "hidden",
        }}
      >
        Permissions matrix. Use arrow keys to navigate cells, space to toggle.
      </span>

      <Stack
        direction={{ xs: "column", sm: "row" }}
        alignItems={{ xs: "flex-start", sm: "center" }}
        justifyContent="space-between"
        sx={{ mb: 2, gap: 1 }}
      >
        <Typography variant="h5" fontWeight={800} component="h1">
          Permission Matrix
        </Typography>

        <Stack direction="row" spacing={1}>
          <Button
            variant="outlined"
            startIcon={<RestartAltIcon />}
            onClick={resetRoleToDefaults}
          >
            Reset to defaults
          </Button>
          <Button variant="text" onClick={clearRole}>
            Clear all
          </Button>
          <Button variant="contained" startIcon={<SaveIcon />} onClick={save}>
            Save
          </Button>
        </Stack>
      </Stack>

      {/* Role tabs */}
      <Paper sx={{ mb: 2, p: 0.5 }} role="region" aria-label="Role selector">
        <Tabs
          value={tab}
          onChange={(_, v) => setTab(v)}
          variant="scrollable"
          allowScrollButtonsMobile
        >
          {ROLES.map((r, i) => (
            <Tab key={r} label={r} {...a11yProps(i)} />
          ))}
        </Tabs>
      </Paper>

      {/* Matrix */}
      <Paper sx={{ p: 1, overflow: "auto" }} aria-describedby={gridDescId}>
        <Table size="small" stickyHeader aria-label="Permissions table">
          <TableHead>
            <TableRow>
              <TableCell sx={{ position: "sticky", left: 0, zIndex: 1, bgcolor: "background.paper", minWidth: 220 }}>
                Feature
              </TableCell>

              {/* Action headers with column select-all */}
              {ACTIONS.map((a) => (
                <TableCell key={a} align="center" sx={{ minWidth: 120 }}>
                  <Stack direction="row" justifyContent="center" alignItems="center" spacing={0.5}>
                    <Typography variant="body2" fontWeight={700} sx={{ textTransform: "capitalize" }}>
                      {a}
                    </Typography>
                    <Tooltip
                      title={`Select all ${a} for ${role}`}
                      placement="top"
                    >
                      <Checkbox
                        size="small"
                        checked={isColAll(a)}
                        indeterminate={isIndeterminateCol(a)}
                        onChange={(e) => setCol(a, e.target.checked)}
                        inputProps={{ "aria-label": `Toggle all ${a}` }}
                      />
                    </Tooltip>
                  </Stack>
                </TableCell>
              ))}

              {/* Row select-all label column spacer */}
              <TableCell align="center" sx={{ minWidth: 120 }}>
                <Typography variant="body2" fontWeight={700}>
                  Row
                </Typography>
              </TableCell>
            </TableRow>
          </TableHead>

          <TableBody>
            {FEATURES.map((f) => {
              const rowAll = isRowAll(f.key);
              const rowInd = isIndeterminateRow(f.key);

              return (
                <TableRow hover key={f.key}>
                  <TableCell
                    sx={{
                      position: "sticky",
                      left: 0,
                      zIndex: 1,
                      bgcolor: "background.paper",
                    }}
                  >
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <Typography fontWeight={600}>{f.label}</Typography>
                      {f.description && (
                        <Tooltip title={f.description}>
                          <InfoOutlinedIcon fontSize="small" color="action" />
                        </Tooltip>
                      )}
                    </Stack>
                  </TableCell>

                  {ACTIONS.map((a) => {
                    const checked = current[f.key][a];
                    const disabled = false; // hook any future constraints here
                    return (
                      <TableCell key={`${f.key}-${a}`} align="center">
                        <Checkbox
                          checked={checked}
                          onChange={(e) => toggle(f.key, a, e.target.checked)}
                          disabled={disabled}
                          inputProps={{ "aria-label": `${f.label} - ${a}` }}
                          size="small"
                        />
                      </TableCell>
                    );
                  })}

                  {/* Row select all */}
                  <TableCell align="center">
                    <Checkbox
                      checked={rowAll}
                      indeterminate={rowInd}
                      onChange={(e) => setRow(f.key, e.target.checked)}
                      inputProps={{ "aria-label": `Toggle all for ${f.label}` }}
                      size="small"
                    />
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>

        <Divider sx={{ my: 2 }} />

        {/* Legend */}
        <Stack direction="row" spacing={2} flexWrap="wrap">
          <Typography variant="body2" color="text.secondary">
            Dependencies: <b>view</b> is required for create/edit/delete/approve/export.
          </Typography>
        </Stack>
      </Paper>

      {SnackbarOutlet}
    </Box>
  );
}
