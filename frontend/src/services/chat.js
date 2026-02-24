import api from "./api";

export const sendChatMessage = async (message) => {
  const response = await api.post("chat/intent-test/", { message });
  return response.data;
};

export const fetchChatHistory = async (limit = 50) => {
  const response = await api.get(`chat/intent-test/?limit=${limit}`);
  return response.data;
};
