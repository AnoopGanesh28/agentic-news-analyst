import { useState } from 'react';

export default function TopicInput({ onStart, isStreaming }) {
  const [topic, setTopic] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (topic.trim() && !isStreaming) {
      onStart(topic);
      setTopic('');
    }
  };

  return (
    <div className="glass" style={{ padding: '24px', marginBottom: '24px' }}>
      <h2 style={{ marginBottom: '16px', fontSize: '1.2rem', fontWeight: '500' }}>
        What would you like to investigate?
      </h2>
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '16px' }}>
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="e.g. AI Regulation in the EU"
          disabled={isStreaming}
        />
        <button 
          type="submit" 
          className="btn-primary"
          disabled={isStreaming || !topic.trim()}
          style={{ whiteSpace: 'nowrap' }}
        >
          {isStreaming ? (
            <span className="dots">Analyzing<span>.</span><span>.</span><span>.</span></span>
          ) : 'Run Analysis'}
        </button>
      </form>
    </div>
  );
}
