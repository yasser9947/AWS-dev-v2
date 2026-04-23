/* Shared JS for AWS DVA-C02 Course
 * - Language switcher (AR <-> EN) persisted in localStorage
 * - Chapter completion tracking in localStorage
 * - Quiz result persistence
 * - Code copy buttons
 */

const STORAGE_KEYS = {
  LANG: 'dva_lang',
  COMPLETED: 'dva_completed_chapters',
  QUIZ_RESULTS: 'dva_quiz_results',
  EXAM_RESULTS: 'dva_exam_results',
  EXAM_STATE: 'dva_exam_state',
};

// ---------- Language ----------
function getLang() {
  return localStorage.getItem(STORAGE_KEYS.LANG) || 'ar';
}

function setLang(lang) {
  const html = document.documentElement;
  html.lang = lang;
  html.dir = lang === 'ar' ? 'rtl' : 'ltr';
  localStorage.setItem(STORAGE_KEYS.LANG, lang);
  updateLangToggleUI();
}

function toggleLang() {
  setLang(getLang() === 'ar' ? 'en' : 'ar');
}

function updateLangToggleUI() {
  const lang = getLang();
  const toggles = document.querySelectorAll('[data-lang-toggle]');
  toggles.forEach((el) => {
    el.textContent = lang === 'ar' ? 'EN' : 'ع';
    el.setAttribute('aria-label', lang === 'ar' ? 'Switch to English' : 'التبديل للعربية');
  });
}

// ---------- Chapter completion ----------
function getCompletedChapters() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.COMPLETED) || '[]');
  } catch {
    return [];
  }
}

function markChapterComplete(chNum) {
  const completed = getCompletedChapters();
  if (!completed.includes(chNum)) {
    completed.push(chNum);
    localStorage.setItem(STORAGE_KEYS.COMPLETED, JSON.stringify(completed));
  }
}

function unmarkChapterComplete(chNum) {
  const completed = getCompletedChapters().filter((c) => c !== chNum);
  localStorage.setItem(STORAGE_KEYS.COMPLETED, JSON.stringify(completed));
}

function isChapterComplete(chNum) {
  return getCompletedChapters().includes(chNum);
}

// ---------- Quiz results ----------
function saveQuizResult(chNum, score, total) {
  const results = JSON.parse(localStorage.getItem(STORAGE_KEYS.QUIZ_RESULTS) || '{}');
  results[chNum] = {
    score,
    total,
    percent: Math.round((score / total) * 100),
    timestamp: Date.now(),
  };
  localStorage.setItem(STORAGE_KEYS.QUIZ_RESULTS, JSON.stringify(results));
}

function getQuizResult(chNum) {
  const results = JSON.parse(localStorage.getItem(STORAGE_KEYS.QUIZ_RESULTS) || '{}');
  return results[chNum];
}

function getAllQuizResults() {
  return JSON.parse(localStorage.getItem(STORAGE_KEYS.QUIZ_RESULTS) || '{}');
}

// ---------- Code copy ----------
function copyCode(btn) {
  const pre = btn.closest('.code-block').querySelector('pre');
  const code = pre.querySelector('code').textContent;
  navigator.clipboard.writeText(code).then(() => {
    const orig = btn.innerHTML;
    btn.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5"></i><span class="lang-ar">تم</span><span class="lang-en">Copied</span>';
    if (window.lucide) window.lucide.createIcons();
    setTimeout(() => {
      btn.innerHTML = orig;
      if (window.lucide) window.lucide.createIcons();
    }, 1800);
  });
}

