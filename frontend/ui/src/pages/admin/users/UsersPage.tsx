import * as React from "react";
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

type UserRow = {
  id: string;
  username: string;
  name: string;
  email: string;
  role: Role;
  status: "Active" | "Inactive";
  lastLogin?: string;
  lastPasswordResetAt?: string;
  tempPasswordLastSetAt?: string;
  mustChangePassword?: boolean;
};

const INITIAL_ROWS: UserRow[] = [
  {
    id: "u1",
    username: "admin",
    name: "System Admin",
    email: "admin@example.com",
    role: "admin",
    status: "Active",
    lastLogin: new Date().toISOString(),
    lastPasswordResetAt: "",
    tempPasswordLastSetAt: "",
    mustChangePassword: false,
  },
  {
    id: "u2",
    username: "creator1",
    name: "Creator One",
    email: "creator1@example.com",
    role: "creator",
    status: "Active",
    lastLogin: "",
    lastPasswordResetAt: "",
    tempPasswordLastSetAt: "",
    mustChangePassword: false,
  },
  {
    id: "u3",
    username: "reviewer1",
    name: "Reviewer One",
    email: "reviewer1@example.com",
    role: "reviewer",
    status: "Inactive",
    lastLogin: "",
    lastPasswordResetAt: "",
    tempPasswordLastSetAt: "",
    mustChangePassword: true,
  },
];

type Mode = "create" | "edit";

