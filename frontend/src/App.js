import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import ReportListPage from './pages/ReportListPage';
import ReportCreatePage from './pages/ReportCreatePage';
import ReportDetailPage from './pages/ReportDetailPage';
import KBListPage from './pages/KBListPage';
import KBDetailPage from './pages/KBDetailPage';
import UserManagementPage from './pages/UserManagementPage';
import AuditLogPage from './pages/AuditLogPage';

function App() {
  return (
    <AuthProvider>
      <div className="app">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/reports"
              element={
                <ProtectedRoute allowedRoles={['pentester', 'admin']}>
                  <ReportListPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/reports/new"
              element={
                <ProtectedRoute allowedRoles={['pentester', 'admin']}>
                  <ReportCreatePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/reports/:id"
              element={
                <ProtectedRoute allowedRoles={['viewer', 'pentester', 'admin']}>
                  <ReportDetailPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/kb"
              element={
                <ProtectedRoute>
                  <KBListPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/kb/:id"
              element={
                <ProtectedRoute>
                  <KBDetailPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/users"
              element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <UserManagementPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/audit"
              element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <AuditLogPage />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </AuthProvider>
  );
}

export default App;
