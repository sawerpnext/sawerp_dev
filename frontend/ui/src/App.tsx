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
  GlobalStyles,
} from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';

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

function App() {
  // State for the login form
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  // State to track if the user is logged in
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Hardcoded Credentials
  const HARDCODED_USERNAME = 'admin';
  const HARDCODED_PASSWORD = 'password123';

  // Handles the form submission event
  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError('');

    if (username === HARDCODED_USERNAME && password === HARDCODED_PASSWORD) {
      setIsLoggedIn(true);
    } else {
      setError('Invalid username or password. Please try again.');
    }
  };

  // Handles the logout action
  const handleLogout = () => {
    setIsLoggedIn(false);
    setUsername('');
    setPassword('');
    setError('');
  };

  return (
    <>
      <CssBaseline />
      {inputGlobalStyles}
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#f5f5f5',
        }}
      >
        <Container maxWidth={isLoggedIn ? "sm" : "xs"}>
          <Box
            sx={{
              padding: { xs: 2, sm: 4 },
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              backgroundColor: 'white',
              borderRadius: 2,
              boxShadow: 3,
            }}
          >
            {isLoggedIn ? (
              <>
                <Typography component="h1" variant="h4">
                  Welcome, {username}!
                </Typography>
                <Typography variant="body1" sx={{ mt: 2 }}>
                  You have successfully logged in.
                </Typography>
                <Button
                  onClick={handleLogout}
                  variant="contained"
                  sx={{ mt: 3, mb: 2 }}
                >
                  Logout
                </Button>
              </>
            ) : (
              <>
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
                    label="Username"
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
                    label="Password"
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
                  <FormControlLabel
                    control={<Checkbox value="remember" color="primary" />}
                    label="Remember me"
                  />
                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    sx={{ mt: 3, mb: 2 }}
                  >
                    Sign In
                  </Button>
                </Box>
              </>
            )}
          </Box>
        </Container>
      </Box>
    </>
  );
}

export default App;