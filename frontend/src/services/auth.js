import api from "./api";

export const loginUser = async (data) => {
  const response = await api.post("auth/login/", data);

  localStorage.setItem("accessToken", response.data.access);
  localStorage.setItem("refreshToken", response.data.refresh);

  return response.data;
};

export const registerUser = async (data) => {
  const response = await api.post("users/register/", data);
  return response.data;
};