export default function UsersPage() {
  const { showSuccess, showInfo, SnackbarOutlet } = useSnackbar();

  const [rows, setRows] = React.useState<UserRow[]>(INITIAL_ROWS);
  const [filters, setFilters] = React.useState<UsersFilters>({
    search: "",
    role: "all",
    status: "all",
  });

  // form / edit
  const [formOpen, setFormOpen] = React.useState(false);
  const [mode, setMode] = React.useState<Mode>("create");
  const [editing, setEditing] = React.useState<UserRow | null>(null);

  // delete confirm
  const [confirmOpen, setConfirmOpen] = React.useState(false);
  const [toDelete, setToDelete] = React.useState<UserRow | null>(null);

  // More menu
  const [menuAnchor, setMenuAnchor] = React.useState<null | HTMLElement>(null);
  const [menuUser, setMenuUser] = React.useState<UserRow | null>(null);
  const menuOpen = Boolean(menuAnchor);
  const openMenuFor = (el: HTMLElement, user: UserRow) => {
    setMenuAnchor(el);
    setMenuUser(user);
  };
  // IMPORTANT: don't clear menuUser here; keep selection for dialogs
  const closeMenu = () => {
    setMenuAnchor(null);
  };

  // Reset link confirm
  const [resetConfirmOpen, setResetConfirmOpen] = React.useState(false);
  const askSendReset = () => setResetConfirmOpen(true);
  const handleConfirmSendReset = () => {
    if (!menuUser) return;
    setRows((prev) =>
      prev.map((r) =>
        r.id === menuUser.id
          ? { ...r, lastPasswordResetAt: new Date().toISOString() }
          : r
      )
    );
    showSuccess(`Reset link sent to ${menuUser.email}`);
    setResetConfirmOpen(false);
    setMenuUser(null); // clear selection after dialog completes
  };

  // Set temp password dialog
  const [tempOpen, setTempOpen] = React.useState(false);
  const askSetTemp = () => setTempOpen(true);
  const handleSetTempSubmit = (payload: {
    password: string;
    expiresInMins: number;
    mustChange: boolean;
  }) => {
    if (!menuUser) return;
    // Do NOT store password; only safe metadata.
    setRows((prev) =>
      prev.map((r) =>
        r.id === menuUser.id
          ? {
              ...r,
              tempPasswordLastSetAt: new Date().toISOString(),
              mustChangePassword: payload.mustChange,
            }
          : r
      )
    );
    showSuccess(
      `Temporary password set for ${menuUser.email} (expires in ${Math.round(
        payload.expiresInMins / 60
      )}h)`
    );
    setTempOpen(false);
    setMenuUser(null); // clear selection after dialog completes
  };

  // Force change toggle
  const toggleForceChange = () => {
    if (!menuUser) return;
    setRows((prev) =>
      prev.map((r) =>
        r.id === menuUser.id
          ? { ...r, mustChangePassword: !r.mustChangePassword }
          : r
      )
    );
    const newVal = !menuUser.mustChangePassword;
    showInfo(
      `${newVal ? "Enabled" : "Disabled"} "force change at next login" for ${
        menuUser.username
      }`
    );
    // keep menuUser selected so menu label is consistent until closed
  };

  // Filtering
  const filteredRows = React.useMemo(() => {
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

  const askDelete = (row: UserRow) => {
    setToDelete(row);
    setConfirmOpen(true);
  };
  const handleConfirmDelete = () => {
    if (!toDelete) return;
    setRows((prev) => prev.filter((r) => r.id !== toDelete.id));
    showInfo(`Deleted user "${toDelete.username}" (in-memory)`);
    setConfirmOpen(false);
    setToDelete(null);
  };

  const onRowDoubleClick = (params: GridRowParams<UserRow>) =>
    openEdit(params.row);

  const columns = React.useMemo<GridColDef<UserRow>[]>(
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
        width: 180,
        renderCell: (p) => (
          <Stack direction="row" spacing={0.5}>
            <Tooltip title="Edit user">
              <IconButton
                size="small"
                onClick={() => openEdit(p.row)}
                aria-label={`Edit ${p.row.username}`}
              >
                <EditIcon fontSize="small" />
              </IconButton>
            </Tooltip>

            <Tooltip title="Delete user">
              <IconButton
                size="small"
                onClick={() => askDelete(p.row)}
                aria-label={`Delete ${p.row.username}`}
              >
                <Delete fontSize="small" />
              </IconButton>
            </Tooltip>

            {/* More menu trigger */}
            <Tooltip title="More actions">
              <IconButton
                size="small"
                aria-label={`More actions for ${p.row.username}`}
                onClick={(e) => openMenuFor(e.currentTarget, p.row)}
              >
                <MoreVertIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Stack>
        ),
      },
    ],
    []
  );

  // usernames for uniqueness (lowercased), excluding the one being edited
  const existingUsernames = React.useMemo(() => {
    const list = rows.map((r) => r.username.toLowerCase());
    if (mode === "edit" && editing) {
      const idx = list.indexOf(editing.username.toLowerCase());
      if (idx > -1) list.splice(idx, 1);
    }
    return list;
  }, [rows, mode, editing]);

  const handleSubmitForm = (values: UserFormValues) => {
    if (mode === "create") {
      const newRow: UserRow = {
        id: `u-${Date.now()}`,
        ...values,
        lastLogin: "",
        lastPasswordResetAt: "",
        tempPasswordLastSetAt: "",
        mustChangePassword: false,
      };
      setRows((prev) => [newRow, ...prev]);
      showSuccess("User created (in-memory)");
    } else if (mode === "edit" && editing) {
      setRows((prev) =>
        prev.map((r) => (r.id === editing.id ? { ...r, ...values } : r))
      );
      showSuccess("User updated (in-memory)");
    }
    setFormOpen(false);
  };

  // A11y helper for the grid
  const gridDescId = React.useId();

  return (
    <Box>
      {/* SR helper */}
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
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={openCreate}
          aria-label="Add new user"
        >
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

      {filteredRows.length === 0 ? (
        <EmptyState
          title={rows.length === 0 ? "No users yet" : "No users match your filters"}
          description={
            rows.length === 0
              ? "Start by creating your first user. You can always edit or remove them later."
              : "Try changing your search, role, or status filters."
          }
          actionText={rows.length === 0 ? "Add user" : "Reset filters"}
          onAction={rows.length === 0 ? openCreate : resetFilters}
        />
      ) : (
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
      )}

      {/* Create/Edit form */}
      <UserForm
        open={formOpen}
        mode={mode}
        initial={
          mode === "edit" && editing
            ? {
                username: editing.username,
                name: editing.name,
                email: editing.email,
                role: editing.role,
                status: editing.status,
              }
            : undefined
        }
        existingUsernames={existingUsernames}
        onClose={() => setFormOpen(false)}
        onSubmit={handleSubmitForm}
      />

      {/* Delete confirm */}
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

      {/* More menu */}
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
          aria-label={
            menuUser ? `Send reset link to ${menuUser.username}` : "Send reset link"
          }
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
          aria-label={
            menuUser
              ? `Set temporary password for ${menuUser.username}`
              : "Set temporary password"
          }
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
          aria-label={
            menuUser
              ? `Toggle force change for ${menuUser.username}`
              : "Toggle force change"
          }
        >
          <ListItemIcon>
            <ChangeCircleIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>
            {menuUser?.mustChangePassword
              ? "Disable force change at next login"
              : "Force change at next login"}
          </ListItemText>
        </MenuItem>
      </Menu>

      {/* Confirm “Send reset link” */}
      <ConfirmDialog
        open={resetConfirmOpen}
        onClose={() => {
          setResetConfirmOpen(false);
          setMenuUser(null); // clear on cancel/close
        }}
        onConfirm={handleConfirmSendReset}
        title="Send password reset link?"
        message={
          menuUser ? (
            <>
              We will send a password reset link to <b>{menuUser.email}</b>.
              The user can choose a new password securely. Continue?
            </>
          ) : null
        }
        confirmText="Send link"
        cancelText="Cancel"
        destructive={false}
      />

      {/* Set temporary password dialog */}
      <SetTempPasswordDialog
        open={tempOpen}
        email={menuUser?.email}
        onClose={() => {
          setTempOpen(false);
          setMenuUser(null); // clear on cancel/close
        }}
        onSubmit={handleSetTempSubmit}
      />

      {SnackbarOutlet}
    </Box>
  );
}
