import * as React from "react";
import {
  AppBar,
  Box,
  CssBaseline,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Avatar,
} from "@mui/material";
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Security as SecurityIcon,
  Tune as TuneIcon,
} from "@mui/icons-material";
import { Outlet, NavLink, useNavigate } from "react-router-dom";

const drawerWidth = 240;

type NavItem = { label: string; path: string; icon: React.ReactNode };

const NAV_ITEMS: NavItem[] = [
  { label: "Overview", path: "/admin", icon: <DashboardIcon /> },
  { label: "Users", path: "/admin/users", icon: <PeopleIcon /> },
  { label: "Roles", path: "/admin/roles", icon: <SecurityIcon /> },
  { label: "Settings", path: "/admin/settings", icon: <TuneIcon /> },
];

export default function AdminLayout() {
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const navigate = useNavigate();

  const drawer = (
    <Box sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <Box sx={{ display: "flex", alignItems: "center", p: 2, gap: 1 }}>
        <Avatar
          src="/logo.svg"
          alt="ERP"
          variant="rounded"
          sx={{ width: 36, height: 36, bgcolor: "primary.main" }}
        />
        <Typography variant="h6" fontWeight={800}>
          Admin
        </Typography>
      </Box>
      <Divider />
      <Box sx={{ flex: 1, overflowY: "auto" }}>
        <List sx={{ py: 1 }}>
          {NAV_ITEMS.map((item) => (
            <ListItemButton
              key={item.path}
              component={NavLink}
              to={item.path}
              // highlight active link
              sx={{
                mx: 1,
                borderRadius: 2,
                "&.active": {
                  bgcolor: "action.selected",
                  "& .MuiListItemIcon-root, & .MuiListItemText-primary": {
                    color: "primary.main",
                    fontWeight: 700,
                  },
                },
              }}
              onClick={() => setMobileOpen(false)}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          ))}
        </List>
      </Box>
      <Divider />
      <ListItemButton
        sx={{ m: 1, borderRadius: 2 }}
        onClick={() => navigate("/login")}
      >
        <ListItemText primary="Logout" />
      </ListItemButton>
    </Box>
  );

  return (
    <Box sx={{ display: "flex" }}>
      <CssBaseline />

      {/* Top bar */}
      <AppBar
        position="fixed"
        elevation={1}
        sx={{
          bgcolor: "background.paper",
          color: "text.primary",
          borderBottom: 1,
          borderColor: "divider",
          zIndex: (t) => t.zIndex.drawer + 1,
        }}
      >
        <Toolbar>
          {/* hamburger on small screens */}
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setMobileOpen((s) => !s)}
            sx={{ mr: 2, display: { md: "none" } }}
            aria-label="open navigation"
          >
            <MenuIcon />
          </IconButton>

          <Typography variant="h6" sx={{ fontWeight: 800 }}>
            ERP Admin
          </Typography>

          <Box sx={{ flex: 1 }} />

          {/* right-side avatar placeholder */}
          <Avatar sx={{ width: 32, height: 32 }}>A</Avatar>
        </Toolbar>
      </AppBar>

      {/* Sidebar — mobile (temporary) */}
      <Box component="nav" sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}>
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: "block", md: "none" },
            "& .MuiDrawer-paper": { boxSizing: "border-box", width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>

        {/* Sidebar — desktop (permanent) */}
        <Drawer
          variant="permanent"
          open
          sx={{
            display: { xs: "none", md: "block" },
            "& .MuiDrawer-paper": {
              boxSizing: "border-box",
              width: drawerWidth,
              borderRight: 1,
              borderColor: "divider",
            },
          }}
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          minHeight: "100dvh",
          bgcolor: "background.default",
        }}
      >
        {/* push content below app bar */}
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
}
