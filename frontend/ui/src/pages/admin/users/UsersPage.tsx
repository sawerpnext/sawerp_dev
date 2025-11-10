import * as React from "react";
// Import hooks for API calls
import { useEffect, useState, useMemo, useId } from "react";
import {
  Box,
  Paper,
  Stack,
  Typography,
  Button,
  Chip,
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Alert, // For error
  CircularProgress, // For loading
} from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import type { GridColDef, GridRowParams } from "@mui/x-data-grid";
import {
  Add,
  Delete,
  Edit as EditIcon,
  MoreVert as MoreVertIcon,
  Send as SendIcon,
  LockReset as LockResetIcon,
  ChangeCircle as ChangeCircleIcon,
} from "@mui/icons-material";
import type { Role } from "../../../lib/session";
import ConfirmDialog from "../../../components/ConfirmDialog";
import UsersToolbar, { type UsersFilters } from "./UsersToolbar";
import EmptyState from "../../../components/EmptyState";
import UserForm, { type UserFormValues } from "../../../components/UserForm";
import useSnackbar from "../../../hooks/useSnackbar";
import SetTempPasswordDialog from "../../../components/SetTempPasswordDialog";

// Import our API Client and User type
import apiClient from "../../../lib/apiClient";
import type { User } from "../../../types/user";

// This type from your file now matches our API response
type UserRow = User & {
  name: string;
  status: "Active" | "Inactive";
  lastLogin?: string | null;
  lastPasswordResetAt?: string | null;
  tempPasswordLastSetAt?: string | null;
  mustChangePassword?: boolean;
};

// We no longer need INITIAL_ROWS
type Mode = "create" | "edit";

