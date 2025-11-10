import axios from "axios";

// This is the base URL of your Django API
const API_URL = "http://127.0.0.1:8000/api";

const apiClient = axios.create({
  baseURL: API_URL,
});

// We use an interceptor to add the token to every request.
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

export default apiClient;