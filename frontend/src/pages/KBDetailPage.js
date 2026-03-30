import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  getKBEntry,
  updateKBEntry,
  deleteKBEntry,
  createKBEntry,
  getReports,
  createFinding,
} from '../services/api';

function KBDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAdmin, isPentester } = useAuth();

  const isNew = id === 'new';
  const [entry, setEntry] = useState(null);
  const [loading, setLoading] = useState(!isNew);
  const [error, setError] = useState('');
  const [isEditing, setIsEditing] = useState(isNew);

  const [form, setForm] = useState({
    name: '',
    category: '',
    severity: 'medium',
    description: '',
    recommendation: '',
    references: '',
  });

  const [showReportModal, setShowReportModal] = useState(false);
  const [reports, setReports] = useState([]);

  const fetchEntry = useCallback(async () => {
    if (isNew) return;
    try {
      const res = await getKBEntry(id);
      setEntry(res.data);
      setForm({
        name: res.data.name || res.data.title || '',
        category: res.data.category || '',
        severity: res.data.severity || 'medium',
        description: res.data.description || '',
        recommendation: res.data.recommendation || '',
        references: res.data.references || '',
      });
    } catch {
      setError('Failed to load KB entry.');
    } finally {
      setLoading(false);
    }
  }, [id, isNew]);

  useEffect(() => {
    fetchEntry();
  }, [fetchEntry]);

  const handleSave = async () => {
    try {
      if (isNew) {
        const res = await createKBEntry(form);
        navigate(`/kb/${res.data.id}`, { replace: true });
      } else {
        const res = await updateKBEntry(id, form);
        setEntry(res.data);
        setIsEditing(false);
      }
    } catch (err) {
      if (err.response && err.response.data) {
        const messages = Object.values(err.response.data).flat().join(' ');
        setError(messages || 'Failed to save.');
      } else {
        setError('Network error.');
      }
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Delete this KB entry?')) return;
    try {
      await deleteKBEntry(id);
      navigate('/kb');
    } catch {
      setError('Failed to delete.');
    }
  };

  const openUseInReport = async () => {
    try {
      const res = await getReports();
      setReports(res.data.results || res.data || []);
    } catch {
      setReports([]);
    }
    setShowReportModal(true);
  };

  const addToReport = async (reportId) => {
    try {
      await createFinding(reportId, {
        title: entry.name || entry.title,
        severity: entry.severity || 'medium',
        description: entry.description || '',
        recommendation: entry.recommendation || '',
        references: entry.references || '',
        kb_entry: entry.id,
      });
      setShowReportModal(false);
      navigate(`/reports/${reportId}`);
    } catch {
      setError('Failed to add finding to report.');
    }
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
      </div>
    );
  }

  if (error && !entry && !isNew) {
    return <div className="error-message">{error}</div>;
  }

  if (isEditing) {
    return (
      <div>
        <div className="page-header">
          <h1>{isNew ? 'New KB Entry' : 'Edit KB Entry'}</h1>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="card" style={{ maxWidth: '700px' }}>
          <div className="form-group">
            <label>Name *</label>
            <input
              type="text"
              className="form-control"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
              autoFocus
            />
          </div>
          <div className="form-group">
            <label>Category</label>
            <input
              type="text"
              className="form-control"
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
              placeholder="e.g., Web, Network, Authentication"
            />
          </div>
          <div className="form-group">
            <label>Severity</label>
            <select
              className="form-control"
              value={form.severity}
              onChange={(e) => setForm({ ...form, severity: e.target.value })}
            >
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
              <option value="info">Info</option>
            </select>
          </div>
          <div className="form-group">
            <label>Description</label>
            <textarea
              className="form-control"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              rows={6}
            />
          </div>
          <div className="form-group">
            <label>Recommendation</label>
            <textarea
              className="form-control"
              value={form.recommendation}
              onChange={(e) => setForm({ ...form, recommendation: e.target.value })}
              rows={4}
            />
          </div>
          <div className="form-group">
            <label>References</label>
            <textarea
              className="form-control"
              value={form.references}
              onChange={(e) => setForm({ ...form, references: e.target.value })}
              rows={3}
              placeholder="One URL per line"
            />
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button className="btn btn-primary" onClick={handleSave}>
              {isNew ? 'Create' : 'Save'}
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => (isNew ? navigate('/kb') : setIsEditing(false))}
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!entry) return null;

  const referenceList = (entry.references || '')
    .split('\n')
    .map((r) => r.trim())
    .filter(Boolean);

  return (
    <div>
      {error && <div className="error-message">{error}</div>}

      <div className="detail-header">
        <div>
          <h1>{entry.name || entry.title}</h1>
        </div>
        <div className="detail-actions">
          {isPentester && (
            <button className="btn btn-primary" onClick={openUseInReport}>
              Use in Report
            </button>
          )}
          {isAdmin && (
            <>
              <button className="btn btn-secondary" onClick={() => setIsEditing(true)}>Edit</button>
              <button className="btn btn-danger" onClick={handleDelete}>Delete</button>
            </>
          )}
        </div>
      </div>

      <div className="detail-meta">
        {entry.category && <span>Category: {entry.category}</span>}
        <span>
          Severity:{' '}
          <span className={`severity-badge severity-${entry.severity || 'medium'}`}>
            {entry.severity || 'medium'}
          </span>
        </span>
        <span>Updated: {new Date(entry.updated_at || entry.created_at).toLocaleDateString()}</span>
      </div>

      {entry.description && (
        <div className="detail-section">
          <h2>Description</h2>
          <div className="content">{entry.description}</div>
        </div>
      )}

      {entry.recommendation && (
        <div className="detail-section">
          <h2>Recommendation</h2>
          <div className="content">{entry.recommendation}</div>
        </div>
      )}

      {referenceList.length > 0 && (
        <div className="detail-section">
          <h2>References</h2>
          <ul className="kb-references">
            {referenceList.map((ref, i) => (
              <li key={i}>
                {ref.startsWith('http') ? (
                  <a href={ref} target="_blank" rel="noopener noreferrer">{ref}</a>
                ) : (
                  ref
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {showReportModal && (
        <div className="modal-overlay" onClick={() => setShowReportModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Select Report</h2>
            {reports.length === 0 ? (
              <p style={{ color: 'var(--text-muted)' }}>No reports available.</p>
            ) : (
              <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                {reports
                  .filter((r) => r.status !== 'published')
                  .map((report) => (
                    <div
                      key={report.id}
                      className="finding-item"
                      style={{ cursor: 'pointer' }}
                      onClick={() => addToReport(report.id)}
                    >
                      <div className="finding-header">
                        <div className="finding-title">{report.title}</div>
                        <span className={`status-badge status-${report.status}`}>
                          {report.status.replace('_', ' ')}
                        </span>
                      </div>
                    </div>
                  ))}
              </div>
            )}
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => setShowReportModal(false)}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default KBDetailPage;
