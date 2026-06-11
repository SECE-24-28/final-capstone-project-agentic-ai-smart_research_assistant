/**
 * streamApi.js
 * 
 * Streaming service layer using Fetch ReadableStream + Server-Sent Events (SSE).
 * Each function returns an AbortController so the caller can cancel the stream.
 */

const BASE_URL = 'http://localhost:8000';

/**
 * Core stream consumer.
 * Sends a POST request, reads the SSE text/event-stream, and calls:
 *   onToken(tokenText)      – called for each streamed token
 *   onDone()                – called when the stream ends cleanly
 *   onError(errorMessage)   – called on error event or fetch failure
 * 
 * Returns an AbortController so the caller can call .abort() to stop.
 */
function createStream(endpoint, body, { onToken, onDone, onError }) {
  const controller = new AbortController();

  (async () => {
    try {
      const response = await fetch(`${BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: controller.signal,
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({ detail: response.statusText }));
        onError(err.detail || 'Backend error');
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Process complete SSE lines from the buffer
        const lines = buffer.split('\n');
        buffer = lines.pop(); // keep the last incomplete line

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              onDone();
              return;
            }
            // Restore escaped newlines back to real newlines
            const token = data.replace(/\\n/g, '\n');
            onToken(token);
          } else if (line.startsWith('event: error')) {
            // Next line will be "data: <error message>"
          } else if (line.startsWith('data: ') && buffer.includes('event: error')) {
            onError(line.slice(6));
            return;
          }
        }
      }
      onDone();
    } catch (err) {
      if (err.name === 'AbortError') {
        onDone(); // Treat abort as a clean finish
      } else {
        onError(err.message || 'Stream connection failed');
      }
    }
  })();

  return controller;
}

// ─── Agent-specific streaming helpers ────────────────────────────────────────

export function streamChat(question, paperIds, callbacks) {
  return createStream('/agent/chat/stream', {
    question,
    paper_ids: paperIds && paperIds.length > 0 ? paperIds : null,
    session_id: null,
  }, callbacks);
}

export function streamSummary(paperId, callbacks) {
  return createStream(`/agent/summary/stream?paper_id=${paperId}`, {}, callbacks);
}

export function streamComparison(paperIds, callbacks) {
  return createStream('/agent/compare/stream', { paper_ids: paperIds }, callbacks);
}

export function streamGap(paperIds, topic, callbacks) {
  return createStream('/agent/gap/stream', { topic, paper_ids: paperIds }, callbacks);
}

export function streamReview(paperIds, topic, callbacks) {
  return createStream('/agent/review/stream', { topic, paper_ids: paperIds }, callbacks);
}
