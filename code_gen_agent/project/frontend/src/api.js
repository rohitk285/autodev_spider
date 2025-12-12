import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getAllTasks = () => api.get('/tasks');

export const createTask = (newTask) => api.post('/tasks', newTask);

export const updateTask = (id, updateData) => api.patch(`/tasks/${id}`, updateData);

export const deleteTask = (id) => api.delete(`/tasks/${id}`);
