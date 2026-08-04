import axios from "axios";

const API_URL = "http://localhost:5000/schemes";

export const getAllSchemes = async () => {
  const response = await axios.get(API_URL);
  return response.data.data;
};

export const getSchemeById = async (id) => {
  const response = await axios.get(`${API_URL}/${id}`);
  return response.data.data;
};

export const searchSchemes = async (query) => {
  const response = await axios.get(
    `${API_URL}/search?query=${query}`
  );

  return response.data.data;
};

export const filterSchemes = async (category, state) => {
  const response = await axios.get(
    `${API_URL}/filter?category=${category}&state=${state}`
  );

  return response.data.data;
};