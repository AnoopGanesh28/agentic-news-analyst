import React from 'react';
import { useSSE } from './hooks/useSSE';
import RunHistory from './components/RunHistory';
import TopicInput from './components/TopicInput';
import AgentTimeline from './components/AgentTimeline';
import ReportPanel from './components/ReportPanel';

function App() {
  const { events, isStreaming, report, error, startStream } = useSSE();

  return (
    <div className="app-container">
      <RunHistory />
      
      <div className="main-content">
        <div className="top-bar">
          <TopicInput onStart={startStream} isStreaming={isStreaming} />
          {error && (
            <div style={{ color: 'var(--danger)', padding: '12px', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
              Error: {error}
            </div>
          )}
        </div>
        
        <div className="content-area">
          <AgentTimeline events={events} isStreaming={isStreaming} />
          <ReportPanel report={report} isStreaming={isStreaming} />
        </div>
      </div>
    </div>
  );
}

export default App;
