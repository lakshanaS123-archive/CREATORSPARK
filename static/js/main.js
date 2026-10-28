/**
 * CreatorSpark — Main Client JavaScript
 * Handles navigation toggling, alert dismissal, live landing preview,
 * clipboard copy helpers, studio tabs/character counters,
 * and comprehensive Web Speech API audio playback controls.
 */

document.addEventListener('DOMContentLoaded', () => {
  initMobileNavigation();
  initAlertDismissal();
  initLiveIdeaPreview();
  initClipboardHelpers();
  initStudioTabsAndCounter();
  initAudioPlayerSystem();
});

/* --------------------------------------------------------------------------
   1. Mobile Navigation Drawer Toggle
   -------------------------------------------------------------------------- */
function initMobileNavigation() {
  const toggleBtn = document.getElementById('navToggleBtn');
  const navMenu = document.getElementById('navMenu');

  if (!toggleBtn || !navMenu) return;

  toggleBtn.addEventListener('click', () => {
    const isExpanded = toggleBtn.getAttribute('aria-expanded') === 'true';
    toggleBtn.setAttribute('aria-expanded', !isExpanded);
    navMenu.classList.toggle('open');
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && navMenu.classList.contains('open')) {
      navMenu.classList.remove('open');
      toggleBtn.setAttribute('aria-expanded', 'false');
    }
  });
}

/* --------------------------------------------------------------------------
   2. Alert Message Dismissal
   -------------------------------------------------------------------------- */
function initAlertDismissal() {
  const closeButtons = document.querySelectorAll('.alert-close');
  closeButtons.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const alert = e.target.closest('.alert');
      if (alert) {
        alert.style.transition = 'opacity 200ms ease, transform 200ms ease';
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-6px)';
        setTimeout(() => alert.remove(), 200);
      }
    });
  });
}

/* --------------------------------------------------------------------------
   3. Interactive Live Idea Generator Preview (Landing Page)
   -------------------------------------------------------------------------- */
