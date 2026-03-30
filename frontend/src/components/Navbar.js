import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Navbar() {
  const { user, isAuthenticated, isAdmin, isPentester, logout } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) return null;

  const isActive = (path) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  const handleLogout = async () => {
    await logout();
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/" className="navbar-logo">
          <span className="logo-icon">&#9737;</span>
          VulnReport
        </Link>
      </div>

      <ul className="navbar-links">
        <li>
          <Link to="/" className={isActive('/') ? 'active' : ''}>
            Dashboard
          </Link>
        </li>

        {isPentester && (
          <li>
            <Link to="/reports" className={isActive('/reports') ? 'active' : ''}>
              Reports
            </Link>
          </li>
        )}

        <li>
          <Link to="/kb" className={isActive('/kb') ? 'active' : ''}>
            Knowledge Base
          </Link>
        </li>

        {isAdmin && (
          <>
            <li>
              <Link to="/admin/users" className={isActive('/admin/users') ? 'active' : ''}>
                Users
              </Link>
            </li>
            <li>
              <Link to="/admin/audit" className={isActive('/admin/audit') ? 'active' : ''}>
                Audit Log
              </Link>
            </li>
          </>
        )}
      </ul>

      <div className="navbar-user">
        <span className="user-info">
          <span className="user-name">{user.username}</span>
          <span className={`role-badge role-${user.role}`}>{user.role}</span>
        </span>
        <button onClick={handleLogout} className="btn btn-logout">
          Logout
        </button>
      </div>
    </nav>
  );
}

export default Navbar;
