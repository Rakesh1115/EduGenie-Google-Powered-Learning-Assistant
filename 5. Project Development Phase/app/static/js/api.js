const apiBaseUrl = window.location.origin;
const REQUEST_TIMEOUT_MS = 15000;

async function postJSON(path, payload) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const res = await fetch(`${apiBaseUrl}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
    const text = await res.text();
    let data = null;
    try { data = JSON.parse(text); } catch {}
    const error = data && data.detail ? (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)) : null;
    return { ok: res.ok, data, text, error };
  } catch (error) {
    const message = error.name === 'AbortError' ? 'Request timed out' : error.message;
    return { ok: false, data: null, text: message, error: message };
  } finally {
    clearTimeout(timeout);
  }
}

export async function fetchHealth() {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const response = await fetch(`${apiBaseUrl}/health`, { signal: controller.signal });
    if (!response.ok) throw new Error('Health check failed');
    return response.json();
  } catch (error) {
    throw new Error(error.name === 'AbortError' ? 'Health check timed out' : error.message);
  } finally {
    clearTimeout(timeout);
  }
}

export async function postQA(payload) { return postJSON('/qa/', payload); }
export async function postExplain(payload) { return postJSON('/explain/', payload); }
export async function postQuiz(payload) { return postJSON('/quiz/', payload); }
export async function postSummarize(payload) { return postJSON('/summarize/', payload); }
export async function postRoadmap(payload) { return postJSON('/roadmap/', payload); }

export function formatError(error) { return error instanceof Error ? error.message : 'An unexpected error occurred.'; }

// small helpers
export function downloadText(filename, text) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([text], { type: 'text/plain' }));
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
}
