import React, { useEffect, useState } from 'react';

export default function RunHistory() {
  const [runs, setRuns] = useState([]);

  useEffect(() => {
    // Fetch runs on mount
    fetch('http://localhost:8000/api/runs')
      .then(res => res.json())
      .then(data => {
        // Sort newest first
        const sorted = (data.runs || []).sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        setRuns(sorted);
      })
      .catch(err => console.error("Failed to fetch runs", err));
  }, []);

  return (
    <div className="sidebar">
      <div style={{ padding: '24px', borderBottom: '1px solid var(--border-color)' }}>
        <h2 style={{ fontSize: '1.2rem', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '8px', letterSpacing: '-0.5px' }}>
          Agentic Analyst
        </h2>
      </div>
      
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
        <h3 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '16px', paddingLeft: '8px' }}>
          Recent Investigations
        </h3>
        
        {runs.length === 0 ? (
          <p style={{ padding: '8px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>No past runs found.</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {runs.map(run => (
              <div 
                key={run.run_id} 
                className="glass" 
                style={{ 
                  padding: '12px 16px', 
                  cursor: 'pointer',
                  borderLeft: run.status === 'running' ? '3px solid var(--accent)' : '3px solid var(--secondary)'
                }}
                onClick={() => alert('Viewing past runs not fully implemented in UI yet. Please check the backend /report endpoint.')}
              >
                <div style={{ fontWeight: '500', fontSize: '0.95rem', marginBottom: '4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {run.topic}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between' }}>
                  <span>{new Date(run.created_at).toLocaleDateString()}</span>
                  <span style={{ color: run.status === 'running' ? 'var(--accent)' : 'var(--secondary)' }}>
                    {run.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      <div style={{ padding: '24px', borderTop: '1px solid var(--border-color)', fontSize: '0.8rem', color: 'var(--text-muted)', textAlign: 'center' }}>
        Powered by Groq & LangGraph
      </div>
    </div>
  );
}
