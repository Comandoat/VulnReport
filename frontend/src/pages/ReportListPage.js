import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getReports } from '../services/api';

function ReportListPage() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      const res = await getReports();
      setReports(res.data.results || res.data || []);
    } catch {
      setReports([]);
    } finally {
      setLoading(false);
    }
  };

  const filtered = reports.filter((r) => {
    const matchesSearch = !search || r.title.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = !statusFilter || r.status === statusFilter;
    return matchesSearch && matchesStatus;
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
        <h1>Reports</h1>
        <Link to="/reports/new" className="btn btn-primary">
          + New Report
        </Link>
      </div>

      <div className="filters-bar">
        <input
          type="text"
          className="form-control"
          placeholder="Search by title..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className="form-control"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="in_progress">In Progress</option>
          <option value="finalized">Finalized</option>
          <option value="published">Published</option>
        </select>
      </div>

      {filtered.length === 0 ? (
        <div className="empty-state">
          <p>No reports found.</p>
          <Link to="/reports/new" className="btn btn-primary">
            Create your first report
          </Link>
        </div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Title</th>
                <th>Status</th>
                <th>Findings</th>
                <th>Created</th>
                <th>Updated</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((report) => (
                <tr
                  key={report.id}
                  className="clickable"
                  onClick={() => navigate(`/reports/${report.id}`)}
                >
                  <td style={{ fontWeight: 500 }}>{report.title}</td>
                  <td>
                    <span className={`status-badge status-${report.status}`}>
                      {report.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td>{report.findings_total || report.findings?.length || 0}</td>
                  <td>{new Date(report.created_at).toLocaleDateString()}</td>
                  <td>{new Date(report.updated_at || report.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default ReportListPage;
