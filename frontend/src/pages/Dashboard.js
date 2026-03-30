import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getReports, getKBEntries, getAuditLogs } from '../services/api';

function Dashboard() {
  const { user, isAdmin, isPentester } = useAuth();
  const [stats, setStats] = useState({
    totalReports: 0,
    publishedReports: 0,
    draftReports: 0,
    inProgressReports: 0,
    findings: { critical: 0, high: 0, medium: 0, low: 0, info: 0 },
    kbCount: 0,
    recentReports: [],
    recentActivity: [],
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        const [reportsRes, kbRes] = await Promise.all([
          getReports(),
          getKBEntries(),
        ]);

        const reports = reportsRes.data.results || reportsRes.data || [];
        const kbEntries = kbRes.data.results || kbRes.data || [];

        const totalReports = reports.length;
        const publishedReports = reports.filter((r) => r.status === 'published').length;
        const draftReports = reports.filter((r) => r.status === 'draft').length;
        const inProgressReports = reports.filter((r) => r.status === 'in_progress').length;

        const findings = { critical: 0, high: 0, medium: 0, low: 0, info: 0 };
        reports.forEach((r) => {
          if (r.findings_count) {
            Object.keys(r.findings_count).forEach((sev) => {
              if (findings[sev] !== undefined) {
                findings[sev] += r.findings_count[sev];
              }
            });
          } else if (r.findings_summary) {
            Object.keys(r.findings_summary).forEach((sev) => {
              if (findings[sev] !== undefined) {
                findings[sev] += r.findings_summary[sev];
              }
            });
          }
        });

        const recentReports = [...reports]
          .sort((a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at))
          .slice(0, 5);

        let recentActivity = [];
        if (isAdmin) {
          try {
            const auditRes = await getAuditLogs({ page_size: 5 });
            recentActivity = auditRes.data.results || auditRes.data || [];
          } catch {
            recentActivity = [];
          }
        }

        setStats({
          totalReports,
          publishedReports,
          draftReports,
          inProgressReports,
          findings,
          kbCount: kbEntries.length,
          recentReports,
          recentActivity,
        });
      } catch {
        // Stats will remain at defaults
      } finally {
        setLoading(false);
      }
    }

    fetchStats();
  }, [isAdmin]);

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
        <h1>Dashboard</h1>
        <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          Welcome back, {user?.username}
        </span>
      </div>

      {isAdmin && <AdminDashboard stats={stats} />}
      {!isAdmin && isPentester && <PentesterDashboard stats={stats} />}
      {!isPentester && <ViewerDashboard stats={stats} />}
    </div>
  );
}

function AdminDashboard({ stats }) {
  return (
    <>
      <div className="card-grid">
        <div className="stat-card blue">
          <span className="stat-label">Total Reports</span>
          <span className="stat-value">{stats.totalReports}</span>
        </div>
        <div className="stat-card critical">
          <span className="stat-label">Critical Findings</span>
          <span className="stat-value">{stats.findings.critical}</span>
        </div>
        <div className="stat-card high">
          <span className="stat-label">High Findings</span>
          <span className="stat-value">{stats.findings.high}</span>
        </div>
        <div className="stat-card medium">
          <span className="stat-label">Medium Findings</span>
          <span className="stat-value">{stats.findings.medium}</span>
        </div>
        <div className="stat-card low">
          <span className="stat-label">Low Findings</span>
          <span className="stat-value">{stats.findings.low}</span>
        </div>
        <div className="stat-card cyan">
          <span className="stat-label">KB Entries</span>
          <span className="stat-value">{stats.kbCount}</span>
        </div>
      </div>

      <div className="detail-section">
        <h2>Recent Activity</h2>
        {stats.recentActivity.length > 0 ? (
          <table>
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Actor</th>
                <th>Action</th>
                <th>Object</th>
              </tr>
            </thead>
            <tbody>
              {stats.recentActivity.map((log, i) => (
                <tr key={i}>
                  <td>{new Date(log.timestamp || log.created_at).toLocaleString()}</td>
                  <td>{log.actor || log.user || '-'}</td>
                  <td>{log.action}</td>
                  <td>{log.object_type} #{log.object_id}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: 'var(--text-muted)' }}>No recent activity</p>
        )}
      </div>

      <RecentReports reports={stats.recentReports} />
    </>
  );
}

function PentesterDashboard({ stats }) {
  return (
    <>
      <div className="card-grid">
        <div className="stat-card blue">
          <span className="stat-label">My Reports</span>
          <span className="stat-value">{stats.totalReports}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Draft</span>
          <span className="stat-value" style={{ color: 'var(--status-draft)' }}>{stats.draftReports}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">In Progress</span>
          <span className="stat-value" style={{ color: 'var(--status-in-progress)' }}>{stats.inProgressReports}</span>
        </div>
        <div className="stat-card critical">
          <span className="stat-label">Critical Findings</span>
          <span className="stat-value">{stats.findings.critical}</span>
        </div>
        <div className="stat-card high">
          <span className="stat-label">High Findings</span>
          <span className="stat-value">{stats.findings.high}</span>
        </div>
        <div className="stat-card medium">
          <span className="stat-label">Medium Findings</span>
          <span className="stat-value">{stats.findings.medium}</span>
        </div>
      </div>

      <div style={{ marginBottom: '1rem' }}>
        <Link to="/reports/new" className="btn btn-primary">
          + New Report
        </Link>
      </div>

      <RecentReports reports={stats.recentReports} />
    </>
  );
}

function ViewerDashboard({ stats }) {
  return (
    <>
      <div className="card-grid">
        <div className="stat-card blue">
          <span className="stat-label">Published Reports</span>
          <span className="stat-value">{stats.publishedReports}</span>
        </div>
        <div className="stat-card cyan">
          <span className="stat-label">KB Entries</span>
          <span className="stat-value">{stats.kbCount}</span>
        </div>
      </div>

      <RecentReports reports={stats.recentReports.filter((r) => r.status === 'published')} />
    </>
  );
}

function RecentReports({ reports }) {
  if (reports.length === 0) {
    return (
      <div className="detail-section">
        <h2>Recent Reports</h2>
        <div className="empty-state">
          <p>No reports yet.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="detail-section">
      <h2>Recent Reports</h2>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Status</th>
              <th>Updated</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((report) => (
              <tr key={report.id} className="clickable">
                <td>
                  <Link to={`/reports/${report.id}`}>{report.title}</Link>
                </td>
                <td>
                  <span className={`status-badge status-${report.status}`}>
                    {report.status.replace('_', ' ')}
                  </span>
                </td>
                <td>{new Date(report.updated_at || report.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Dashboard;
