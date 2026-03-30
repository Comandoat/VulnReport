import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getMe, login as apiLogin, logout as apiLogout } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const checkAuth = useCallback(async () => {
    try {
      const response = await getMe();
      setUser(response.data);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const loginFn = async (username, password) => {
    const response = await apiLogin(username, password);
    setUser(response.data.user || response.data);
    return response;
  };

  const logoutFn = async () => {
    try {
      await apiLogout();
    } finally {
      setUser(null);
    }
  };

  const isAuthenticated = !!user;
  const isAdmin = user?.role === 'admin';
  const isPentester = user?.role === 'pentester' || isAdmin;
  const isViewer = isAuthenticated;

  const value = {
    user,
    loading,
    isAuthenticated,
    isAdmin,
    isPentester,
    isViewer,
    login: loginFn,
    logout: logoutFn,
    checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
