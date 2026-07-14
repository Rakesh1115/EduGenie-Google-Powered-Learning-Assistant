import { postQA, postExplain, postQuiz, postSummarize, postRoadmap, formatError, downloadText } from './api.js';

const playground = document.getElementById('playground');
const toastRoot = document.getElementById('toast-root');
let lastResultText = '';
let currentView = 'dashboard';

function showToast(msg, type = 'info') {
  if (!toastRoot) return;
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  t.textContent = msg;
  toastRoot.appendChild(t);
  t.addEventListener('animationend', () => t.remove(), { once: true });
}

function setActiveNav(view) {
  currentView = view;
  document.querySelectorAll('.nav-item').forEach(b => b.classList.toggle('active', b.dataset.view === view));
}

function clearPlayground() { playground.innerHTML = ''; }

function createLoadingIndicator() {
  const spinner = document.createElement('div');
  spinner.className = 'loading-indicator';
  spinner.textContent = 'Working on it...';
  return spinner;
}

function setFormLoading(form, loading) {
  if (!form) return;
  const submit = form.querySelector('button[type="submit"]');
  if (submit) {
    submit.disabled = loading;
    submit.textContent = loading ? 'Generating…' : 'Generate';
  }
  const existing = form.querySelector('.loading-indicator');
  if (loading) {
    if (!existing) form.appendChild(createLoadingIndicator());
  } else {
    existing?.remove();
  }
}

