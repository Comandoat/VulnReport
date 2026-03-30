import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createReport } from '../services/api';

function ReportCreatePage() {
  const [title, setTitle] = useState('');
  const [context, setContext] = useState('');
  const [executiveSummary, setExecutiveSummary] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!title.trim()) {
      setError('Title is required.');
      return;
    }

    setLoading(true);
    try {
      const res = await createReport({
        title: title.trim(),
        context: context.trim(),
        executive_summary: executiveSummary.trim(),
      });
      const newId = res.data.id;
      navigate(`/reports/${newId}`);
    } catch (err) {
      if (err.response && err.response.data) {
        const data = err.response.data;
        const messages = Object.values(data).flat().join(' ');
        setError(messages || 'Failed to create report.');
      } else {
        setError('Network error. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>New Report</h1>
      </div>

      <div className="card" style={{ maxWidth: '700px' }}>
        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="title">Title *</label>
            <input
              id="title"
              type="text"
              className="form-control"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Web Application Penetration Test - ACME Corp"
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="context">Context</label>
            <textarea
              id="context"
              className="form-control"
              value={context}
              onChange={(e) => setContext(e.target.value)}
              placeholder="Describe the scope and context of this pentest..."
              rows={4}
            />
          </div>

          <div className="form-group">
            <label htmlFor="executive_summary">Executive Summary</label>
            <textarea
              id="executive_summary"
              className="form-control"
              value={executiveSummary}
              onChange={(e) => setExecutiveSummary(e.target.value)}
              placeholder="High-level summary of findings and recommendations..."
              rows={6}
            />
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create Report'}
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => navigate('/reports')}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ReportCreatePage;
