import axios from 'axios';

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

function validateId(id) {
  const parsed = Number(id);
  if (!Number.isInteger(parsed) || parsed <= 0) {
    throw new Error('Invalid ID parameter.');
  }
  return parsed;
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
    if (error.response) {
      const status = error.response.status;
      const currentPath = window.location.pathname;

      if (status === 401 && currentPath !== '/login') {
        // Session expired — redirect to login
        window.location.href = '/login';
      }
      // 403 is a permission error — do NOT redirect, let the caller handle it
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
  api.get('/auth/users/');

export const updateUser = (id, data) => {
  const safeId = validateId(id);
  return api.patch(`/auth/users/${safeId}/`, data);
};

export const createUser = (data) =>
  api.post('/auth/register/', data);

export const getReports = (params) =>
  api.get('/reports/', { params });

export const createReport = (data) =>
  api.post('/reports/', data);

export const getReport = (id) => {
  const safeId = validateId(id);
  return api.get(`/reports/${safeId}/`);
};

export const updateReport = (id, data) => {
  const safeId = validateId(id);
  return api.patch(`/reports/${safeId}/`, data);
};

export const deleteReport = (id) => {
  const safeId = validateId(id);
  return api.delete(`/reports/${safeId}/`);
};

export const getFindings = (reportId) => {
  const safeReportId = validateId(reportId);
  return api.get(`/reports/${safeReportId}/findings/`);
};

export const createFinding = (reportId, data) => {
  const safeReportId = validateId(reportId);
  return api.post(`/reports/${safeReportId}/findings/`, data);
};

export const updateFinding = (reportId, findingId, data) => {
  const safeReportId = validateId(reportId);
  const safeFindingId = validateId(findingId);
  return api.patch(`/reports/${safeReportId}/findings/${safeFindingId}/`, data);
};

export const deleteFinding = (reportId, findingId) => {
  const safeReportId = validateId(reportId);
  const safeFindingId = validateId(findingId);
  return api.delete(`/reports/${safeReportId}/findings/${safeFindingId}/`);
};

export const reorderFindings = (reportId, data) => {
  const safeReportId = validateId(reportId);
  return api.post(`/reports/${safeReportId}/findings/reorder/`, data);
};

export const getKBEntries = (params) =>
  api.get('/kb/entries/', { params });

export const getKBEntry = (id) => {
  const safeId = validateId(id);
  return api.get(`/kb/entries/${safeId}/`);
};

export const createKBEntry = (data) =>
  api.post('/kb/entries/', data);

export const updateKBEntry = (id, data) => {
  const safeId = validateId(id);
  return api.patch(`/kb/entries/${safeId}/`, data);
};

export const deleteKBEntry = (id) => {
  const safeId = validateId(id);
  return api.delete(`/kb/entries/${safeId}/`);
};

export const getResources = (params) =>
  api.get('/kb/resources/', { params });

export const getAuditLogs = (params) =>
  api.get('/audit/logs/', { params });

export default api;
// API security fix - Diego
