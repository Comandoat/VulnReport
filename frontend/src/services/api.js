import axios from 'axios';

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const csrfToken = getCookie('csrftoken');
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      const currentPath = window.location.pathname;
      if (currentPath !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const login = (username, password) =>
  api.post('/auth/login/', { username, password });

export const logout = () =>
  api.post('/auth/logout/');

export const getMe = () =>
  api.get('/auth/me/');

export const getUsers = () =>
  api.get('/users/');

export const updateUser = (id, data) =>
  api.patch(`/users/${id}/`, data);

export const createUser = (data) =>
  api.post('/users/', data);

export const getReports = (params) =>
  api.get('/reports/', { params });

export const createReport = (data) =>
  api.post('/reports/', data);

export const getReport = (id) =>
  api.get(`/reports/${id}/`);

export const updateReport = (id, data) =>
  api.patch(`/reports/${id}/`, data);

export const deleteReport = (id) =>
  api.delete(`/reports/${id}/`);

export const getFindings = (reportId) =>
  api.get(`/reports/${reportId}/findings/`);

export const createFinding = (reportId, data) =>
  api.post(`/reports/${reportId}/findings/`, data);

export const updateFinding = (reportId, findingId, data) =>
  api.patch(`/reports/${reportId}/findings/${findingId}/`, data);

export const deleteFinding = (reportId, findingId) =>
  api.delete(`/reports/${reportId}/findings/${findingId}/`);

export const reorderFindings = (reportId, data) =>
  api.post(`/reports/${reportId}/findings/reorder/`, data);

export const getKBEntries = (params) =>
  api.get('/kb/', { params });

export const getKBEntry = (id) =>
  api.get(`/kb/${id}/`);

export const createKBEntry = (data) =>
  api.post('/kb/', data);

export const updateKBEntry = (id, data) =>
  api.patch(`/kb/${id}/`, data);

export const deleteKBEntry = (id) =>
  api.delete(`/kb/${id}/`);

export const getResources = (params) =>
  api.get('/resources/', { params });

export const getAuditLogs = (params) =>
  api.get('/audit/', { params });

export default api;
