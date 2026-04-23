#!/usr/bin/env python3
"""Cheatsheet HTML generator for AWS DVA-C02 course.

Schema:
  {
    "slug": "lambda",
    "name": "AWS Lambda",
    "icon": "zap",
    "color": "amber",  # tailwind palette name
    "tagline_ar": "...",
    "tagline_en": "...",
    "key_concepts": [
      {"concept": "...", "desc_ar": "...", "desc_en": "..."},
      ...
    ],
    "limits": [
      {"limit": "...", "value": "...", "note_ar": "...", "note_en": "..."},
      ...
    ],
    "cli_commands": [
      {"desc_ar": "...", "desc_en": "...", "cmd": "..."},
      ...
    ],
    "when_to_use": [
      {"scenario_ar": "...", "scenario_en": "...", "choice": "..."},
      ...
    ],
    "vs_alternatives": [                  # optional table of comparisons
      {"feature": "...", "this": "...", "alt": "...", "alt_name": "..."},
      ...
    ],
    "exam_tips": [
      {"ar": "...", "en": "..."},
      ...
    ],
  }
"""

import json
from pathlib import Path


def render_cheatsheet(spec: dict) -> str:
    slug = spec["slug"]
    name = spec["name"]
    icon = spec["icon"]
    color = spec["color"]

    # Key concepts table
    kc_rows = ""
    for c in spec.get("key_concepts", []):
        kc_rows += f"""
  <tr>
    <td class="px-4 py-2 font-mono font-semibold text-{color}-700" dir="ltr">{c['concept']}</td>
    <td class="px-4 py-2 text-surface-600">
      <span class="lang-ar">{c['desc_ar']}</span>
      <span class="lang-en">{c['desc_en']}</span>
    </td>
  </tr>
"""

    # Limits table
    limits_rows = ""
    for l in spec.get("limits", []):
        note_html = ""
        if l.get("note_ar") or l.get("note_en"):
            note_html = f"""
      <div class="text-xs text-surface-500 mt-1">
        <span class="lang-ar">{l.get('note_ar', '')}</span>
        <span class="lang-en">{l.get('note_en', '')}</span>
      </div>
"""
        limits_rows += f"""
  <tr>
    <td class="px-4 py-2 text-surface-700">
      <span class="lang-ar">{l['limit']}</span>
      <span class="lang-en">{l.get('limit_en', l['limit'])}</span>
      {note_html}
    </td>
    <td class="px-4 py-2 font-mono text-brand-700 font-semibold whitespace-nowrap" dir="ltr">{l['value']}</td>
  </tr>
"""

    # CLI commands
    cli_html = ""
    for cmd in spec.get("cli_commands", []):
        cmd_escaped = cmd["cmd"].replace("</", "&lt;/").replace("<", "&lt;")
        cli_html += f"""
<div class="space-y-2">
  <p class="text-sm text-surface-600">
    <span class="lang-ar">{cmd['desc_ar']}</span>
    <span class="lang-en">{cmd['desc_en']}</span>
  </p>
  <div class="code-block relative group" dir="ltr">
    <button onclick="copyCode(this)" class="absolute top-2 left-2 opacity-0 group-hover:opacity-100 transition-opacity bg-surface-700 text-white text-xs px-2 py-1 rounded z-10"><i data-lucide="copy" class="w-3 h-3"></i></button>
    <pre class="!p-3"><code class="language-bash">{cmd_escaped}</code></pre>
  </div>
</div>
"""

    # When to use
    when_items = ""
    for w in spec.get("when_to_use", []):
        when_items += f"""
<div class="bg-white border border-surface-200 rounded-xl p-4 flex items-start gap-3">
  <div class="w-8 h-8 rounded-lg bg-{color}-100 text-{color}-700 flex items-center justify-center flex-shrink-0"><i data-lucide="arrow-right" class="w-4 h-4 rtl-flip"></i></div>
  <div class="flex-1">
    <p class="text-sm font-semibold text-surface-800 mb-1">
      <span class="lang-ar">{w['scenario_ar']}</span>
      <span class="lang-en">{w['scenario_en']}</span>
    </p>
    <p class="text-xs text-{color}-700 font-mono">{w['choice']}</p>
  </div>
</div>
"""

    # VS alternatives table (optional)
    vs_html = ""
    if spec.get("vs_alternatives"):
        alt_name = spec["vs_alternatives"][0].get("alt_name", "Alternative")
        vs_rows = ""
        for v in spec["vs_alternatives"]:
            vs_rows += f"""
  <tr>
    <td class="px-4 py-2 text-surface-700 font-medium">
      <span class="lang-ar">{v.get('feature_ar', v['feature'])}</span>
      <span class="lang-en">{v['feature']}</span>
    </td>
    <td class="px-4 py-2 text-{color}-700 font-semibold">{v['this']}</td>
    <td class="px-4 py-2 text-surface-600">{v['alt']}</td>
  </tr>
"""
        vs_html = f"""
<section class="bg-white rounded-2xl border border-surface-200 overflow-hidden">
  <div class="px-6 py-4 border-b border-surface-200 bg-surface-50">
    <h2 class="font-bold text-surface-800 flex items-center gap-2">
      <i data-lucide="git-compare" class="w-4 h-4"></i>
      <span class="lang-ar">مقارنة مع البدائل</span>
      <span class="lang-en">Vs Alternatives</span>
    </h2>
  </div>
  <div class="overflow-x-auto">
    <table class="w-full text-sm">
      <thead class="bg-surface-100 text-surface-700 text-xs uppercase">
        <tr>
          <th class="text-start px-4 py-2">
            <span class="lang-ar">الخاصّية</span>
            <span class="lang-en">Feature</span>
          </th>
          <th class="text-start px-4 py-2">{name}</th>
          <th class="text-start px-4 py-2">{alt_name}</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-surface-100">{vs_rows}</tbody>
    </table>
  </div>
</section>
"""

    # Exam tips
    tips_html = ""
    for t in spec.get("exam_tips", []):
        tips_html += f"""
<div class="flex gap-3 p-4 bg-amber-50 border border-amber-200 rounded-xl">
  <i data-lucide="alert-triangle" class="w-4 h-4 text-amber-600 shrink-0 mt-0.5"></i>
  <div class="text-sm text-amber-800">
    <span class="lang-ar">{t['ar']}</span>
    <span class="lang-en">{t['en']}</span>
  </div>
</div>
"""

    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name} — Cheatsheet | DVA-C02</title>

  <style>
    html[lang="ar"] .lang-en {{ display: none !important; }}
    html[lang="en"] .lang-ar {{ display: none !important; }}
    html[lang="en"] {{ direction: ltr; text-align: left; }}
    html[lang="en"] body {{ font-family: 'Inter', system-ui, sans-serif !important; }}
    html[dir="rtl"] .rtl-flip {{ transform: scaleX(-1); }}
    pre[class*="language-"] {{ border-radius: 0.5rem !important; font-size: 0.8rem !important; margin: 0 !important; padding: 0.75rem 1rem !important; background: #0f172a !important; }}
    code[class*="language-"] {{ font-family: 'JetBrains Mono', monospace !important; font-size: 0.8rem !important; }}
    @media print {{ .no-print {{ display: none !important; }} body {{ background: white; }} }}
  </style>

  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      theme: {{ extend: {{
        fontFamily: {{ arabic: ['IBM Plex Sans Arabic','sans-serif'], mono: ['JetBrains Mono','monospace'] }},
        colors: {{
          brand: {{ 50:'#f0f7ff',100:'#e0effe',200:'#bae0fd',500:'#0c99e9',600:'#0079c7',700:'#0060a1',800:'#055285' }},
          surface: {{ 50:'#f8fafc',100:'#f1f5f9',200:'#e2e8f0',500:'#64748b',600:'#475569',700:'#334155',800:'#1e293b',900:'#0f172a' }}
        }}
      }}}}
    }}
  </script>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

  <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
  <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-bash.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-json.min.js"></script>
