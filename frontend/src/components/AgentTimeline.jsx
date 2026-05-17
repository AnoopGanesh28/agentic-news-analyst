import React from 'react';

// Defines the order and display names of our nodes
const NODES = [
  { id: 'planner', label: 'Planner (Structuring Queries)' },
  { id: 'researcher', label: 'Researcher (Fetching APIs)' },
  { id: 'post_researcher', label: 'Data Processing (Deduplicating)' },
  { id: 'fact_checker', label: 'Fact Checker (Cross-referencing)' },
  { id: 'bias_analyst', label: 'Bias Analyst (Scoring Sentiment)' },
  { id: 'critic', label: 'Critic (Evaluating Completeness)' },
  { id: 'writer', label: 'Writer (Generating Final Report)' }
];

export default function AgentTimeline({ events, isStreaming }) {
  // Determine which node is currently active based on the last event
  const lastEvent = events[events.length - 1];
  let activeNodeId = null;
  let completedNodes = new Set();
  let iterationCount = 0;

  if (lastEvent) {
    const nodeKeys = Object.keys(lastEvent);
    if (nodeKeys.length > 0) {
      activeNodeId = nodeKeys[0];
    }
    
    // Calculate iteration based on critic feedback
    events.forEach(e => {
      if (e.critic && e.critic.iteration) {
        iterationCount = e.critic.iteration;
      }
    });
  }

  // Determine completed vs active
  let passedActive = false;
  const processedNodes = NODES.map(node => {
    let isActive = false;
    let isCompleted = false;

    if (node.id === activeNodeId) {
      isActive = true;
      passedActive = true;
    } else if (!passedActive && events.length > 0) {
      // Very naive logic: if it's before the active node in the list, it's completed
      // Exception: If the graph looped back, we just show the current state visually
      isCompleted = true;
    }

    // Special logic for when streaming is fully done
    if (!isStreaming && events.length > 0) {
      isCompleted = true;
      isActive = false;
    }

    return { ...node, isActive, isCompleted };
  });

  return (
    <div className="glass-panel" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '24px', borderBottom: '1px solid var(--border-color)' }}>
        <h3 style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Agent Timeline</span>
          {iterationCount > 0 && (
            <span style={{ fontSize: '0.8rem', background: 'var(--accent)', padding: '2px 8px', borderRadius: '12px', color: '#000' }}>
              Loop: {iterationCount}
            </span>
          )}
        </h3>
      </div>
      
      <div className="timeline-container" style={{ padding: '24px', flex: 1 }}>
        {processedNodes.map((node) => {
          let className = "timeline-node";
          if (node.isActive) className += " active";
          if (node.isCompleted) className += " completed";

          return (
            <div key={node.id} className={className}>
              <div style={{ fontWeight: node.isActive ? '600' : '400', color: node.isActive ? 'var(--text-main)' : 'var(--text-muted)' }}>
                {node.label}
              </div>
              
              {/* Display some dynamic metadata if it's the active node */}
              {node.isActive && lastEvent && lastEvent[node.id] && (
                <div className="animate-fade-in" style={{ marginTop: '8px', fontSize: '0.85rem', color: 'var(--primary)' }}>
                  {node.id === 'planner' && `Generated ${lastEvent.planner.sub_questions?.length || 0} questions`}
                  {node.id === 'researcher' && `Fetched ${lastEvent.researcher.raw_articles?.length || 0} articles`}
                  {node.id === 'fact_checker' && `Found ${lastEvent.fact_checker.claims?.length || 0} claims`}
                  {node.id === 'critic' && `Decision: ${lastEvent.critic.critic_feedback?.toUpperCase()}`}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
