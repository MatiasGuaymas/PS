import axios from 'axios'; 
const API_BASE_URL = import.meta.env.VITE_API_URL || 'admin-grupo21.proyecto2025.linti.unlp.edu.ar';

export const getFeatureFlag = async () => {
  const res = await axios.get(`${API_BASE_URL}/api/handler`)

  return res.data;
};
