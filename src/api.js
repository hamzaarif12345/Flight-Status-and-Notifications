// src/api.js
import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:5000/api',
});

export const getFlights = () => API.get('/flights');
export const getUserSettings = (userId) => API.get(`/users/${userId}/settings`);
export const updateUserSettings = (userId, settings) =>
  API.put(`/users/${userId}/settings`, settings);
