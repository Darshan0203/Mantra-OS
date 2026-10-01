import axios from 'axios';

export const apiClient = axios.create({
  baseURL: 'http://192.168.1.6:8000',
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
});