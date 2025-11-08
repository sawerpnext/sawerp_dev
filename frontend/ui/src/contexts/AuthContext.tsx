import React, { createContext, useContext, useState, ReactNode, useEffect } from "react";
import axios from "axios"; // We still need axios for the token-auth call
import apiClient from "../lib/apiClient"; // <-- Import our new client
import type { User } from "../types/user"; // <-- We'll create this type

// --- Create a new types file ---
// Create a file at src/types/user.ts
// export interface User {
//   id: number;
//   username: string;
//   email: string;
//   first_name: string;
//   last_name: string;
//   role: 'CREATOR' | 'REVIEWER' | 'ADMIN' | 'VIEWER';
// }

// This is the base URL of your Django API
const API_URL = "http://127.0.0.1:8000/api";

interface AuthContextType {
  token: string | null;
  user: User | null; // <-- Use our new User type
  login: (username: string, password: string) => Promise<User>; // <-- Return the user
  logout: () => void;
  isLoading: boolean; // <-- Add loading state for startup
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem("token"));
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true); // <-- True on load

  // --- New Feature: Check login on app start ---
  useEffect(() => {
    const checkUser = async () => {
      if (token) {
        try {
          // Use the apiClient, which already has the token
          const response = await apiClient.get<User>("/users/me/");
          setUser(response.data);
        } catch (error) {
          // Token is invalid
          setToken(null);
          localStorage.removeItem("token");
        }
      }
      setIsLoading(false); // Done loading
    };

    checkUser();
  }, [token]);
  // ---

  const login = async (username: string, password: string): Promise<User> => {
    try {
      // 1. Get the token
      const response = await axios.post(
        `${API_URL}/token-auth/`,
        new URLSearchParams({ username, password }),
        { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
      );

      const { token } = response.data;
      setToken(token);
      localStorage.setItem("token", token);

      // 2. Set the token on our new client
      // (The interceptor will pick it up on the *next* request,
      // so we set it manually for this very first one)
      apiClient.defaults.headers.common["Authorization"] = `Token ${token}`;
      
      // 3. Get the user data
      const userResponse = await apiClient.get<User>("/users/me/");
      setUser(userResponse.data);
      
      return userResponse.data; // <-- Return the user

    } catch (error) {
      console.error("Login failed:", error);
      // Clean up on failure
      setToken(null);
      setUser(null);
      localStorage.removeItem("token");
      delete apiClient.defaults.headers.common["Authorization"];
      throw new Error("Login failed");
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("token");
    delete apiClient.defaults.headers.common["Authorization"];
  };

  // Show a loading spinner until we've checked the token
  if (isLoading) {
    return <div>Loading...</div>; // Or a <CircularProgress />
  }

  return (
    <AuthContext.Provider value={{ token, user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook to use the AuthContext
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}