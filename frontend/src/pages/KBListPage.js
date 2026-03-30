import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getKBEntries, deleteKBEntry } from '../services/api';

function KBListPage() {
  const { isAdmin } = useAuth();
  const navigate = useNavigate();
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  useEffect(() => {
    fetchEntries();
  }, []);

  const fetchEntries = async () => {
    try {
      const res = await getKBEntries();
      setEntries(res.data.results || res.data || []);
    } catch {
      setEntries([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm('Delete this KB entry?')) return;
    try {
      await deleteKBEntry(id);
      setEntries((prev) => prev.filter((entry) => entry.id !== id));
    } catch {
      alert('Failed to delete KB entry.');
    }
  };

  const categories = [...new Set(entries.map((e) => e.category).filter(Boolean))];

  const filtered = entries.filter((e) => {
    const name = e.name || e.title || '';
    const matchesSearch = !search || name.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = !categoryFilter || e.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

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
        <h1>Knowledge Base</h1>
        {isAdmin && (
          <button className="btn btn-primary" onClick={() => navigate('/kb/new')}>
            + New Entry
          </button>
        )}
      </div>

      <div className="filters-bar">
        <input
          type="text"
          className="form-control"
          placeholder="Search by name..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className="form-control"
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
        >
          <option value="">All Categories</option>
          {categories.map((cat) => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
      </div>

      {filtered.length === 0 ? (
        <div className="empty-state">
          <p>No KB entries found.</p>
        </div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Category</th>
                <th>Severity</th>
                <th>Updated</th>
                {isAdmin && <th>Actions</th>}
              </tr>
            </thead>
            <tbody>
              {filtered.map((entry) => (
                <tr
                  key={entry.id}
                  className="clickable"
                  onClick={() => navigate(`/kb/${entry.id}`)}
                >
                  <td style={{ fontWeight: 500 }}>{entry.name || entry.title}</td>
                  <td>{entry.category || '-'}</td>
                  <td>
                    <span className={`severity-badge severity-${entry.severity || 'medium'}`}>
                      {entry.severity || 'medium'}
                    </span>
                  </td>
                  <td>{new Date(entry.updated_at || entry.created_at).toLocaleDateString()}</td>
                  {isAdmin && (
                    <td>
                      <button
                        className="btn btn-danger btn-small"
                        onClick={(e) => handleDelete(e, entry.id)}
                      >
                        Delete
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default KBListPage;
// KB list - Diego
