import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api/",
});

let isRefreshing = false;
let pendingRequests = [];

const resolvePendingRequests = (token) => {
  pendingRequests.forEach((callback) => callback(token));
  pendingRequests = [];
};

const clearAuthAndRedirect = () => {
  localStorage.removeItem("accessToken");
  localStorage.removeItem("refreshToken");
  if (window.location.pathname !== "/") {
    window.location.href = "/";
  }
};

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("accessToken");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error?.response?.status;

    if (!originalRequest || status !== 401) {
      return Promise.reject(error);
    }

    if (originalRequest._retry) {
      clearAuthAndRedirect();
      return Promise.reject(error);
    }

    const refreshToken = localStorage.getItem("refreshToken");
    if (!refreshToken) {
      clearAuthAndRedirect();
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    if (isRefreshing) {
      return new Promise((resolve) => {
        pendingRequests.push((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          resolve(api(originalRequest));
        });
      });
    }

    isRefreshing = true;

    try {
      const refreshResponse = await axios.post(
        "http://localhost:8000/api/auth/refresh/",
        { refresh: refreshToken }
      );
      const newAccessToken = refreshResponse.data.access;
      const rotatedRefreshToken = refreshResponse.data.refresh;

      localStorage.setItem("accessToken", newAccessToken);
      if (rotatedRefreshToken) {
        localStorage.setItem("refreshToken", rotatedRefreshToken);
      }

      resolvePendingRequests(newAccessToken);
      originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
      return api(originalRequest);
    } catch (refreshError) {
      pendingRequests = [];
      clearAuthAndRedirect();
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);

export default api;
