import * as React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import AdminLayout from "./pages/admin/AdminLayout";
import AdminHome from "./pages/admin/AdminHome";
import UsersPage from "./pages/admin/users/UsersPage";
// import CreatorView from "./pages/creator/CreatorView";
import ProtectedRoute from "./components/ProtectedRoute";
import { useAuth } from "./contexts/AuthContext"; // <-- Import useAuth

export default function App() {
  const { user } = useAuth(); // <-- Get the user

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      {/* --- Protected Admin Routes --- */}
      <Route element={<ProtectedRoute />}>
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<AdminHome />} />
          <Route path="users" element={<UsersPage />} />
          <Route path="roles" element={<div>Roles (placeholder)</div>} />
          <Route path="settings" element={<div>Settings (placeholder)</div>} />
        </Route>
      </Route>

      {/* --- Protected Creator Routes --- */}
      <Route element={<ProtectedRoute />}>
        <Route path="/creator" element={<AdminLayout />}> 
          <Route index element={<AdminHome />} /> 
          <Route path="users" element={<UsersPage />} />
          <Route path="roles" element={<div>Roles (placeholder)</div>} />
          <Route path="settings" element={<div>Settings (placeholder)</div>} />
        </Route>
      </Route>

      {/* --- Add other roles like /reviewer and /viewer --- */}

      {/* --- Smart Redirect --- */}
      <Route 
        path="*" 
        element={
          user ? (
            // If logged in but at a bad URL, send to their home
            <Navigate to={`/${user.role.toLowerCase()}`} replace />
          ) : (
            // If not logged in, send to login
            <Navigate to="/login" replace />
          )
        } 
      />
    </Routes>
  );
}