function initLiveIdeaPreview() {
  const nicheSelect = document.getElementById('previewNicheSelect');
  const formatSelect = document.getElementById('previewFormatSelect');
  const generateBtn = document.getElementById('previewGenerateBtn');

  if (!nicheSelect || !formatSelect || !generateBtn) return;

  const updatePreview = async () => {
    const niche = nicheSelect.value;
    const format = formatSelect.value;

    generateBtn.disabled = true;
    generateBtn.textContent = 'Generating...';

    try {
      const response = await fetch(`/api/sample-idea/?niche=${encodeURIComponent(niche)}&format=${encodeURIComponent(format)}`);
      if (!response.ok) throw new Error('Preview fetch failed');
      const data = await response.json();
      renderIdeaPreview(data.idea, niche, format);
    } catch (err) {
      console.warn('Fallback to local rule preview:', err);
    } finally {
      generateBtn.disabled = false;
      generateBtn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
        </svg>
        Generate Sample
      `;
    }
  };

  generateBtn.addEventListener('click', updatePreview);
  nicheSelect.addEventListener('change', updatePreview);
  formatSelect.addEventListener('change', updatePreview);
}

function renderIdeaPreview(idea, niche, format) {
  if (!idea) return;

  const titleEl = document.getElementById('previewIdeaTitle');
  if (titleEl) titleEl.textContent = idea.title;

  const hookEl = document.getElementById('previewIdeaHook');
  if (hookEl) hookEl.textContent = idea.hook;

  const diffEl = document.getElementById('previewIdeaDifficulty');
  if (diffEl && idea.difficulty) diffEl.textContent = idea.difficulty;

  const formatBadgeEl = document.getElementById('previewIdeaFormatBadge');
  if (formatBadgeEl) formatBadgeEl.textContent = format.toUpperCase();

  const outlineList = document.getElementById('previewIdeaOutline');
  if (outlineList && Array.isArray(idea.outline)) {
    outlineList.innerHTML = '';
    idea.outline.forEach((stepText, idx) => {
      const li = document.createElement('li');
      li.className = 'outline-step-item';
      li.innerHTML = `
        <span class="step-num">${idx + 1}</span>
        <span>${escapeHtml(stepText)}</span>
      `;
      outlineList.appendChild(li);
    });
  }

  const captionEl = document.getElementById('previewIdeaCaption');
  if (captionEl) captionEl.textContent = idea.caption;

  const hashtagCloud = document.getElementById('previewIdeaHashtags');
  if (hashtagCloud && Array.isArray(idea.hashtags)) {
    hashtagCloud.innerHTML = '';
    idea.hashtags.forEach((tag) => {
      const span = document.createElement('span');
      span.className = 'hashtag-pill';
      span.textContent = tag;
      hashtagCloud.appendChild(span);
    });
  }
}

/* --------------------------------------------------------------------------
   4. Clipboard Copy Helpers
   -------------------------------------------------------------------------- */
function initClipboardHelpers() {
  // Generic copy buttons targeting an ID
  const copyButtons = document.querySelectorAll('.copy-btn');
  copyButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-copy-target');
      const targetEl = document.getElementById(targetId);
      if (!targetEl) return;

      const textToCopy = targetEl.value !== undefined ? targetEl.value : targetEl.innerText;
      copyTextToClipboard(textToCopy, btn);
    });
  });

  // Studio: Copy Caption + Hashtags Together
  const copyAllBtn = document.getElementById('copyAllStudioBtn');
  if (copyAllBtn) {
    copyAllBtn.addEventListener('click', () => {
      const captionEl = document.getElementById('studioCaptionEditor');
      const hashtagsEl = document.getElementById('studioHashtagsRaw');
      const caption = captionEl ? captionEl.value : '';
      const hashtags = hashtagsEl ? hashtagsEl.value : '';

      const combined = `${caption}\n\n---\n${hashtags}`;
      copyTextToClipboard(combined, copyAllBtn);
    });
  }
}

function copyTextToClipboard(text, triggerBtn) {
  if (!text) return;

  const origText = triggerBtn.innerHTML;

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(() => {
      showCopiedFeedback(triggerBtn, origText);
    }).catch(() => fallbackCopy(text, triggerBtn, origText));
  } else {
    fallbackCopy(text, triggerBtn, origText);
  }
}

function fallbackCopy(text, triggerBtn, origText) {
  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.style.position = 'fixed';
  textarea.style.opacity = '0';
  document.body.appendChild(textarea);
  textarea.select();
  try {
    document.execCommand('copy');
    showCopiedFeedback(triggerBtn, origText);
  } catch (e) {
    console.error('Copy fallback failed', e);
  }
  document.body.removeChild(textarea);
}

function showCopiedFeedback(btn, originalHtml) {
  btn.innerHTML = '✓ Copied!';
  btn.classList.add('btn-success');
  setTimeout(() => {
    btn.innerHTML = originalHtml;
    btn.classList.remove('btn-success');
  }, 1800);
}

/* --------------------------------------------------------------------------
   5. Caption Studio Tabs & Live Character Counter
   -------------------------------------------------------------------------- */
function initStudioTabsAndCounter() {
  const editor = document.getElementById('studioCaptionEditor');
  const counter = document.getElementById('charCountDisplay');
  const hiddenSave = document.getElementById('hiddenSaveCaption');
  const tabButtons = document.querySelectorAll('.style-tab-btn');

  if (editor && counter) {
    const updateCounter = () => {
      const len = editor.value.length;
      counter.textContent = len;
      if (hiddenSave) hiddenSave.value = editor.value;
    };

    editor.addEventListener('input', updateCounter);
    updateCounter(); // Initial count
  }

  // Switch between Storytelling, Listicle, and Conversational tabs
  tabButtons.forEach((tab) => {
    tab.addEventListener('click', () => {
      tabButtons.forEach((t) => t.classList.remove('active'));
      tab.classList.add('active');

      const targetId = tab.getAttribute('data-style-target');
      const sourceEl = document.getElementById(targetId);
      if (sourceEl && editor) {
        editor.value = sourceEl.value;
        if (counter) counter.textContent = editor.value.length;
        if (hiddenSave) hiddenSave.value = editor.value;
      }
    });
  });
}

/* --------------------------------------------------------------------------
   6. Comprehensive Web Speech API Audio Player System
   -------------------------------------------------------------------------- */
let globalSynth = null;
let currentUtterance = null;
let currentActivePlayButton = null;

function initAudioPlayerSystem() {
  if (!('speechSynthesis' in window)) {
    const audioBar = document.getElementById('audioGlobalBar');
    if (audioBar) {
      audioBar.innerHTML = `
        <div style="font-size: 0.8125rem; color: var(--color-slate-500); padding: 0.25rem;">
          ℹ️ <em>Browser audio playback (Web Speech API) is not supported in this browser version.</em>
        </div>
      `;
    }
    return;
  }

  globalSynth = window.speechSynthesis;

  const pauseBtn = document.getElementById('audioPauseBtn');
  const resumeBtn = document.getElementById('audioResumeBtn');
  const stopBtn = document.getElementById('audioStopBtn');
  const voiceSelect = document.getElementById('audioVoiceSelect');
  const statusLabel = document.getElementById('audioStatusText');
  const indicator = document.getElementById('audioPulseIndicator');

  // Populate voice selector when voices are loaded
  const populateVoices = () => {
    if (!voiceSelect) return;
    const voices = globalSynth.getVoices();
    if (!voices || voices.length === 0) return;

    voiceSelect.innerHTML = '<option value="">Default Voice</option>';
    voices.forEach((voice, index) => {
      // Prioritize English or high-quality voices
      const opt = document.createElement('option');
      opt.value = index;
      opt.textContent = `${voice.name} (${voice.lang})`;
      voiceSelect.appendChild(opt);
    });
  };

  populateVoices();
  if (globalSynth.onvoiceschanged !== undefined) {
    globalSynth.onvoiceschanged = populateVoices;
  }

  // Update Toolbar States
  const setAudioState = (state, label) => {
    if (statusLabel) statusLabel.textContent = label;

    if (state === 'speaking') {
      if (indicator) indicator.classList.add('active');
      if (pauseBtn) pauseBtn.disabled = false;
      if (resumeBtn) resumeBtn.disabled = true;
      if (stopBtn) stopBtn.disabled = false;
    } else if (state === 'paused') {
      if (indicator) indicator.classList.remove('active');
      if (pauseBtn) pauseBtn.disabled = true;
      if (resumeBtn) resumeBtn.disabled = false;
      if (stopBtn) stopBtn.disabled = false;
    } else { // stopped / idle
      if (indicator) indicator.classList.remove('active');
      if (pauseBtn) pauseBtn.disabled = true;
      if (resumeBtn) resumeBtn.disabled = true;
      if (stopBtn) stopBtn.disabled = true;
      if (currentActivePlayButton) {
        currentActivePlayButton.innerHTML = currentActivePlayButton.getAttribute('data-orig-text') || '🔊 Listen';
        currentActivePlayButton = null;
      }
    }
  };

  // Listen buttons across generator cards, idea details, and studio
  const playButtons = document.querySelectorAll('.audio-play-btn, #previewAudioBtn');
  playButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-speak-target') || 'previewIdeaHook';
      const targetEl = document.getElementById(targetId);
      if (!targetEl) return;

      const textToSpeak = targetEl.value !== undefined ? targetEl.value : targetEl.innerText;
      if (!textToSpeak.trim()) return;

      // Stop any active speech first (prevents overlapping speech)
      globalSynth.cancel();

      // Store original button text
      if (!btn.getAttribute('data-orig-text')) {
        btn.setAttribute('data-orig-text', btn.innerHTML);
      }

      currentActivePlayButton = btn;
      btn.innerHTML = '⏸ Speaking...';

      currentUtterance = new SpeechSynthesisUtterance(textToSpeak);
      currentUtterance.rate = 1.0;
      currentUtterance.pitch = 1.0;

      // Apply selected voice if any
      if (voiceSelect && voiceSelect.value !== '') {
        const voices = globalSynth.getVoices();
        const selectedVoice = voices[parseInt(voiceSelect.value, 10)];
        if (selectedVoice) currentUtterance.voice = selectedVoice;
      }

      currentUtterance.onstart = () => {
        setAudioState('speaking', 'Playing audio with Web Speech API...');
      };

      currentUtterance.onend = () => {
        setAudioState('idle', 'Audio finished. Player ready.');
      };

      currentUtterance.onerror = (e) => {
        console.warn('SpeechSynthesis error:', e);
        setAudioState('idle', 'Audio playback stopped.');
      };

      globalSynth.speak(currentUtterance);
    });
  });

  // Pause Button
  if (pauseBtn) {
    pauseBtn.addEventListener('click', () => {
      if (globalSynth.speaking && !globalSynth.paused) {
        globalSynth.pause();
        setAudioState('paused', 'Audio playback paused.');
      }
    });
  }

  // Resume Button
  if (resumeBtn) {
    resumeBtn.addEventListener('click', () => {
      if (globalSynth.paused) {
        globalSynth.resume();
        setAudioState('speaking', 'Resumed audio playback.');
      }
    });
  }

  // Stop Button
  if (stopBtn) {
    stopBtn.addEventListener('click', () => {
      globalSynth.cancel();
      setAudioState('idle', 'Audio playback stopped.');
    });
  }

  // Cancel speech immediately on page navigation
  window.addEventListener('beforeunload', () => {
    if (globalSynth) globalSynth.cancel();
  });
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
