import React from 'react';
import ReactMarkdown from 'react-markdown';

export default function ReportPanel({ report, isStreaming }) {
  if (isStreaming && !report) {
    return (
      <div className="glass-panel report-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          <h3 style={{ fontWeight: '500' }}>Processing Analysis</h3>
          <p style={{ marginTop: '8px', opacity: 0.7 }}>This may take 30-60 seconds depending on the research depth.</p>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="glass-panel report-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          <h3 style={{ fontWeight: '500' }}>Ready for Investigation</h3>
          <p style={{ marginTop: '8px', opacity: 0.7 }}>Enter a topic on the left to begin.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-panel report-container">
      <div className="markdown-body animate-fade-in">
        <ReactMarkdown>{report}</ReactMarkdown>
      </div>
    </div>
  );
}