// ---------- Quiz engine ----------
// Each chapter quiz calls QuizEngine.init(chapterNumber, questions)
const QuizEngine = {
  currentChapter: null,
  questions: [],
  answers: {},        // { qId: selectedOptionIndex }
  revealed: {},       // { qId: true } once answered
  wrongOnly: false,

  init(chNum, questions) {
    this.currentChapter = chNum;
    this.questions = questions;
    this.answers = {};
    this.revealed = {};
    this.render();
  },

  render() {
    const container = document.getElementById('quiz-container');
    if (!container) return;
    container.innerHTML = '';
    this.questions.forEach((q, idx) => {
      if (this.wrongOnly) {
        const ans = this.answers[q.id];
        if (ans === undefined) return;
        if (ans === q.correct) return; // skip correct ones
      }
      container.appendChild(this.renderQuestion(q, idx));
    });
    this.updateSubmitState();
    if (window.lucide) window.lucide.createIcons();
    if (window.Prism) window.Prism.highlightAll();
  },

  renderQuestion(q, idx) {
    const card = document.createElement('div');
    card.className = 'bg-white rounded-2xl border border-surface-200 p-6 space-y-4 quiz-card';
    card.dataset.qId = q.id;

    const isMulti = q.type === 'multi';
    const revealed = this.revealed[q.id];
    const selected = this.answers[q.id];

    const typeBadge = isMulti
      ? '<span class="text-xs px-2 py-0.5 bg-purple-100 text-purple-700 rounded-full font-medium"><span class="lang-ar">اختيارات متعددة</span><span class="lang-en">Multi-select</span></span>'
      : '<span class="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full font-medium"><span class="lang-ar">اختيار واحد</span><span class="lang-en">Single</span></span>';

    card.innerHTML = `
      <div class="flex items-start justify-between gap-3">
        <div class="flex items-start gap-3 flex-1">
          <span class="flex-shrink-0 w-8 h-8 rounded-full bg-brand-100 text-brand-700 font-bold flex items-center justify-center text-sm">${idx + 1}</span>
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-2">${typeBadge}</div>
            <p class="font-semibold text-surface-800 leading-relaxed">${q.question}</p>
            ${q.scenario ? `<p class="text-sm text-surface-600 mt-2 leading-relaxed bg-surface-50 p-3 rounded-lg border border-surface-100">${q.scenario}</p>` : ''}
          </div>
        </div>
      </div>
      <div class="space-y-2 quiz-options"></div>
      <div class="feedback hidden"></div>
    `;

    const optionsDiv = card.querySelector('.quiz-options');
    q.options.forEach((opt, oIdx) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'quiz-option w-full text-start p-4 rounded-xl border-2 border-surface-200 hover:border-brand-300 hover:bg-brand-50/30 transition-all flex items-start gap-3';
      btn.innerHTML = `
        <span class="flex-shrink-0 w-6 h-6 rounded-full border-2 border-surface-300 text-xs font-bold flex items-center justify-center option-letter">${String.fromCharCode(65 + oIdx)}</span>
        <span class="flex-1 text-sm leading-relaxed">${opt}</span>
      `;
      if (revealed) {
        btn.disabled = true;
        btn.classList.add('opacity-70');
        const isCorrect = isMulti ? q.correct.includes(oIdx) : q.correct === oIdx;
        const isSelected = isMulti ? (selected || []).includes(oIdx) : selected === oIdx;
        if (isCorrect) {
          btn.classList.add('!border-emerald-500', '!bg-emerald-50');
          btn.querySelector('.option-letter').classList.add('!border-emerald-500', '!bg-emerald-500', '!text-white');
        } else if (isSelected) {
          btn.classList.add('!border-red-500', '!bg-red-50');
          btn.querySelector('.option-letter').classList.add('!border-red-500', '!bg-red-500', '!text-white');
        }
      } else {
        btn.onclick = () => this.selectOption(q, oIdx, card);
        if (isMulti && selected && selected.includes(oIdx)) {
          btn.classList.add('!border-brand-500', '!bg-brand-50');
        } else if (!isMulti && selected === oIdx) {
          btn.classList.add('!border-brand-500', '!bg-brand-50');
        }
      }
      optionsDiv.appendChild(btn);
    });

    // Feedback
    if (revealed) {
      const fb = card.querySelector('.feedback');
      fb.classList.remove('hidden');
      const isCorrect = this.isAnswerCorrect(q);
      fb.className = `feedback mt-4 p-4 rounded-xl border ${isCorrect ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-red-50 border-red-200 text-red-800'}`;
      fb.innerHTML = `
        <div class="flex items-start gap-2">
          <i data-lucide="${isCorrect ? 'check-circle' : 'x-circle'}" class="w-5 h-5 flex-shrink-0 mt-0.5"></i>
          <div class="flex-1 space-y-2">
            <p class="font-bold">${isCorrect ? '<span class="lang-ar">صحيح!</span><span class="lang-en">Correct!</span>' : '<span class="lang-ar">إجابة خاطئة</span><span class="lang-en">Incorrect</span>'}</p>
            <p class="text-sm leading-relaxed">${q.explanation}</p>
            ${q.wrongExplanations ? `<div class="text-sm leading-relaxed space-y-1 pt-2 border-t border-current/10">${q.wrongExplanations.map((e, i) => `<p><strong>${String.fromCharCode(65 + i)})</strong> ${e}</p>`).join('')}</div>` : ''}
            ${q.reference ? `<p class="text-xs text-current/70 pt-1"><i data-lucide="book-open" class="inline w-3 h-3"></i> <span class="lang-ar">راجع قسم:</span><span class="lang-en">Review:</span> ${q.reference}</p>` : ''}
          </div>
        </div>
      `;
    }

    // Submit button per question
    if (!revealed) {
      const submitBtn = document.createElement('button');
      submitBtn.type = 'button';
      submitBtn.className = 'mt-2 px-5 py-2 bg-brand-600 hover:bg-brand-700 disabled:bg-surface-300 disabled:cursor-not-allowed text-white text-sm font-semibold rounded-xl transition-all';
      submitBtn.innerHTML = '<span class="lang-ar">تحقق من الإجابة</span><span class="lang-en">Check Answer</span>';
      submitBtn.disabled = selected === undefined || (isMulti && (!selected || selected.length === 0));
      submitBtn.onclick = () => this.revealQuestion(q, card);
      card.appendChild(submitBtn);
      card.dataset.submitBtn = 'yes';
    }

    return card;
  },

  selectOption(q, optIdx, card) {
    if (q.type === 'multi') {
      if (!this.answers[q.id]) this.answers[q.id] = [];
      const arr = this.answers[q.id];
      const pos = arr.indexOf(optIdx);
      if (pos >= 0) arr.splice(pos, 1);
      else arr.push(optIdx);
    } else {
      this.answers[q.id] = optIdx;
    }
    // Re-render this card
    const newCard = this.renderQuestion(q, this.questions.indexOf(q));
    card.replaceWith(newCard);
    if (window.lucide) window.lucide.createIcons();
  },

  revealQuestion(q, card) {
    this.revealed[q.id] = true;
    const newCard = this.renderQuestion(q, this.questions.indexOf(q));
    card.replaceWith(newCard);
    if (window.lucide) window.lucide.createIcons();
    this.updateSubmitState();
    this.checkAllAnswered();
  },

  isAnswerCorrect(q) {
    const ans = this.answers[q.id];
    if (ans === undefined) return false;
    if (q.type === 'multi') {
      if (!Array.isArray(ans) || !Array.isArray(q.correct)) return false;
      if (ans.length !== q.correct.length) return false;
      return ans.every((a) => q.correct.includes(a));
    }
    return ans === q.correct;
  },

  updateSubmitState() {
    // no-op; per-question buttons
  },

  checkAllAnswered() {
    const total = this.questions.length;
    const answered = this.questions.filter((q) => this.revealed[q.id]).length;
    if (answered === total) {
      const score = this.questions.filter((q) => this.isAnswerCorrect(q)).length;
      saveQuizResult(this.currentChapter, score, total);
      this.renderFinalResult(score, total);
    }
  },

  renderFinalResult(score, total) {
    const resultEl = document.getElementById('quiz-final-result');
    if (!resultEl) return;
    const pct = Math.round((score / total) * 100);
    let tone, title, advice;
    if (pct >= 80) {
      tone = 'from-emerald-500 to-emerald-600';
      title = { ar: 'ممتاز! 🎯', en: 'Excellent! 🎯' };
      advice = { ar: 'فاهم الموضوع كويس. راجع الأسئلة الخطأ وانتقل للشابتر اللي بعده.', en: 'You\'ve mastered this chapter. Review any wrong answers and move on.' };
    } else if (pct >= 60) {
      tone = 'from-amber-500 to-amber-600';
      title = { ar: 'جيد — يحتاج مراجعة', en: 'Good — needs review' };
      advice = { ar: 'فهمك للأساسيات حلو لكن في تفاصيل ضايعة. راجع الأقسام المرتبطة بالأسئلة الخاطئة قبل ما تكمل.', en: 'Solid fundamentals but missed details. Review the sections tied to wrong answers before proceeding.' };
    } else {
      tone = 'from-red-500 to-red-600';
      title = { ar: 'أعد الدراسة', en: 'Restudy recommended' };
      advice = { ar: 'الشابتر يحتاج قراءة ثانية. ركز على الأقسام الأساسية وارجع للكويز بعدين.', en: 'This chapter needs a second read. Focus on the core sections and retake the quiz.' };
    }
    resultEl.classList.remove('hidden');
    resultEl.innerHTML = `
      <div class="bg-gradient-to-br ${tone} text-white rounded-2xl p-8 space-y-4 shadow-lg">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-white/80 text-sm font-medium"><span class="lang-ar">نتيجتك</span><span class="lang-en">Your score</span></p>
            <p class="text-4xl font-bold mt-1">${score}/${total} <span class="text-2xl font-normal text-white/80">(${pct}%)</span></p>
          </div>
          <div class="text-5xl font-bold opacity-90">${pct >= 80 ? '🏆' : pct >= 60 ? '📚' : '🔁'}</div>
        </div>
        <h3 class="text-2xl font-bold"><span class="lang-ar">${title.ar}</span><span class="lang-en">${title.en}</span></h3>
        <p class="text-white/90 leading-relaxed"><span class="lang-ar">${advice.ar}</span><span class="lang-en">${advice.en}</span></p>
        <div class="flex flex-wrap gap-2 pt-2">
          <button onclick="QuizEngine.retake()" class="px-4 py-2 bg-white text-surface-800 rounded-xl text-sm font-semibold hover:bg-white/90 transition-all flex items-center gap-2">
            <i data-lucide="rotate-ccw" class="w-4 h-4"></i><span class="lang-ar">إعادة الكويز</span><span class="lang-en">Retake</span>
          </button>
          <button onclick="QuizEngine.toggleWrongOnly()" class="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-xl text-sm font-semibold transition-all flex items-center gap-2">
            <i data-lucide="filter" class="w-4 h-4"></i><span class="lang-ar">راجع الخاطئة فقط</span><span class="lang-en">Review wrong only</span>
          </button>
        </div>
      </div>
    `;
    if (window.lucide) window.lucide.createIcons();
    resultEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
  },

  retake() {
    this.answers = {};
    this.revealed = {};
    this.wrongOnly = false;
    const resultEl = document.getElementById('quiz-final-result');
    if (resultEl) resultEl.classList.add('hidden');
    this.render();
    document.getElementById('quiz-container')?.scrollIntoView({ behavior: 'smooth' });
  },

  toggleWrongOnly() {
    this.wrongOnly = !this.wrongOnly;
    this.render();
  },
};

// ---------- Navigation helpers ----------
function toggleComplete(chNum, btn) {
  if (isChapterComplete(chNum)) {
    unmarkChapterComplete(chNum);
    btn.querySelector('.btn-label').innerHTML = '<span class="lang-ar">وسم كمكتمل</span><span class="lang-en">Mark complete</span>';
    btn.classList.remove('bg-emerald-600', 'hover:bg-emerald-700');
    btn.classList.add('bg-brand-600', 'hover:bg-brand-700');
  } else {
    markChapterComplete(chNum);
    btn.querySelector('.btn-label').innerHTML = '<span class="lang-ar">مكتمل ✓</span><span class="lang-en">Completed ✓</span>';
    btn.classList.add('bg-emerald-600', 'hover:bg-emerald-700');
    btn.classList.remove('bg-brand-600', 'hover:bg-brand-700');
  }
}

// ---------- Init on load ----------
document.addEventListener('DOMContentLoaded', () => {
  setLang(getLang());
  // Set up lang toggle buttons
  document.querySelectorAll('[data-lang-toggle]').forEach((btn) => {
    btn.addEventListener('click', toggleLang);
  });
  updateLangToggleUI();
  if (window.lucide) window.lucide.createIcons();
});
