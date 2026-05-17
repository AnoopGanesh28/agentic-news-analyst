import { useState, useCallback, useRef } from 'react';

export function useSSE() {
  const [events, setEvents] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);
  const eventSourceRef = useRef(null);

  const startStream = useCallback(async (topic) => {
    // Reset state
    setEvents([]);
    setReport(null);
    setError(null);
    setIsStreaming(true);

    try {
      // 1. Start the run
      const res = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic }),
      });

      if (!res.ok) throw new Error('Failed to start analysis');
      const { run_id } = await res.json();

      // 2. Connect to SSE
      eventSourceRef.current = new EventSource(`http://localhost:8000/api/analyze/${run_id}/stream`);

      eventSourceRef.current.onmessage = async (e) => {
        const data = JSON.parse(e.data);
        
        if (data.event === 'done') {
          eventSourceRef.current.close();
          setIsStreaming(false);
          // 3. Fetch final report
          try {
            const reportRes = await fetch(`http://localhost:8000/api/analyze/${run_id}/report`);
            if (reportRes.ok) {
              const reportData = await reportRes.json();
              setReport(reportData.report);
            }
          } catch (err) {
            console.error("Failed to fetch final report", err);
          }
        } else {
          // Append new event
          setEvents((prev) => [...prev, data]);
        }
      };

      eventSourceRef.current.onerror = (err) => {
        console.error("SSE Error:", err);
        eventSourceRef.current.close();
        setIsStreaming(false);
        setError("Connection to server lost.");
      };

    } catch (err) {
      console.error(err);
      setError(err.message);
      setIsStreaming(false);
    }
  }, []);

  const stopStream = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    setIsStreaming(false);
  }, []);

  return { events, isStreaming, report, error, startStream, stopStream };
}
