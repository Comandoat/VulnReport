import React, { useState, useEffect, useCallback } from 'react';
import { getAuditLogs } from '../services/api';

function AuditLogPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [actionFilter, setActionFilter] = useState('');
  const [actorFilter, setActorFilter] = useState('');
  const pageSize = 25;

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page, page_size: pageSize };
      if (actionFilter) params.action = actionFilter;
      if (actorFilter) params.actor = actorFilter;

      const res = await getAuditLogs(params);
      const data = res.data;

      if (data.results) {
        setLogs(data.results);
        setTotalPages(Math.ceil((data.count || data.results.length) / pageSize));
      } else if (Array.isArray(data)) {
        setLogs(data);
        setTotalPages(1);
      } else {
        setLogs([]);
        setTotalPages(1);
      }
    } catch {
      setLogs([]);
    } finally {
      setLoading(false);
    }
  }, [page, actionFilter, actorFilter]);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  const handleFilterChange = (setter) => (e) => {
    setter(e.target.value);
    setPage(1);
  };

  return (
    <div>
      <div className="page-header">
        <h1>Audit Log</h1>
      </div>

      <div className="filters-bar">
        <input
          type="text"
          className="form-control"
          placeholder="Filter by actor..."
          value={actorFilter}
          onChange={handleFilterChange(setActorFilter)}
        />
        <select
          className="form-control"
          value={actionFilter}
          onChange={handleFilterChange(setActionFilter)}
        >
          <option value="">All Actions</option>
          <option value="create">Create</option>
          <option value="update">Update</option>
          <option value="delete">Delete</option>
          <option value="login">Login</option>
          <option value="logout">Logout</option>
          <option value="view">View</option>
        </select>
      </div>

      {loading ? (
        <div className="loading-screen" style={{ height: '40vh' }}>
          <div className="spinner"></div>
        </div>
      ) : logs.length === 0 ? (
        <div className="empty-state">
          <p>No audit logs found.</p>
        </div>
      ) : (
        <>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Actor</th>
                  <th>Action</th>
                  <th>Object Type</th>
                  <th>Object ID</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log, i) => (
                  <tr key={log.id || i}>
                    <td>
                      {new Date(log.timestamp || log.created_at).toLocaleString()}
                    </td>
                    <td style={{ fontWeight: 500 }}>{log.actor || log.user || '-'}</td>
                    <td>
                      <span className={`status-badge status-${getActionColor(log.action)}`}>
                        {log.action}
                      </span>
                    </td>
                    <td>{log.object_type || '-'}</td>
                    <td>{log.object_id || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button
                className="btn btn-secondary btn-small"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
              >
                Previous
              </button>
              <span className="page-info">
                Page {page} of {totalPages}
              </span>
              <button
                className="btn btn-secondary btn-small"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function getActionColor(action) {
  switch (action) {
    case 'create':
      return 'published';
    case 'delete':
      return 'draft';
    case 'update':
      return 'in_progress';
    case 'login':
      return 'finalized';
    case 'logout':
      return 'draft';
    default:
      return 'in_progress';
  }
}

export default AuditLogPage;