</head>
<body class="bg-surface-50 font-arabic text-surface-800 antialiased min-h-screen">

  <nav class="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-surface-200 no-print">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between gap-3">
      <a href="../index.html" class="flex items-center gap-2 text-surface-600 hover:text-brand-700">
        <i data-lucide="arrow-right" class="w-4 h-4 rtl-flip"></i>
        <span class="text-sm font-semibold">
          <span class="lang-ar">الرئيسية</span>
          <span class="lang-en">Home</span>
        </span>
      </a>
      <div class="flex items-center gap-2">
        <button onclick="window.print()" class="p-2 text-surface-600 hover:text-brand-700 rounded-lg hover:bg-surface-100" title="Print">
          <i data-lucide="printer" class="w-4 h-4"></i>
        </button>
        <button data-lang-toggle class="px-3 py-1.5 bg-surface-100 hover:bg-surface-200 text-surface-700 rounded-lg font-semibold text-sm">EN</button>
      </div>
    </div>
  </nav>

  <header class="bg-gradient-to-bl from-{color}-600 via-{color}-700 to-{color}-900 text-white">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 py-10">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-14 h-14 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
          <i data-lucide="{icon}" class="w-7 h-7"></i>
        </div>
        <div>
          <p class="text-sm text-{color}-200 font-semibold">
            <span class="lang-ar">ملخّص سريع</span>
            <span class="lang-en">Cheatsheet</span>
          </p>
          <h1 class="text-3xl md:text-4xl font-bold">{name}</h1>
        </div>
      </div>
      <p class="text-lg text-{color}-100 max-w-2xl leading-relaxed">
        <span class="lang-ar">{spec['tagline_ar']}</span>
        <span class="lang-en">{spec['tagline_en']}</span>
      </p>
    </div>
  </header>

  <main class="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-8">

    <!-- Key concepts -->
    <section class="bg-white rounded-2xl border border-surface-200 overflow-hidden">
      <div class="px-6 py-4 border-b border-surface-200 bg-surface-50">
        <h2 class="font-bold text-surface-800 flex items-center gap-2">
          <i data-lucide="key" class="w-4 h-4 text-{color}-600"></i>
          <span class="lang-ar">المفاهيم الأساسية</span>
          <span class="lang-en">Key Concepts</span>
        </h2>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-surface-100 text-surface-700 text-xs uppercase">
            <tr>
              <th class="text-start px-4 py-2 w-48">
                <span class="lang-ar">المفهوم</span>
                <span class="lang-en">Concept</span>
              </th>
              <th class="text-start px-4 py-2">
                <span class="lang-ar">الوصف</span>
                <span class="lang-en">Description</span>
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-surface-100">{kc_rows}</tbody>
        </table>
      </div>
    </section>

    <!-- Limits -->
    {"" if not spec.get("limits") else f'''
    <section class="bg-white rounded-2xl border border-surface-200 overflow-hidden">
      <div class="px-6 py-4 border-b border-surface-200 bg-surface-50">
        <h2 class="font-bold text-surface-800 flex items-center gap-2">
          <i data-lucide="ruler" class="w-4 h-4 text-{color}-600"></i>
          <span class="lang-ar">الحدود المهمة للامتحان</span>
          <span class="lang-en">Exam-Relevant Limits</span>
        </h2>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-surface-100 text-surface-700 text-xs uppercase">
            <tr>
              <th class="text-start px-4 py-2">
                <span class="lang-ar">الحدّ</span>
                <span class="lang-en">Limit</span>
              </th>
              <th class="text-start px-4 py-2 w-40">
                <span class="lang-ar">القيمة</span>
                <span class="lang-en">Value</span>
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-surface-100">{limits_rows}</tbody>
        </table>
      </div>
    </section>
    '''}

    <!-- CLI commands -->
    {"" if not spec.get("cli_commands") else f'''
    <section class="bg-white rounded-2xl border border-surface-200 p-6 space-y-4">
      <h2 class="font-bold text-surface-800 flex items-center gap-2">
        <i data-lucide="terminal" class="w-4 h-4 text-{color}-600"></i>
        <span class="lang-ar">أوامر CLI الأساسية</span>
        <span class="lang-en">Essential CLI Commands</span>
      </h2>
      {cli_html}
    </section>
    '''}

    <!-- When to use -->
    {"" if not spec.get("when_to_use") else f'''
    <section class="space-y-3">
      <h2 class="font-bold text-surface-800 flex items-center gap-2">
        <i data-lucide="compass" class="w-4 h-4 text-{color}-600"></i>
        <span class="lang-ar">متى تستخدم {name}؟</span>
        <span class="lang-en">When to use {name}</span>
      </h2>
      <div class="grid md:grid-cols-2 gap-3">{when_items}</div>
    </section>
    '''}

    {vs_html}

    <!-- Exam tips -->
    {"" if not spec.get("exam_tips") else f'''
    <section class="space-y-3">
      <h2 class="font-bold text-surface-800 flex items-center gap-2">
        <i data-lucide="target" class="w-4 h-4 text-amber-600"></i>
        <span class="lang-ar">نصائح للامتحان</span>
        <span class="lang-en">Exam Tips</span>
      </h2>
      {tips_html}
    </section>
    '''}

  </main>

  <footer class="bg-surface-900 text-surface-400 py-6 px-4 sm:px-6 text-center text-sm no-print">
    <a href="../index.html" class="text-brand-300 hover:text-brand-100">
      <span class="lang-ar">← العودة للرئيسية</span>
      <span class="lang-en">← Back to home</span>
    </a>
  </footer>

  <script>
    function getLang() {{ return localStorage.getItem('dva_lang') || 'ar'; }}
    function setLang(lang) {{
      const html = document.documentElement;
      html.lang = lang; html.dir = lang === 'ar' ? 'rtl' : 'ltr';
      localStorage.setItem('dva_lang', lang);
      document.querySelectorAll('[data-lang-toggle]').forEach(el => el.textContent = lang === 'ar' ? 'EN' : 'ع');
    }}
    function toggleLang() {{ setLang(getLang() === 'ar' ? 'en' : 'ar'); }}
    function copyCode(btn) {{
      const code = btn.closest('.code-block').querySelector('code').textContent;
      navigator.clipboard.writeText(code).then(() => {{
        const o = btn.innerHTML;
        btn.innerHTML = '<i data-lucide="check" class="w-3 h-3"></i>';
        if (window.lucide) lucide.createIcons();
        setTimeout(() => {{ btn.innerHTML = o; if (window.lucide) lucide.createIcons(); }}, 1500);
      }});
    }}
    document.addEventListener('DOMContentLoaded', () => {{
      setLang(getLang());
      document.querySelectorAll('[data-lang-toggle]').forEach(b => b.addEventListener('click', toggleLang));
      if (window.lucide) lucide.createIcons();
      if (window.Prism) Prism.highlightAll();
    }});
  </script>
</body>
</html>"""


def generate(spec_path: str, output_dir: str = "cheatsheets"):
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)
    html_content = render_cheatsheet(spec)
    out_path = Path(output_dir) / f"{spec['slug']}.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_content, encoding="utf-8")
    print(f"✓ Generated {out_path} ({len(html_content):,} bytes)")
    return out_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python gen_cheatsheet.py <spec.json> [output_dir]")
        sys.exit(1)
    generate(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "cheatsheets")
