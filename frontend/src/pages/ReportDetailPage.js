import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  getReport,
  updateReport,
  deleteReport,
  getFindings,
  createFinding,
  updateFinding,
  deleteFinding,
  reorderFindings,
  getKBEntries,
} from '../services/api';

function ReportDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, isAdmin } = useAuth();

  const [report, setReport] = useState(null);
  const [findings, setFindings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [showKBModal, setShowKBModal] = useState(false);
  const [kbEntries, setKBEntries] = useState([]);
  const [kbSearch, setKBSearch] = useState('');

  const [showFindingForm, setShowFindingForm] = useState(false);
  const [editingFinding, setEditingFinding] = useState(null);
  const [findingForm, setFindingForm] = useState({
    title: '',
    severity: 'medium',
    description: '',
    recommendation: '',
    references: '',
  });

  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    title: '',
    context: '',
    executive_summary: '',
  });

  const isOwner = report && user && (report.owner === user.id || report.owner === user.username);
  const canEdit = isOwner || isAdmin;

  const fetchData = useCallback(async () => {
    try {
      const [reportRes, findingsRes] = await Promise.all([
        getReport(id),
        getFindings(id),
      ]);
      setReport(reportRes.data);
      setFindings(findingsRes.data.results || findingsRes.data || []);
      setEditForm({
        title: reportRes.data.title || '',
        context: reportRes.data.context || '',
        executive_summary: reportRes.data.executive_summary || '',
      });
    } catch {
      setError('Failed to load report.');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleStatusChange = async (newStatus) => {
    try {
      await updateReport(id, { status: newStatus });
      setReport((prev) => ({ ...prev, status: newStatus }));
    } catch {
      setError('Failed to update status.');
    }
  };

  const handleDeleteReport = async () => {
    if (!window.confirm('Are you sure you want to delete this report?')) return;
    try {
      await deleteReport(id);
      navigate('/reports');
    } catch {
      setError('Failed to delete report.');
    }
  };

  const handleSaveEdit = async () => {
    try {
      const res = await updateReport(id, editForm);
      setReport(res.data);
      setIsEditing(false);
    } catch {
      setError('Failed to update report.');
    }
  };

  const openKBModal = async () => {
    try {
      const res = await getKBEntries();
      setKBEntries(res.data.results || res.data || []);
    } catch {
      setKBEntries([]);
    }
    setShowKBModal(true);
  };

  const addFromKB = async (entry) => {
    try {
      await createFinding(id, {
        title: entry.name || entry.title,
        severity: entry.severity || 'medium',
        description: entry.description || '',
        recommendation: entry.recommendation || '',
        references: entry.references || '',
        kb_entry: entry.id,
      });
      setShowKBModal(false);
      fetchData();
    } catch {
      setError('Failed to add finding from KB.');
    }
  };

  const openFindingForm = (finding) => {
    if (finding) {
      setEditingFinding(finding);
      setFindingForm({
        title: finding.title || '',
        severity: finding.severity || 'medium',
        description: finding.description || '',
        recommendation: finding.recommendation || '',
        references: finding.references || '',
      });
    } else {
      setEditingFinding(null);
      setFindingForm({
        title: '',
        severity: 'medium',
        description: '',
        recommendation: '',
        references: '',
      });
    }
    setShowFindingForm(true);
  };

  const handleSaveFinding = async () => {
    try {
      if (editingFinding) {
        await updateFinding(id, editingFinding.id, findingForm);
      } else {
        await createFinding(id, findingForm);
      }
      setShowFindingForm(false);
      fetchData();
    } catch {
      setError('Failed to save finding.');
    }
  };

  const handleDeleteFinding = async (findingId) => {
    if (!window.confirm('Delete this finding?')) return;
    try {
      await deleteFinding(id, findingId);
      setFindings((prev) => prev.filter((f) => f.id !== findingId));
    } catch {
      setError('Failed to delete finding.');
    }
  };

  const moveFinding = async (index, direction) => {
    const newFindings = [...findings];
    const targetIndex = index + direction;
    if (targetIndex < 0 || targetIndex >= newFindings.length) return;

    [newFindings[index], newFindings[targetIndex]] = [newFindings[targetIndex], newFindings[index]];
    setFindings(newFindings);

    try {
      await reorderFindings(id, {
        order: newFindings.map((f) => f.id),
      });
    } catch {
      fetchData();
    }
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
      </div>
    );
  }

  if (error && !report) {
    return <div className="error-message">{error}</div>;
  }

  if (!report) return null;

  const filteredKB = kbEntries.filter(
    (e) =>
      !kbSearch ||
      (e.name || e.title || '').toLowerCase().includes(kbSearch.toLowerCase())
  );

  return (
    <div>
      {error && <div className="error-message">{error}</div>}

      {isEditing ? (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <div className="form-group">
            <label>Title</label>
            <input
              type="text"
              className="form-control"
              value={editForm.title}
              onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Context</label>
            <textarea
              className="form-control"
              value={editForm.context}
              onChange={(e) => setEditForm({ ...editForm, context: e.target.value })}
              rows={3}
            />
          </div>
          <div className="form-group">
            <label>Executive Summary</label>
            <textarea
              className="form-control"
              value={editForm.executive_summary}
              onChange={(e) => setEditForm({ ...editForm, executive_summary: e.target.value })}
              rows={5}
            />
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button className="btn btn-primary" onClick={handleSaveEdit}>Save</button>
            <button className="btn btn-secondary" onClick={() => setIsEditing(false)}>Cancel</button>
          </div>
        </div>
      ) : (
        <>
          <div className="detail-header">
            <div>
              <h1>{report.title}</h1>
            </div>
            <div className="detail-actions">
              {canEdit && (
                <>
                  <select
                    className="form-control"
                    value={report.status}
                    onChange={(e) => handleStatusChange(e.target.value)}
                    style={{ width: 'auto' }}
                  >
                    <option value="draft">Draft</option>
                    <option value="in_progress">In Progress</option>
                    <option value="finalized">Finalized</option>
                    <option value="published">Published</option>
                  </select>
                  <button className="btn btn-secondary" onClick={() => setIsEditing(true)}>Edit</button>
                  <button className="btn btn-danger" onClick={handleDeleteReport}>Delete</button>
                </>
              )}
            </div>
          </div>

          <div className="detail-meta">
            <span>
              Status: <span className={`status-badge status-${report.status}`}>{report.status.replace('_', ' ')}</span>
            </span>
            <span>Owner: {report.owner_username || report.owner}</span>
            <span>Created: {new Date(report.created_at).toLocaleDateString()}</span>
            <span>Updated: {new Date(report.updated_at || report.created_at).toLocaleDateString()}</span>
          </div>

          {report.context && (
            <div className="detail-section">
              <h2>Context</h2>
              <div className="content">{report.context}</div>
            </div>
          )}

          {report.executive_summary && (
            <div className="detail-section">
              <h2>Executive Summary</h2>
              <div className="content">{report.executive_summary}</div>
            </div>
          )}
        </>
      )}

      <div className="detail-section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
          <h2 style={{ margin: 0, border: 'none', padding: 0 }}>Findings ({findings.length})</h2>
          {canEdit && (
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button className="btn btn-primary btn-small" onClick={openKBModal}>
                + From KB
              </button>
              <button className="btn btn-secondary btn-small" onClick={() => openFindingForm(null)}>
                + Custom
              </button>
            </div>
          )}
        </div>

        {findings.length === 0 ? (
          <div className="empty-state">
            <p>No findings yet.</p>
          </div>
        ) : (
          findings.map((finding, index) => (
            <div key={finding.id} className="finding-item">
              <div className="finding-header">
                <div className="finding-title">
                  <span className={`severity-badge severity-${finding.severity}`}>
                    {finding.severity}
                  </span>
                  {finding.title}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  {canEdit && (
                    <div className="finding-order-btns">
                      <button
                        className="btn btn-icon btn-small"
                        onClick={() => moveFinding(index, -1)}
                        disabled={index === 0}
                        title="Move up"
                      >
                        &#9650;
                      </button>
                      <button
                        className="btn btn-icon btn-small"
                        onClick={() => moveFinding(index, 1)}
                        disabled={index === findings.length - 1}
                        title="Move down"
                      >
                        &#9660;
                      </button>
                    </div>
                  )}
                  <div className="finding-actions">
                    {canEdit && (
                      <>
                        <button className="btn btn-icon" onClick={() => openFindingForm(finding)} title="Edit">
                          &#9998;
                        </button>
                        <button className="btn btn-icon" onClick={() => handleDeleteFinding(finding.id)} title="Delete" style={{ color: 'var(--danger)' }}>
                          &#10005;
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
              {finding.description && (
                <div className="finding-body">{finding.description}</div>
              )}
            </div>
          ))
        )}
      </div>

      {showKBModal && (
        <div className="modal-overlay" onClick={() => setShowKBModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Add Finding from Knowledge Base</h2>
            <input
              type="text"
              className="form-control"
              placeholder="Search KB entries..."
              value={kbSearch}
              onChange={(e) => setKBSearch(e.target.value)}
              style={{ marginBottom: '1rem' }}
              autoFocus
            />
            {filteredKB.length === 0 ? (
              <p style={{ color: 'var(--text-muted)' }}>No KB entries found.</p>
            ) : (
              <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                {filteredKB.map((entry) => (
                  <div
                    key={entry.id}
                    className="finding-item"
                    style={{ cursor: 'pointer' }}
                    onClick={() => addFromKB(entry)}
                  >
                    <div className="finding-header">
                      <div className="finding-title">
                        <span className={`severity-badge severity-${entry.severity || 'medium'}`}>
                          {entry.severity || 'medium'}
                        </span>
                        {entry.name || entry.title}
                      </div>
                    </div>
                    {entry.category && (
                      <div className="finding-body">{entry.category}</div>
                    )}
                  </div>
                ))}
              </div>
            )}
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => setShowKBModal(false)}>Cancel</button>
            </div>
          </div>
        </div>
      )}

      {showFindingForm && (
        <div className="modal-overlay" onClick={() => setShowFindingForm(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>{editingFinding ? 'Edit Finding' : 'New Finding'}</h2>
            <div className="form-group">
              <label>Title *</label>
              <input
                type="text"
                className="form-control"
                value={findingForm.title}
                onChange={(e) => setFindingForm({ ...findingForm, title: e.target.value })}
                required
                autoFocus
              />
            </div>
            <div className="form-group">
              <label>Severity</label>
              <select
                className="form-control"
                value={findingForm.severity}
                onChange={(e) => setFindingForm({ ...findingForm, severity: e.target.value })}
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
                value={findingForm.description}
                onChange={(e) => setFindingForm({ ...findingForm, description: e.target.value })}
                rows={4}
              />
            </div>
            <div className="form-group">
              <label>Recommendation</label>
              <textarea
                className="form-control"
                value={findingForm.recommendation}
                onChange={(e) => setFindingForm({ ...findingForm, recommendation: e.target.value })}
                rows={3}
              />
            </div>
            <div className="form-group">
              <label>References</label>
              <textarea
                className="form-control"
                value={findingForm.references}
                onChange={(e) => setFindingForm({ ...findingForm, references: e.target.value })}
                rows={2}
                placeholder="One URL per line"
              />
            </div>
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => setShowFindingForm(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleSaveFinding}>
                {editingFinding ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ReportDetailPage;