export default function UsersPage() {
  const { showSuccess, showInfo, showError, SnackbarOutlet } = useSnackbar();

  // API Data State
  const [rows, setRows] = useState<UserRow[]>([]); // Start empty
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter State
  const [filters, setFilters] = useState<UsersFilters>({
    search: "",
    role: "all",
    status: "all",
  });

  // Dialog/Form State
  const [formOpen, setFormOpen] = React.useState(false);
  const [mode, setMode] = React.useState<Mode>("create");
  const [editing, setEditing] = React.useState<UserRow | null>(null);

  // Delete Confirm State
  const [confirmOpen, setConfirmOpen] = React.useState(false);
  const [toDelete, setToDelete] = React.useState<UserRow | null>(null);

  // More Menu State
  const [menuAnchor, setMenuAnchor] = React.useState<null | HTMLElement>(null);
  const [menuUser, setMenuUser] = React.useState<UserRow | null>(null);
  const menuOpen = Boolean(menuAnchor);
  const [resetConfirmOpen, setResetConfirmOpen] = React.useState(false);
  const [tempOpen, setTempOpen] = React.useState(false);

  // --- 1. FETCH DATA ON LOAD ---
  useEffect(() => {
    const fetchUsers = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await apiClient.get<UserRow[]>("/users/");
        setRows(response.data);
      } catch (err) {
        console.error(err);
        setError("Failed to fetch users. Please try again.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchUsers();
  }, []); // Empty array means run once on mount

  // --- Derived State ---
  const adminCount = useMemo(
    () => rows.filter((r) => r.role === "ADMIN").length, // Use API value
    [rows]
  );

  // Filtering
  const filteredRows = useMemo(() => {
    const s = filters.search.trim().toLowerCase();
    return rows.filter((r) => {
      const matchesSearch =
        !s ||
        r.username.toLowerCase().includes(s) ||
        r.name.toLowerCase().includes(s) ||
        r.email.toLowerCase().includes(s);
      const matchesRole = filters.role === "all" || r.role === filters.role;
      const matchesStatus =
        filters.status === "all" || r.status === filters.status;
      return matchesSearch && matchesRole && matchesStatus;
    });
  }, [rows, filters]);

  // --- UI Handlers ---
  const openMenuFor = (el: HTMLElement, user: UserRow) => {
    setMenuAnchor(el);
    setMenuUser(user);
  };
  const closeMenu = () => setMenuAnchor(null);
  const resetFilters = () =>
    setFilters({ search: "", role: "all", status: "all" });

  const openCreate = () => {
    setMode("create");
    setEditing(null);
    setFormOpen(true);
  };
  const openEdit = (row: UserRow) => {
    setMode("edit");
    setEditing(row);
    setFormOpen(true);
  };
  const onRowDoubleClick = (params: GridRowParams<UserRow>) =>
    openEdit(params.row);

  // --- 2. CONNECT CREATE/UPDATE (CRUD) ---
  const handleSubmitForm = async (values: UserFormValues) => {
    // Helper to format data for the API
    const splitName = (name: string) => {
      const parts = name.trim().split(' ');
      const first_name = parts.shift() || '';
      const last_name = parts.join(' ');
      return { first_name, last_name };
    };

    if (mode === "edit" && editing) {
      const isEditingTheOnlyAdmin = editing.role === "ADMIN" && adminCount <= 1;
      const demotingAdmin = values.role !== "ADMIN";
      if (isEditingTheOnlyAdmin && demotingAdmin) {
        showError("You must keep at least one admin. Change another user first.");
        return;
      }

      const { first_name, last_name } = splitName(values.name);
      const apiPayload = {
        username: values.username,
        email: values.email,
        role: values.role,
        is_active: values.status === "Active",
        first_name: first_name,
        last_name: last_name,
      };

      try {
        const response = await apiClient.patch<UserRow>(
          `/users/${editing.id}/`,
          apiPayload
        );
        // On success, replace the old row with the new one from the server
        setRows((prev) =>
          prev.map((r) => (r.id === editing.id ? response.data : r))
        );
        showSuccess(`User "${response.data.username}" updated.`);
        setFormOpen(false);
      } catch (err: any) {
        console.error(err);
        const apiErrors = Object.values(err.response?.data || {}).join(' ');
        showError(`Failed to update user: ${apiErrors || 'Unknown error'}`);
      }
      return;
    }

    if (mode === "create") {
      if (!values.password) {
        showError("Password is required to create a user.");
        return;
      }

      const { first_name, last_name } = splitName(values.name);
      const apiPayload = {
        username: values.username,
        email: values.email,
        role: values.role,
        is_active: values.status === "Active",
        first_name: first_name,
        last_name: last_name,
        password: values.password,
      };

      try {
        const response = await apiClient.post<UserRow>("/users/", apiPayload);
        // On success, add the new user (from server) to the top
        setRows((prev) => [response.data, ...prev]);
        showSuccess(`User "${response.data.username}" created.`);
        setFormOpen(false);
      } catch (err: any) {
        console.error(err);
        const apiErrors = Object.values(err.response?.data || {}).join(' ');
        showError(`Failed to create user: ${apiErrors || 'Unknown error'}`);
      }
    }
  };

  // --- 3. CONNECT DELETE (CRUD) ---
  const askDelete = (row: UserRow) => {
    if (row.role === "ADMIN" && adminCount <= 1) {
      showError("You must keep at least one admin. This admin cannot be deleted.");
      return;
    }
    setToDelete(row);
    setConfirmOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!toDelete) return;
    try {
      await apiClient.delete(`/users/${toDelete.id}/`);
      // On success, remove the user from state
      setRows((prev) => prev.filter((r) => r.id !== toDelete.id));
      showInfo(`Deleted user "${toDelete.username}"`);
    } catch (err) {
      console.error(err);
      showError("Failed to delete user.");
    } finally {
      setConfirmOpen(false);
      setToDelete(null);
    }
  };

  // --- 4. MORE ACTIONS (Still Mocked) ---
  // These require custom backend endpoints we haven't built yet
  const askSendReset = () => setResetConfirmOpen(true);
  const handleConfirmSendReset = () => {
    if (!menuUser) return;
    showSuccess(`(DEMO) Reset link sent to ${menuUser.email}`);
    setResetConfirmOpen(false);
    setMenuUser(null);
  };
  const askSetTemp = () => setTempOpen(true);
  const handleSetTempSubmit = (payload: {/*...*/}) => {
    if (!menuUser) return;
    showSuccess(`(DEMO) Temp password set for ${menuUser.email}`);
    setTempOpen(false);
    setMenuUser(null);
  };
  const toggleForceChange = () => {
    if (!menuUser) return;
    showInfo(`(DEMO) Toggled force change for ${menuUser.username}`);
  };

  // --- DataGrid Columns ---
  const columns = useMemo<GridColDef<UserRow>[]>(
    () => [
      { field: "username", headerName: "Username", flex: 1, minWidth: 140 },
      { field: "name", headerName: "Name", flex: 1.2, minWidth: 160 },
      { field: "email", headerName: "Email", flex: 1.4, minWidth: 200 },
      {
        field: "role",
        headerName: "Role",
        flex: 0.8,
        minWidth: 120,
        renderCell: (params) => <Chip size="small" label={params.value} />,
      },
      {
        field: "status",
        headerName: "Status",
        flex: 0.8,
        minWidth: 110,
        renderCell: (p) => (
          <Chip
            size="small"
            color={p.value === "Active" ? "success" : "default"}
            label={p.value}
          />
        ),
      },
      {
        field: "mustChangePassword",
        headerName: "Must change?",
        flex: 0.8,
        minWidth: 130,
        renderCell: (p) => (
          <Chip
            size="small"
            color={p.value ? "warning" : "default"}
            label={p.value ? "Yes" : "No"}
          />
        ),
      },
      {
        field: "lastPasswordResetAt",
        headerName: "Last reset",
        flex: 1,
        minWidth: 160,
        valueGetter: (p) => (p ? p : ""),
        renderCell: (p) =>
          p.value ? new Date(p.value as string).toLocaleString() : "—",
      },
      {
        field: "lastLogin",
        headerName: "Last login",
        flex: 1,
        minWidth: 160,
        valueGetter: (v) => (v ? v : ""),
        renderCell: (p) =>
          p.value ? new Date(p.value as string).toLocaleString() : "—",
      },
      {
        field: "actions",
        headerName: "Actions",
        sortable: false,
        filterable: false,
        width: 200,
        renderCell: (p) => {
          const isOnlyAdmin = p.row.role === "ADMIN" && adminCount <= 1;
          return (
            <Stack direction="row" spacing={0.5}>
              <Tooltip title="Edit user">
                <IconButton size="small" onClick={() => openEdit(p.row)}>
                  <EditIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title={isOnlyAdmin ? "Cannot delete the last admin" : "Delete user"}>
                <span>
                  <IconButton size="small" onClick={() => askDelete(p.row)} disabled={isOnlyAdmin}>
                    <Delete fontSize="small" />
                  </IconButton>
                </span>
              </Tooltip>
              <Tooltip title="More actions">
                <IconButton size="small" onClick={(e) => openMenuFor(e.currentTarget, p.row)}>
                  <MoreVertIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Stack>
          );
        },
      },
    ],
    [adminCount] // Re-run when adminCount changes
  );

  const existingUsernames = useMemo(() => {
    const list = rows.map((r) => r.username.toLowerCase());
    if (mode === "edit" && editing) {
      const idx = list.indexOf(editing.username.toLowerCase());
      if (idx > -1) list.splice(idx, 1);
    }
    return list;
  }, [rows, mode, editing]);

  const gridDescId = useId();

  // --- 5. RENDER LOGIC (Loading, Error, Empty, Data) ---
  const renderContent = () => {
    if (isLoading) {
      return (
        <Paper sx={{ height: 520, display: "grid", placeItems: "center" }}>
          <CircularProgress />
        </Paper>
      );
    }
    if (error) {
      return (
        <Paper sx={{ height: 520, p: 2, display: 'grid', placeItems: 'center' }}>
          <Alert severity="error">{error}</Alert>
        </Paper>
      );
    }
    if (filteredRows.length === 0) {
      return (
        <EmptyState
          title={rows.length === 0 ? "No users yet" : "No users match your filters"}
          description={
            rows.length === 0
              ? "Start by creating your first user."
              : "Try changing your search, role, or status filters."
          }
          actionText={rows.length === 0 ? "Add user" : "Reset filters"}
          onAction={rows.length === 0 ? openCreate : resetFilters}
        />
      );
    }
    return (
      <Paper sx={{ height: 520, p: 1 }}>
        <DataGrid
          rows={filteredRows}
          columns={columns}
          disableRowSelectionOnClick
          pageSizeOptions={[5, 10, 25]}
          initialState={{
            pagination: { paginationModel: { pageSize: 10 } },
          }}
          onRowDoubleClick={onRowDoubleClick}
          aria-label="Users table"
          aria-describedby={gridDescId}
        />
      </Paper>
    );
  };

  return (
    <Box>
      <span id={gridDescId} style={{ position: "absolute", width: 1, /*...*/ }}>
        Users data table. Use arrow keys to navigate rows and columns.
      </span>

      <Stack
        direction="row"
        alignItems="center"
        justifyContent="space-between"
        sx={{ mb: 2 }}
      >
        <Typography variant="h5" fontWeight={800} component="h1">
          Users
        </Typography>
        <Button variant="contained" startIcon={<Add />} onClick={openCreate}>
          Add user
        </Button>
      </Stack>

      <UsersToolbar
        filters={filters}
        onChange={setFilters}
        onReset={resetFilters}
        total={rows.length}
        showing={filteredRows.length}
      />

      {renderContent()}

      {/* --- Dialogs --- */}
      <UserForm
        open={formOpen}
        mode={mode}
        initial={
          mode === "edit" && editing
            ? { // Pass the fields your form expects
                username: editing.username,
                name: editing.name, // This 'name' field comes from the serializer
                email: editing.email,
                role: editing.role as Role, // Cast to your session Role
                status: editing.status,
              }
            : undefined
        }
        existingUsernames={existingUsernames}
        onClose={() => setFormOpen(false)}
        onSubmit={handleSubmitForm}
      />

      <ConfirmDialog
        open={confirmOpen}
        onClose={() => {
          setConfirmOpen(false);
          setToDelete(null);
        }}
        onConfirm={handleConfirmDelete}
        title="Delete user?"
        message={
          toDelete ? (
            <>
              This will permanently remove <b>{toDelete.username}</b>. This
              action cannot be undone.
            </>
          ) : null
        }
        confirmText="Delete"
        cancelText="Cancel"
        destructive
      />

      {/* More Menu */}
      <Menu
        anchorEl={menuAnchor}
        open={menuOpen}
        onClose={closeMenu}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
        transformOrigin={{ vertical: "top", horizontal: "right" }}
      >
        <MenuItem
          onClick={() => {
            closeMenu();
            askSendReset();
          }}
        >
          <ListItemIcon>
            <SendIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Send reset link…</ListItemText>
        </MenuItem>
        <MenuItem
          onClick={() => {
            closeMenu();
            askSetTemp();
          }}
        >
          <ListItemIcon>
            <LockResetIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Set temporary password…</ListItemText>
        </MenuItem>
        <MenuItem
          onClick={() => {
            closeMenu();
            toggleForceChange();
          }}
        >
          <ListItemIcon>
            <ChangeCircleIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>
            {menuUser?.mustChangePassword
              ? "Disable force change"
              : "Force change at next login"}
          </ListItemText>
        </MenuItem>
      </Menu>

      {/* Reset Link Confirm */}
      <ConfirmDialog
        open={resetConfirmOpen}
        onClose={() => {
          setResetConfirmOpen(false);
          setMenuUser(null);
        }}
        onConfirm={handleConfirmSendReset}
        title="Send password reset link?"
        message={
          menuUser ? (
            <>
              We will send a password reset link to <b>{menuUser.email}</b>.
              Continue?
            </>
          ) : null
        }
        confirmText="Send link"
        cancelText="Cancel"
        destructive={false}
      />

      {/* Set Temp Password Dialog */}
      <SetTempPasswordDialog
        open={tempOpen}
        email={menuUser?.email}
        onClose={() => {
          setTempOpen(false);
          setMenuUser(null);
        }}
        onSubmit={handleSetTempSubmit}
      />

      {SnackbarOutlet}
    </Box>
  );
}