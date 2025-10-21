import React, { useState } from 'react';
import {
  Container,
  Box,
  TextField,
  Button,
  Typography,
  Avatar,
  CssBaseline,
  FormControlLabel,
  Checkbox,
  Grid,
  Link as MuiLink,
  GlobalStyles,
  AppBar,
  Toolbar,
  IconButton,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import CreateIcon from '@mui/icons-material/Create';
import RateReviewIcon from '@mui/icons-material/RateReview';
import VisibilityIcon from '@mui/icons-material/Visibility';
import LogoutIcon from '@mui/icons-material/Logout';

// --- 1. DEFINE TYPES AND DATA STRUCTURE ---

// Define the possible roles
type Role = 'admin' | 'creator' | 'reviewer' | 'viewer';

// Define the structure for a user object
interface User {
  username: string;
  password: string;
  role: Role;
}

// Hardcode a list of users with different roles
const HARDCODED_USERS: User[] = [
  { username: 'admin', password: 'password', role: 'admin' },
  { username: 'creator', password: 'password', role: 'creator' },
  { username: 'reviewer', password: 'password', role: 'reviewer' },
  { username: 'viewer', password: 'password', role: 'viewer' },
];

// Global styles to ensure the root element and body take up full height
const inputGlobalStyles = (
  <GlobalStyles
    styles={{
      'html, body, #root': {
        height: '100%',
        margin: 0,
        padding: 0,
        backgroundColor: '#f5f5f5',
      },
    }}
  />
);

// --- 4. CREATE ROLE-BASED DASHBOARD COMPONENTS ---

interface DashboardProps {
  user: User;
  onLogout: () => void;
}

const AdminDashboard: React.FC<DashboardProps> = ({ user, onLogout }) => (
  <Paper sx={{ p: 3, display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
    <AdminPanelSettingsIcon color="primary" sx={{ fontSize: 60, mb: 2 }} />
    <Typography variant="h5" gutterBottom>Admin Control Panel</Typography>
    <Typography>Welcome, {user.username}. You have full system access.</Typography>
    <List>
      <ListItem><ListItemIcon><AdminPanelSettingsIcon /></ListItemIcon><ListItemText primary="Manage Users" /></ListItem>
      <ListItem><ListItemIcon><AdminPanelSettingsIcon /></ListItemIcon><ListItemText primary="System Settings" /></ListItem>
    </List>
  </Paper>
);

const CreatorDashboard: React.FC<DashboardProps> = ({ user, onLogout }) => (
  <Paper sx={{ p: 3, display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
    <CreateIcon color="secondary" sx={{ fontSize: 60, mb: 2 }} />
    <Typography variant="h5" gutterBottom>Creator Dashboard</Typography>
    <Typography>Welcome, {user.username}. Let's create something new.</Typography>
     <List>
      <ListItem><ListItemIcon><CreateIcon /></ListItemIcon><ListItemText primary="Create New Content" /></ListItem>
      <ListItem><ListItemIcon><CreateIcon /></ListItemIcon><ListItemText primary="View My Drafts" /></ListItem>
    </List>
  </Paper>
);

const ReviewerDashboard: React.FC<DashboardProps> = ({ user, onLogout }) => (
  <Paper sx={{ p: 3, display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
    <RateReviewIcon sx={{ fontSize: 60, mb: 2, color: 'orange' }} />
    <Typography variant="h5" gutterBottom>Reviewer Dashboard</Typography>
    <Typography>Welcome, {user.username}. You have content to review.</Typography>
    <List>
      <ListItem><ListItemIcon><RateReviewIcon /></ListItemIcon><ListItemText primary="Content Approval Queue" /></ListItem>
      <ListItem><ListItemIcon><RateReviewIcon /></ListItemIcon><ListItemText primary="Submission History" /></ListItem>
    </List>
  </Paper>
);

const ViewerDashboard: React.FC<DashboardProps> = ({ user, onLogout }) => (
  <Paper sx={{ p: 3, display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
    <VisibilityIcon sx={{ fontSize: 60, mb: 2, color: 'green' }} />
    <Typography variant="h5" gutterBottom>Viewer Dashboard</Typography>
    <Typography>Welcome, {user.username}. Here is the latest content.</Typography>
     <List>
      <ListItem><ListItemIcon><VisibilityIcon /></ListItemIcon><ListItemText primary="Browse Published Articles" /></ListItem>
      <ListItem><ListItemIcon><VisibilityIcon /></ListItemIcon><ListItemText primary="Search Content" /></ListItem>
    </List>
  </Paper>
);

// --- MAIN APP COMPONENT ---

function App() {
  // Form fields state
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  // --- 3. MANAGE USER STATE ---
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  /**
   * --- 2. UPDATE LOGIN LOGIC ---
   * Handles the form submission event.
   */
  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError('');

    // Find the user in our hardcoded list
    const foundUser = HARDCODED_USERS.find(user => user.username === username);

    // Check if user was found and if the password matches
    if (foundUser && foundUser.password === password) {
      console.log('Login successful for role:', foundUser.role);
      setCurrentUser(foundUser);
    } else {
      console.log('Login failed: Invalid credentials.');
      setError('Invalid username or password. Please try again.');
      setCurrentUser(null);
    }
  };

  /**
   * Handles the logout action.
   */
  const handleLogout = () => {
    setCurrentUser(null);
    setUsername('');
    setPassword('');
    setError('');
  };

  // --- 5. CONDITIONAL RENDERING ---

  // If a user is logged in, render their dashboard
  if (currentUser) {
    let DashboardComponent;
    switch (currentUser.role) {
      case 'admin':
        DashboardComponent = <AdminDashboard user={currentUser} onLogout={handleLogout} />;
        break;
      case 'creator':
        DashboardComponent = <CreatorDashboard user={currentUser} onLogout={handleLogout} />;
        break;
      case 'reviewer':
        DashboardComponent = <ReviewerDashboard user={currentUser} onLogout={handleLogout} />;
        break;
      case 'viewer':
        DashboardComponent = <ViewerDashboard user={currentUser} onLogout={handleLogout} />;
        break;
      default:
        // This is a fallback, should not be reached with the current logic
        return <Typography color="error">Error: Unknown user role.</Typography>;
    }

    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <CssBaseline />
        {inputGlobalStyles}
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              SAW ERP - Role: {currentUser.role.charAt(0).toUpperCase() + currentUser.role.slice(1)}
            </Typography>
            <IconButton color="inherit" onClick={handleLogout} aria-label="logout">
              <LogoutIcon />
            </IconButton>
          </Toolbar>
        </AppBar>
        <Container component="main" maxWidth="md" sx={{ mt: 4, mb: 4 }}>
          {DashboardComponent}
        </Container>
      </Box>
    );
  }

  // If no user is logged in, render the login form
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%',
      }}
    >
      <CssBaseline />
      {inputGlobalStyles}
      <Container component="main" maxWidth="xs">
        <Paper elevation={6} sx={{ padding: { xs: 2, sm: 4 }, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <Avatar sx={{ m: 1, bgcolor: 'secondary.main' }}>
            <LockOutlinedIcon />
          </Avatar>
          <Typography component="h1" variant="h5">
            Sign in
          </Typography>
          <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="Username (e.g., admin, creator)"
              name="username"
              autoComplete="username"
              autoFocus
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password (it's 'password')"
              type="password"
              id="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            {error && (
              <Typography color="error" variant="body2" align="center" sx={{ mt: 1 }}>
                {error}
              </Typography>
            )}
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
            >
              Sign In
            </Button>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
}

export default App;

