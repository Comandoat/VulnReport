import React, { useState, useEffect } from 'react';
import { getUsers, updateUser, createUser } from '../services/api';

function UserManagementPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createForm, setCreateForm] = useState({
    username: '',
    email: '',
    password: '',
    role: 'viewer',
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const res = await getUsers();
      setUsers(res.data.results || res.data || []);
    } catch {
      setError('Failed to load users.');
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (userId, newRole) => {
    setError('');
    setSuccess('');
    try {
      await updateUser(userId, { role: newRole });
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, role: newRole } : u))
      );
      setSuccess('Role updated successfully.');
    } catch {
      setError('Failed to update role.');
    }
  };

  const handleToggleActive = async (userId, currentActive) => {
    setError('');
    setSuccess('');
    try {
      await updateUser(userId, { is_active: !currentActive });
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, is_active: !currentActive } : u))
      );
      setSuccess('User status updated.');
    } catch {
      setError('Failed to update user status.');
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      const res = await createUser(createForm);
      setUsers((prev) => [...prev, res.data]);
      setShowCreateForm(false);
      setCreateForm({ username: '', email: '', password: '', role: 'viewer' });
      setSuccess('User created successfully.');
    } catch (err) {
      if (err.response && err.response.data) {
        const messages = Object.values(err.response.data).flat().join(' ');
        setError(messages || 'Failed to create user.');
      } else {
        setError('Network error.');
      }
    }
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <h1>User Management</h1>
        <button className="btn btn-primary" onClick={() => setShowCreateForm(!showCreateForm)}>
          {showCreateForm ? 'Cancel' : '+ New User'}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      {showCreateForm && (
        <div className="card" style={{ marginBottom: '1.5rem', maxWidth: '500px' }}>
          <h2 style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>Create New User</h2>
          <form onSubmit={handleCreateUser}>
            <div className="form-group">
              <label>Username *</label>
              <input
                type="text"
                className="form-control"
                value={createForm.username}
                onChange={(e) => setCreateForm({ ...createForm, username: e.target.value })}
                required
                autoFocus
              />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                className="form-control"
                value={createForm.email}
                onChange={(e) => setCreateForm({ ...createForm, email: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>Password *</label>
              <input
                type="password"
                className="form-control"
                value={createForm.password}
                onChange={(e) => setCreateForm({ ...createForm, password: e.target.value })}
                required
                autoComplete="new-password"
              />
            </div>
            <div className="form-group">
              <label>Role</label>
              <select
                className="form-control"
                value={createForm.role}
                onChange={(e) => setCreateForm({ ...createForm, role: e.target.value })}
              >
                <option value="viewer">Viewer</option>
                <option value="pentester">Pentester</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            <button type="submit" className="btn btn-primary">Create User</button>
          </form>
        </div>
      )}

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Username</th>
              <th>Email</th>
              <th>Role</th>
              <th>Active</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td style={{ fontWeight: 500 }}>{u.username}</td>
                <td>{u.email || '-'}</td>
                <td>
                  <select
                    className="form-control"
                    value={u.role}
                    onChange={(e) => handleRoleChange(u.id, e.target.value)}
                    style={{ width: 'auto', padding: '0.3rem 0.5rem', fontSize: '0.8rem' }}
                  >
                    <option value="viewer">Viewer</option>
                    <option value="pentester">Pentester</option>
                    <option value="admin">Admin</option>
                  </select>
                </td>
                <td>
                  <span
                    className={`status-badge ${u.is_active ? 'status-published' : 'status-draft'}`}
                  >
                    {u.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td>{new Date(u.date_joined || u.created_at).toLocaleDateString()}</td>
                <td>
                  <button
                    className={`btn btn-small ${u.is_active ? 'btn-danger' : 'btn-primary'}`}
                    onClick={() => handleToggleActive(u.id, u.is_active)}
                  >
                    {u.is_active ? 'Deactivate' : 'Activate'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default UserManagementPage;