function autoScrollTo(element) {
  element?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderTimeline(markdown) {
  const items = [];
  const sections = markdown.split(/\n(?=#)/);
  sections.forEach(section => {
    const titleMatch = section.match(/^#+\s*(.+)/m);
    if (!titleMatch) return;
    const title = titleMatch[1].trim();
    const body = section.replace(/^#+\s*.+/m, '').trim();
    const entries = Array.from(body.matchAll(/^\s*[-*+]\s*(.+)$/gm), m => m[1].trim());
    items.push({ title, body: body.replace(/^\s*[-*+]\s*.+$/gm, '').trim(), entries });
  });
  if (!items.length) return null;
  const timeline = document.createElement('div');
  timeline.className = 'timeline';
  items.forEach(item => {
    const entry = document.createElement('div');
    entry.className = 'timeline-item';
    const heading = document.createElement('h4');
    heading.textContent = item.title;
    entry.appendChild(heading);
    if (item.body) {
      const description = document.createElement('p');
      description.textContent = item.body;
      entry.appendChild(description);
    }
    if (item.entries.length) {
      const list = document.createElement('ul');
      item.entries.forEach(text => { const li = document.createElement('li'); li.textContent = text; list.appendChild(li); });
      entry.appendChild(list);
    }
    timeline.appendChild(entry);
  });
  return timeline;
}

function renderResult(title, markdown, meta) {
  lastResultText = markdown || '';
  const wrapper = document.createElement('div');
  wrapper.className = 'result-wrapper';
  const h = document.createElement('h3'); h.textContent = title;
  const md = document.createElement('div'); md.className = 'result';
  md.innerHTML = markdownToHtml(markdown || '');
  wrapper.appendChild(h);
  wrapper.appendChild(md);

  if (currentView === 'roadmap') {
    const timeline = renderTimeline(markdown || '');
    if (timeline) wrapper.appendChild(timeline);
  }

  if (meta && meta.items) {
    const quiz = document.createElement('div'); quiz.className = 'quiz';
    meta.items.forEach((it, i) => {
      const q = document.createElement('div'); q.className = 'q';
    const qtext = document.createElement('div');
    const qstrong = document.createElement('strong');
    qstrong.textContent = it.question;
    qtext.appendChild(qstrong);
      q.appendChild(qtext);
      it.choices.forEach(c => {
        const ch = document.createElement('div'); ch.className = 'choice'; ch.textContent = c;
        ch.addEventListener('click', () => {
          if (it.answer && c.startsWith(it.answer)) showToast('Correct', 'success'); else showToast('Try again', 'error');
        });
        q.appendChild(ch);
      });
      quiz.appendChild(q);
    });
    wrapper.appendChild(quiz);
  }

  clearPlayground();
  playground.appendChild(wrapper);
  autoScrollTo(wrapper);
}

function markdownToHtml(md) {
  if (!md) return '';
  // basic conversions
  let out = md
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  // code blocks
  out = out.replace(/```([\s\S]*?)```/g, (m, code) => `<pre><code>${code}</code></pre>`);
  // headings
  out = out.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  out = out.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  out = out.replace(/^# (.*$)/gim, '<h1>$1</h1>');
  // bold/italic
  out = out.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');
  out = out.replace(/\*(.*?)\*/gim, '<em>$1</em>');
  // lists
  out = out.replace(/^\s*[-\*] (.*$)/gim, '<li>$1</li>');
  out = out.replace(/(<li>.*<\/li>)/gim, '<ul>$1</ul>');
  // paragraphs
  out = out.replace(/^(?!<h|<ul|<pre|<p|<blockquote)([^\n]+)\n?/gim, '<p>$1</p>');
  return out;
}

async function handleSubmit(view, values, form) {
  setFormLoading(form, true);
  try {
    let res;
    if (view === 'qa') res = await postQA(values);
    if (view === 'explain') res = await postExplain(values);
    if (view === 'quiz') res = await postQuiz(values);
    if (view === 'summarize') res = await postSummarize(values);
    if (view === 'roadmap') res = await postRoadmap(values);

    if (!res || !res.ok) {
      const msg = res && (res.error || res.text) ? (res.error || res.text) : 'Request failed';
      showToast(msg, 'error');
      return;
    }

    const payload = res.data || {};
    renderResult('Result', payload.markdown || payload.text || res.text || '', payload.meta || null);
    showToast('Generated successfully', 'success');
  } catch (e) {
    showToast(formatError(e), 'error');
  } finally {
    setFormLoading(form, false);
  }
}

function validate(view, fields) {
  const optionalFields = {
    qa: ['context'],
    explain: [],
    quiz: ['difficulty'],
    summarize: ['max_length'],
    roadmap: ['goals', 'duration_weeks'],
  };

  const missing = [];
  for (const key in fields) {
    const value = fields[key];
    const isOptional = optionalFields[view]?.includes(key);
    if ((value === '' || value === null || value === undefined) && !isOptional) {
      missing.push(key);
    }
  }

  if (view === 'quiz' && fields.num_questions) {
    if (Number(fields.num_questions) < 1 || Number(fields.num_questions) > 50) {
      missing.push('num_questions (must be 1-50)');
    }
  }
  if (view === 'roadmap' && fields.duration_weeks) {
    if (Number(fields.duration_weeks) < 1 || Number(fields.duration_weeks) > 52) {
      missing.push('duration_weeks (must be 1-52)');
    }
  }
  if (view === 'summarize' && fields.max_length) {
    if (Number(fields.max_length) < 50 || Number(fields.max_length) > 1000) {
      missing.push('max_length (must be 50-1000)');
    }
  }
  return missing;
}

// create forms for views
function renderForm(view) {
  const form = document.createElement('form');
  form.className = 'view-form';
  const field = (labelText, name, placeholder='') => {
    const d = document.createElement('div'); d.className = 'field';
    const l = document.createElement('label'); l.textContent = labelText; d.appendChild(l);
    const inp = document.createElement('input'); inp.name = name; inp.placeholder = placeholder; inp.className='input'; d.appendChild(inp);
    return d;
  };

  if (view === 'dashboard') {
    const p = document.createElement('p'); p.className='muted'; p.textContent = 'Choose a feature from the sidebar or open a card.'; form.appendChild(p);
  }

  if (view === 'qa') {
    form.appendChild(field('Question', 'question', 'What do you want to know?'));
    form.appendChild(field('Context (optional)', 'context', 'Optional context to improve the answer'));
  }
  if (view === 'explain') {
    form.appendChild(field('Topic', 'topic', 'Topic or concept'));
    form.appendChild(field('Level', 'level', 'beginner|intermediate|advanced'));
  }
  if (view === 'quiz') {
    form.appendChild(field('Topic', 'topic', 'Topic for quiz'));
    const num = field('Number of questions', 'num_questions', '3');
    num.querySelector('input').type = 'number';
    num.querySelector('input').min = '1';
    num.querySelector('input').max = '50';
    form.appendChild(num);
    form.appendChild(field('Difficulty (optional)', 'difficulty', 'easy|medium|hard'));
  }
  if (view === 'summarize') {
    const d = document.createElement('div'); d.className='field'; const l = document.createElement('label'); l.textContent='Text'; d.appendChild(l);
    const ta = document.createElement('textarea'); ta.name='text'; ta.rows=6; ta.placeholder='Paste text to summarize'; ta.className='input'; d.appendChild(ta); form.appendChild(d);
    const maxLen = field('Max summary length', 'max_length', '200');
    maxLen.querySelector('input').type = 'number';
    maxLen.querySelector('input').min = '50';
    maxLen.querySelector('input').max = '1000';
    form.appendChild(maxLen);
  }
  if (view === 'roadmap') {
    form.appendChild(field('Subject', 'subject', 'What to learn'));
    form.appendChild(field('Goals (optional)', 'goals', 'Your goals for this roadmap'));
    const weeks = field('Duration in weeks', 'duration_weeks', '8');
    weeks.querySelector('input').type = 'number';
    weeks.querySelector('input').min = '1';
    weeks.querySelector('input').max = '52';
    form.appendChild(weeks);
  }

  const submit = document.createElement('button'); submit.type='submit'; submit.className='button button-primary'; submit.textContent='Generate'; form.appendChild(submit);

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    if (data.num_questions) data.num_questions = Number(data.num_questions);
    if (data.duration_weeks) data.duration_weeks = Number(data.duration_weeks);
    if (data.max_length) data.max_length = Number(data.max_length);
    const miss = validate(view, data);
    if (miss.length) { showToast('Check fields: ' + miss.join(', '), 'error'); return; }
    handleSubmit(view, data, form);
  });

  clearPlayground();
  playground.appendChild(form);
  // focus the first form control for accessibility and keyboard users
  const firstControl = form.querySelector('input, textarea, select, button');
  if (firstControl) firstControl.focus();
}

// event wiring
function wireEvents() {
  document.addEventListener('click', (e) => {
    // Try direct elements with data-view first
    const direct = e.target.closest('[data-view]');
    let view = null;
    if (direct) {
      view = direct.dataset.view;
      // prevent anchors from navigating
      if (direct.tagName === 'A') e.preventDefault();
    } else {
      // allow clicking the whole card to open the feature (look for a child data-view)
      const card = e.target.closest('.card, .feature-card, article');
      if (card) {
        const child = card.querySelector('[data-view]');
        if (child) view = child.dataset.view;
      }
    }

    if (view) {
      setActiveNav(view);
      renderForm(view);
    }
  });

  const copyBtn = document.getElementById('copy-btn');
  const downloadBtn = document.getElementById('download-btn');
  const themeToggle = document.getElementById('theme-toggle');
  const navToggle = document.getElementById('nav-toggle');
  const siteNav = document.getElementById('site-nav');

  copyBtn?.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(lastResultText); showToast('Copied to clipboard', 'success'); } catch { showToast('Copy failed', 'error'); }
  });
  downloadBtn?.addEventListener('click', () => {
    if (!lastResultText) { showToast('Generate a result before downloading', 'error'); return; }
    downloadText('edugenie-result.md', lastResultText);
    showToast('Download started', 'success');
  });
  themeToggle?.addEventListener('click', () => { document.documentElement.classList.toggle('light'); showToast('Theme changed', 'info'); });
  navToggle?.setAttribute('aria-expanded', 'false');
  navToggle?.addEventListener('click', () => {
    const isOpen = siteNav?.classList.toggle('is-open');
    navToggle?.setAttribute('aria-expanded', !!isOpen);
  });
}

function init() {
  if (!playground) return;
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.body.classList.add('reduced-motion');
  }
  wireEvents();
  renderForm('dashboard');
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
