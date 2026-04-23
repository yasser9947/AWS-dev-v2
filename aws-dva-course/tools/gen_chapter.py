#!/usr/bin/env python3
"""Chapter HTML generator for AWS DVA-C02 course.

Takes a chapter spec (dict) and writes a complete self-contained HTML file
(inline CSS + inline JS) to chapters/chXX.html.

Chapter spec schema:
  {
    "n": 2,                        # chapter number (1-30)
    "domain": "foundations",       # foundations | development | security | deployment | troubleshoot
    "title_ar": "...",
    "title_en": "...",
    "pages": "39-71",
    "subtitle_ar": "...",
    "subtitle_en": "...",
    "tags": ["EC2", "Instances", ...],
    "objectives": [                # exam objectives mapping
      {"concept": "...", "tested_ar": "...", "tested_en": "..."},
      ...
    ],
    "sections": [                  # main content sections
      {
        "title_ar": "...",
        "title_en": "...",
        "blocks": [                # each block is a dict with "type" key
          {"type": "p", "ar": "...", "en": "..."},
          {"type": "callout", "tone": "tip|warn|pitfall|key|senior", "ar": "...", "en": "..."},
          {"type": "code", "lang": "java|python|bash|yaml|json", "code": "..."},
          {"type": "table", "headers": {"ar": [...], "en": [...]}, "rows": [...]},
          {"type": "cards", "items": [{"icon": "...", "title_ar":"...", "title_en":"...", "body_ar":"...", "body_en":"..."}, ...]},
          {"type": "compare", "left": {...}, "right": {...}},  # two-column comparison
          {"type": "html", "content": "..."},   # raw HTML escape hatch
        ]
      },
      ...
    ],
    "lab": {                       # optional hands-on lab
      "goal_ar": "...",
      "goal_en": "...",
      "steps": [
        {"title_ar":"...", "title_en":"...", "body_ar":"...", "body_en":"...", "code":"..."},
      ],
      "warning_ar": "...",
      "warning_en": "...",
    },
    "quiz": [                      # quiz questions
      {
        "id": "q1",
        "type": "single|multi",
        "question_ar": "...",
        "question_en": "...",
        "options_ar": [...],
        "options_en": [...],
        "correct": 2,               # int or list
        "explanation_ar": "...",
        "explanation_en": "...",
        "wrong_ar": ["...", "", "...", ""],   # optional per-wrong explanations (empty = skip)
        "wrong_en": ["...", "", "...", ""],
        "reference_ar": "القسم ٣",
        "reference_en": "Section 3",
      },
      ...
    ],
    "summary": [                  # 4 key takeaways
      {"icon": "map-pin", "title_ar":"...", "title_en":"...", "body_ar":"...", "body_en":"..."},
      ...
    ],
    "mnemonic_ar": "...",
    "mnemonic_en": "...",
    "prev": 1,                     # prev chapter number (None for ch01)
    "next": 3,                     # next chapter number (None for ch30)
  }
"""

import json
import html
from pathlib import Path

DOMAIN_LABELS = {
    "foundations": {"ar": "أساسيات", "en": "Foundations", "badge": "bg-surface-500"},
    "development": {"ar": "النطاق الأول — 32%", "en": "Domain 1 — 32%", "badge": "bg-blue-600"},
    "security":    {"ar": "النطاق الثاني — 26%", "en": "Domain 2 — 26%", "badge": "bg-red-600"},
    "deployment":  {"ar": "النطاق الثالث — 24%", "en": "Domain 3 — 24%", "badge": "bg-emerald-600"},
    "troubleshoot":{"ar": "النطاق الرابع — 18%", "en": "Domain 4 — 18%", "badge": "bg-amber-600"},
}

DOMAIN_ICONS = {
    "foundations": "layers",
    "development": "code-2",
    "security": "shield",
    "deployment": "rocket",
    "troubleshoot": "activity",
}

CALLOUT_STYLES = {
    "tip":     {"bg": "bg-emerald-50", "border": "border-emerald-200", "text": "text-emerald-800", "icon": "lightbulb", "icon_color": "text-emerald-600", "label_ar": "نصيحة:", "label_en": "Tip:"},
    "warn":    {"bg": "bg-amber-50", "border": "border-amber-200", "text": "text-amber-800", "icon": "alert-triangle", "icon_color": "text-amber-600", "label_ar": "نصيحة للامتحان:", "label_en": "Exam tip:"},
    "pitfall": {"bg": "bg-red-50", "border": "border-red-200", "text": "text-red-800", "icon": "alert-octagon", "icon_color": "text-red-600", "label_ar": "فخّ شائع:", "label_en": "Common pitfall:"},
    "key":     {"bg": "bg-brand-50", "border": "border-brand-200", "text": "text-brand-800", "icon": "info", "icon_color": "text-brand-600", "label_ar": "مفهوم أساسي:", "label_en": "Key concept:"},
    "senior":  {"bg": "bg-indigo-50", "border": "border-indigo-200", "text": "text-indigo-800", "icon": "sparkles", "icon_color": "text-indigo-600", "label_ar": "للمطوّر السينيور:", "label_en": "For the senior dev:"},
}


def render_block(block):
    """Render a single content block to HTML."""
    t = block["type"]

    if t == "p":
        return f"""
  <p class="text-surface-700 leading-relaxed lang-ar">{block['ar']}</p>
  <p class="text-surface-700 leading-relaxed lang-en">{block['en']}</p>
""".strip()

    if t == "callout":
        s = CALLOUT_STYLES[block["tone"]]
        return f"""
  <div class="flex gap-3 p-4 {s['bg']} border {s['border']} rounded-xl">
    <i data-lucide="{s['icon']}" class="w-5 h-5 {s['icon_color']} shrink-0 mt-0.5"></i>
    <div class="text-sm {s['text']}">
      <strong class="lang-ar">{s['label_ar']}</strong><strong class="lang-en">{s['label_en']}</strong>
      <span class="lang-ar"> {block['ar']}</span>
      <span class="lang-en"> {block['en']}</span>
    </div>
  </div>
""".strip()

    if t == "code":
        lang = block.get("lang", "bash")
        code = block["code"].replace("</", "&lt;/").replace("<", "&lt;")
        return f"""
  <div class="code-block relative group" dir="ltr">
    <button onclick="copyCode(this)" class="absolute top-3 left-3 opacity-0 group-hover:opacity-100 transition-opacity bg-surface-700 hover:bg-surface-600 text-white text-xs px-2.5 py-1.5 rounded-lg flex items-center gap-1 z-10">
      <i data-lucide="copy" class="w-3.5 h-3.5"></i>
      <span class="lang-ar">نسخ</span><span class="lang-en">Copy</span>
    </button>
    <pre class="scrollbar-thin"><code class="language-{lang}">{code}</code></pre>
  </div>
""".strip()

    if t == "table":
        headers_ar = block["headers"]["ar"]
        headers_en = block["headers"]["en"]
        head_html = "".join(
            f'<th class="text-start px-4 py-2 font-semibold"><span class="lang-ar">{ar}</span><span class="lang-en">{en}</span></th>'
            for ar, en in zip(headers_ar, headers_en)
        )
        rows_html = ""
        for row in block["rows"]:
            row_cells = ""
            for cell in row:
                if isinstance(cell, dict):
                    ar_cell = cell.get("ar", "")
                    en_cell = cell.get("en", "")
                    mono = "font-mono text-brand-700" if cell.get("mono") else ""
                    ltr = 'dir="ltr"' if cell.get("mono") else ""
                    if mono:
                        row_cells += f'<td class="px-4 py-2 {mono}" {ltr}>{cell.get("value", ar_cell)}</td>'
                    else:
                        row_cells += f'<td class="px-4 py-2 text-surface-600"><span class="lang-ar">{ar_cell}</span><span class="lang-en">{en_cell}</span></td>'
                else:
                    row_cells += f'<td class="px-4 py-2 text-surface-600">{cell}</td>'
            rows_html += f"<tr>{row_cells}</tr>"
        return f"""
  <div class="overflow-x-auto">
    <table class="w-full text-sm border border-surface-200 rounded-lg overflow-hidden">
      <thead class="bg-surface-100 text-surface-700"><tr>{head_html}</tr></thead>
      <tbody class="divide-y divide-surface-200">{rows_html}</tbody>
    </table>
  </div>
""".strip()

    if t == "cards":
        items_html = ""
        for item in block["items"]:
            icon = item.get("icon", "check")
            icon_bg = item.get("icon_bg", "bg-brand-100")
            icon_color = item.get("icon_color", "text-brand-700")
            items_html += f"""
  <div class="bg-white border border-surface-200 rounded-xl p-5">
    <div class="flex items-center gap-2 mb-2">
      <div class="w-8 h-8 rounded-lg {icon_bg} {icon_color} flex items-center justify-center"><i data-lucide="{icon}" class="w-4 h-4"></i></div>
      <h4 class="font-bold text-surface-800"><span class="lang-ar">{item['title_ar']}</span><span class="lang-en">{item['title_en']}</span></h4>
    </div>
    <p class="text-sm text-surface-600 leading-relaxed lang-ar">{item['body_ar']}</p>
    <p class="text-sm text-surface-600 leading-relaxed lang-en">{item['body_en']}</p>
  </div>
"""
        cols = block.get("cols", 2)
        return f'<div class="grid md:grid-cols-{cols} gap-4">{items_html}</div>'

    if t == "compare":
        left, right = block["left"], block["right"]
        return f"""
  <div class="grid md:grid-cols-2 gap-4">
    <div class="bg-gradient-to-br from-{left.get('tone','purple')}-50 to-white border-2 border-{left.get('tone','purple')}-200 rounded-2xl p-6">
      <div class="flex items-center gap-2 mb-4">
        <div class="w-10 h-10 rounded-xl bg-{left.get('tone','purple')}-600 text-white flex items-center justify-center">
          <i data-lucide="{left.get('icon','check')}" class="w-5 h-5"></i>
        </div>
        <h3 class="font-bold text-surface-800 text-lg"><span class="lang-ar">{left['title_ar']}</span><span class="lang-en">{left['title_en']}</span></h3>
      </div>
      <p class="text-sm text-surface-700 lang-ar">{left['body_ar']}</p>
      <p class="text-sm text-surface-700 lang-en">{left['body_en']}</p>
    </div>
    <div class="bg-gradient-to-br from-{right.get('tone','emerald')}-50 to-white border-2 border-{right.get('tone','emerald')}-200 rounded-2xl p-6">
      <div class="flex items-center gap-2 mb-4">
        <div class="w-10 h-10 rounded-xl bg-{right.get('tone','emerald')}-600 text-white flex items-center justify-center">
          <i data-lucide="{right.get('icon','check')}" class="w-5 h-5"></i>
        </div>
        <h3 class="font-bold text-surface-800 text-lg"><span class="lang-ar">{right['title_ar']}</span><span class="lang-en">{right['title_en']}</span></h3>
      </div>
      <p class="text-sm text-surface-700 lang-ar">{right['body_ar']}</p>
      <p class="text-sm text-surface-700 lang-en">{right['body_en']}</p>
    </div>
  </div>
""".strip()

    if t == "html":
        return block["content"]

    return f"<!-- unknown block type: {t} -->"


def render_section(idx, section):
    blocks_html = "\n".join(render_block(b) for b in section["blocks"])
    return f"""
<section class="space-y-5">
  <div class="flex items-center gap-3">
    <div class="w-10 h-10 rounded-xl bg-brand-600 text-white font-bold flex items-center justify-center">{idx}</div>
    <h2 class="text-2xl font-bold text-surface-800">
      <span class="lang-ar">{section['title_ar']}</span>
      <span class="lang-en">{section['title_en']}</span>
    </h2>
  </div>
  {blocks_html}
</section>
""".strip()


def render_objectives_table(objectives):
    rows = ""
    for obj in objectives:
        rows += f"""
  <tr>
    <td class="px-4 py-2 font-mono text-brand-700" dir="ltr">{obj['concept']}</td>
    <td class="px-4 py-2 text-surface-600">
      <span class="lang-ar">{obj['tested_ar']}</span>
      <span class="lang-en">{obj['tested_en']}</span>
    </td>
  </tr>
"""
    return f"""
<section class="bg-white rounded-2xl border border-surface-200 overflow-hidden">
  <div class="bg-gradient-to-l from-brand-50 to-white border-b border-surface-200 px-6 py-4">
    <div class="flex items-center gap-2">
      <i data-lucide="clipboard-check" class="w-5 h-5 text-brand-600"></i>
      <h2 class="text-lg font-bold text-surface-800">
        <span class="lang-ar">ربط المحتوى بأهداف الامتحان</span>
        <span class="lang-en">Exam Objectives Mapping</span>
      </h2>
    </div>
  </div>
  <div class="p-6">
    <div class="overflow-x-auto">
      <table class="w-full text-sm border border-surface-200 rounded-lg overflow-hidden">
        <thead class="bg-surface-100 text-surface-700">
          <tr>
            <th class="text-start px-4 py-2 font-semibold">
              <span class="lang-ar">المفهوم</span>
              <span class="lang-en">Concept</span>
            </th>
            <th class="text-start px-4 py-2 font-semibold">
              <span class="lang-ar">يُستخدم في الامتحان ضمن</span>
              <span class="lang-en">Tested within</span>
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-surface-200">{rows}</tbody>
      </table>
    </div>
  </div>
</section>
""".strip()


def render_lab(lab):
    if not lab:
        return ""
    steps_html = ""
    ar_digits = "٠١٢٣٤٥٦٧٨٩"
    for i, step in enumerate(lab["steps"], 1):
        ar_num = "".join(ar_digits[int(d)] for d in str(i))
        code_block = ""
        if step.get("code"):
            code_escaped = step["code"].replace("</", "&lt;/").replace("<", "&lt;")
            code_block = f"""
    <div class="code-block relative group mt-2" dir="ltr">
      <button onclick="copyCode(this)" class="absolute top-2 left-2 opacity-0 group-hover:opacity-100 transition-opacity bg-surface-700 text-white text-xs px-2 py-1 rounded z-10">
        <i data-lucide="copy" class="w-3 h-3"></i>
      </button>
      <pre class="!p-3"><code class="language-{step.get('lang', 'bash')}">{code_escaped}</code></pre>
    </div>
"""
        body_ar = f'<p class="text-surface-600 leading-relaxed lang-ar">{step["body_ar"]}</p>' if step.get("body_ar") else ""
        body_en = f'<p class="text-surface-600 leading-relaxed lang-en">{step["body_en"]}</p>' if step.get("body_en") else ""
        steps_html += f"""
<li class="flex gap-3">
  <span class="flex-shrink-0 w-7 h-7 rounded-full bg-indigo-600 text-white font-bold flex items-center justify-center text-xs">{ar_num}</span>
  <div>
    <p class="font-semibold mb-1">
      <span class="lang-ar">{step['title_ar']}</span>
      <span class="lang-en">{step['title_en']}</span>
    </p>
    {body_ar}{body_en}{code_block}
  </div>
</li>
"""

    warning_html = ""
    if lab.get("warning_ar") or lab.get("warning_en"):
        warning_html = f"""
<div class="flex gap-3 p-4 bg-amber-100 border border-amber-300 rounded-xl mt-5">
  <i data-lucide="alert-triangle" class="w-5 h-5 text-amber-700 shrink-0 mt-0.5"></i>
  <div class="text-sm text-amber-900">
    <strong class="lang-ar">تنبيه:</strong>
    <strong class="lang-en">Warning:</strong>
    <span class="lang-ar"> {lab.get('warning_ar', '')}</span>
    <span class="lang-en"> {lab.get('warning_en', '')}</span>
  </div>
</div>
"""

    return f"""
<section class="bg-gradient-to-br from-indigo-50 to-purple-50 border-2 border-indigo-200 rounded-2xl p-6 md:p-8">
  <div class="flex items-center gap-2 mb-3">
    <div class="w-10 h-10 rounded-xl bg-indigo-600 text-white flex items-center justify-center">
      <i data-lucide="flask-conical" class="w-5 h-5"></i>
    </div>
    <h2 class="text-xl font-bold text-surface-800">
      <span class="lang-ar">معمل عملي</span>
      <span class="lang-en">Hands-on Lab</span>
    </h2>
  </div>
  <p class="text-sm text-surface-700 mb-4 lang-ar"><strong>الهدف:</strong> {lab['goal_ar']}</p>
  <p class="text-sm text-surface-700 mb-4 lang-en"><strong>Goal:</strong> {lab['goal_en']}</p>
  <ol class="space-y-3 text-sm text-surface-700">{steps_html}</ol>
  {warning_html}
</section>
""".strip()


def render_summary(summary, mnemonic_ar, mnemonic_en):
    cards = ""
    for s in summary:
        cards += f"""
<div class="bg-white/10 backdrop-blur-sm rounded-2xl p-5 border border-white/10">
  <div class="flex items-start gap-3">
    <div class="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center flex-shrink-0"><i data-lucide="{s.get('icon', 'check')}" class="w-4 h-4"></i></div>
    <div>
      <p class="font-bold mb-1">
        <span class="lang-ar">{s['title_ar']}</span>
        <span class="lang-en">{s['title_en']}</span>
      </p>
      <p class="text-sm text-brand-100 leading-relaxed lang-ar">{s['body_ar']}</p>
      <p class="text-sm text-brand-100 leading-relaxed lang-en">{s['body_en']}</p>
    </div>
  </div>
</div>
"""
    mnem_html = ""
    if mnemonic_ar or mnemonic_en:
        mnem_html = f"""
<div class="mt-6 p-5 bg-black/20 backdrop-blur-sm rounded-2xl border border-white/10">
  <div class="flex items-center gap-2 mb-2">
    <i data-lucide="brain" class="w-5 h-5 text-amber-300"></i>
    <p class="font-bold text-amber-100">
      <span class="lang-ar">للحفظ السريع:</span>
      <span class="lang-en">Mnemonic:</span>
    </p>
  </div>
  <p class="text-sm text-brand-100 leading-relaxed lang-ar">{mnemonic_ar}</p>
  <p class="text-sm text-brand-100 leading-relaxed lang-en">{mnemonic_en}</p>
</div>
"""
    return f"""
<section class="bg-gradient-to-br from-brand-600 via-brand-700 to-brand-900 text-white rounded-3xl p-8 md:p-10 shadow-xl">
  <div class="flex items-center gap-3 mb-6">
    <div class="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
      <i data-lucide="sparkles" class="w-6 h-6"></i>
    </div>
    <h2 class="text-2xl md:text-3xl font-bold">
      <span class="lang-ar">الملخّص وأهمّ النقاط</span>
      <span class="lang-en">Summary & Key Takeaways</span>
    </h2>
  </div>
  <div class="grid md:grid-cols-2 gap-4">{cards}</div>
  {mnem_html}
</section>
""".strip()


def render_navigation(ch_n, prev_n, next_n):
    prev_html = ""
    if prev_n:
        prev_id = str(prev_n).zfill(2)
        prev_html = f"""
<a href="ch{prev_id}.html" class="inline-flex items-center gap-2 px-5 py-2.5 bg-white border border-surface-200 hover:bg-surface-50 text-surface-700 rounded-xl font-semibold text-sm transition-all">
  <i data-lucide="arrow-right" class="w-4 h-4 rtl-flip"></i>
  <span class="lang-ar">السابق</span>
  <span class="lang-en">Previous</span>
</a>
"""

    next_html = ""
    if next_n:
        next_id = str(next_n).zfill(2)
        next_html = f"""
<a href="ch{next_id}.html" class="inline-flex items-center gap-2 px-5 py-2.5 bg-surface-800 hover:bg-surface-900 text-white rounded-xl font-semibold text-sm transition-all">
  <span class="lang-ar">التالي</span>
  <span class="lang-en">Next</span>
  <i data-lucide="arrow-left" class="w-4 h-4 rtl-flip"></i>
</a>
"""

    return f"""
<nav class="flex items-center justify-between gap-3 pt-6 border-t border-surface-200 flex-wrap">
  <div>{prev_html}</div>
  <button onclick="toggleComplete({ch_n}, this)" id="complete-btn" class="inline-flex items-center gap-2 px-5 py-2.5 bg-brand-600 hover:bg-brand-700 text-white rounded-xl font-semibold text-sm transition-all shadow-sm">
    <i data-lucide="check" class="w-4 h-4"></i>
    <span class="btn-label">
      <span class="lang-ar">وسم كمكتمل</span>
      <span class="lang-en">Mark complete</span>
    </span>
  </button>
  {next_html}
</nav>
""".strip()


def render_quiz_data(quiz):
    """Convert quiz spec to JS array string."""
    js_questions = []
    for q in quiz:
        opts_combined = []
        for i, (ar, en) in enumerate(zip(q["options_ar"], q["options_en"])):
            opts_combined.append(f'<span class="lang-ar">{ar}</span><span class="lang-en">{en}</span>')

        correct = q["correct"]
        if isinstance(correct, list):
            correct_js = f"[{','.join(str(c) for c in correct)}]"
        else:
            correct_js = str(correct)

        wrong_js = ""
        if q.get("wrong_ar") or q.get("wrong_en"):
            wrong_items = []
            wrong_ar = q.get("wrong_ar") or [""] * len(q["options_ar"])
            wrong_en = q.get("wrong_en") or [""] * len(q["options_en"])
            for ar, en in zip(wrong_ar, wrong_en):
                if ar or en:
                    wrong_items.append(f'"<span class=\\"lang-ar\\">{ar}</span><span class=\\"lang-en\\">{en}</span>"')
                else:
                    wrong_items.append('""')
            wrong_js = f",\n        wrongExplanations: [{', '.join(wrong_items)}]"

        ref_js = ""
        if q.get("reference_ar") or q.get("reference_en"):
            ref_js = f',\n        reference: "<span class=\\"lang-ar\\">{q.get("reference_ar","")}</span><span class=\\"lang-en\\">{q.get("reference_en","")}</span>"'

        options_js = "[\n          " + ",\n          ".join(f'"{o}"' for o in opts_combined) + "\n        ]"

        question_combined = f'<span class="lang-ar">{q["question_ar"]}</span><span class="lang-en">{q["question_en"]}</span>'
        explanation_combined = f'<span class="lang-ar">{q["explanation_ar"]}</span><span class="lang-en">{q["explanation_en"]}</span>'

        js_questions.append(f"""{{
        id: "{q['id']}",
        type: "{q['type']}",
        question: "{question_combined}",
        options: {options_js},
        correct: {correct_js},
        explanation: "{explanation_combined}"{wrong_js}{ref_js}
      }}""")

    return ",\n      ".join(js_questions)


def render_chapter(spec: dict) -> str:
    """Render a complete chapter HTML file."""
    ch_n = spec["n"]
    ch_id = str(ch_n).zfill(2)
    domain = spec["domain"]
    domain_info = DOMAIN_LABELS[domain]
    domain_icon = DOMAIN_ICONS[domain]

    # Convert ch_n to Arabic-Indic digits
    ar_digits = "٠١٢٣٤٥٦٧٨٩"
    ch_n_ar = "".join(ar_digits[int(d)] for d in str(ch_n))

    # Render sections
    sections_html = "\n\n".join(render_section(i + 1, s) for i, s in enumerate(spec["sections"]))

    # Objectives table
    objectives_html = render_objectives_table(spec["objectives"])

    # Lab (optional)
    lab_html = render_lab(spec.get("lab"))

    # Summary
    summary_html = render_summary(
        spec["summary"],
        spec.get("mnemonic_ar", ""),
        spec.get("mnemonic_en", ""),
    )

    # Navigation
    nav_html = render_navigation(ch_n, spec.get("prev"), spec.get("next"))

    # Tags
    tags_html = "\n".join(
        f'<span class="px-3 py-1 bg-surface-500/30 backdrop-blur-sm rounded-full text-xs font-medium font-mono">{tag}</span>'
        for tag in spec.get("tags", [])
    )

    # Quiz JS data
    quiz_js = render_quiz_data(spec["quiz"])
    quiz_count = len(spec["quiz"])
    quiz_count_ar = "".join(ar_digits[int(d)] for d in str(quiz_count))

    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ch {ch_id} — {spec['title_en']} | DVA-C02</title>

  <style>
    html[lang="ar"] .lang-en {{ display: none !important; }}
    html[lang="en"] .lang-ar {{ display: none !important; }}
    html[lang="en"] {{ direction: ltr; text-align: left; }}
    html[lang="en"] body {{ font-family: 'Inter', system-ui, sans-serif !important; }}
    pre[class*="language-"] {{
      border-radius: 0.75rem !important; font-size: 0.875rem !important;
      margin: 0 !important; padding: 1.25rem 1.5rem !important; background: #0f172a !important;
    }}
    code[class*="language-"] {{ font-family: 'JetBrains Mono', monospace !important; font-size: 0.85rem !important; }}
    .scrollbar-thin::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    .scrollbar-thin::-webkit-scrollbar-thumb {{ background: #64748b; border-radius: 3px; }}
    .scrollbar-thin::-webkit-scrollbar-track {{ background: transparent; }}
    .text-balance {{ text-wrap: balance; }}
    html[dir="rtl"] .rtl-flip {{ transform: scaleX(-1); }}
    .quiz-option {{ text-align: inherit; }}
    .quiz-option:disabled {{ cursor: not-allowed; }}
  </style>

  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          fontFamily: {{
            arabic: ['IBM Plex Sans Arabic', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace'],
          }},
          colors: {{
            brand: {{ 50:'#f0f7ff',100:'#e0effe',200:'#bae0fd',300:'#7ccbfc',400:'#36b3f8',500:'#0c99e9',600:'#0079c7',700:'#0060a1',800:'#055285',900:'#0a446e',950:'#072b49' }},
            surface: {{ 50:'#f8fafc',100:'#f1f5f9',200:'#e2e8f0',300:'#cbd5e1',400:'#94a3b8',500:'#64748b',600:'#475569',700:'#334155',800:'#1e293b',900:'#0f172a',950:'#020617' }}
          }}
        }}
      }}
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
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-java.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-yaml.min.js"></script>
</head>
<body class="bg-surface-50 font-arabic text-surface-800 antialiased min-h-screen">

  <nav class="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-surface-200">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between gap-3">
      <a href="../index.html" class="flex items-center gap-2 text-surface-600 hover:text-brand-700 transition-colors">
        <i data-lucide="arrow-right" class="w-4 h-4 rtl-flip"></i>
        <span class="text-sm font-semibold"><span class="lang-ar">الرئيسية</span><span class="lang-en">Home</span></span>
      </a>
      <div class="flex items-center gap-2">
        <button data-lang-toggle class="px-3 py-1.5 bg-surface-100 hover:bg-surface-200 text-surface-700 rounded-lg font-semibold text-sm transition-all">EN</button>
      </div>
    </div>
  </nav>

  <header class="bg-gradient-to-bl from-surface-800 via-surface-700 to-surface-900 text-white">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 py-12">
      <div class="flex items-center gap-2 mb-4 text-xs text-surface-300 flex-wrap">
        <span class="px-2.5 py-1 {domain_info['badge']}/50 rounded-full font-semibold flex items-center gap-1.5">
          <i data-lucide="{domain_icon}" class="w-3 h-3"></i>
          <span class="lang-ar">{domain_info['ar']}</span>
          <span class="lang-en">{domain_info['en']}</span>
        </span>
        <span class="text-surface-400">·</span>
        <span class="lang-ar">الشابتر {ch_n_ar} من ٣٠</span>
        <span class="lang-en">Chapter {ch_n} of 30</span>
        <span class="text-surface-400">·</span>
        <span class="font-mono text-xs">p.{spec['pages']}</span>
      </div>
      <h1 class="text-3xl md:text-4xl font-bold mb-3 text-balance">
        <span class="lang-ar">{spec['title_ar']}</span>
        <span class="lang-en">{spec['title_en']}</span>
      </h1>
      <p class="text-lg text-surface-200 mb-6 max-w-2xl leading-relaxed">
        <span class="lang-ar">{spec['subtitle_ar']}</span>
        <span class="lang-en">{spec['subtitle_en']}</span>
      </p>
      <div class="flex flex-wrap gap-2">{tags_html}</div>
    </div>
  </header>

  <main class="max-w-5xl mx-auto px-4 sm:px-6 py-12 space-y-12">
    {objectives_html}

    {sections_html}

    {lab_html}

    <section class="space-y-5">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-amber-500 text-white flex items-center justify-center">
          <i data-lucide="help-circle" class="w-5 h-5"></i>
        </div>
        <h2 class="text-2xl font-bold text-surface-800">
          <span class="lang-ar">كويز الشابتر — {quiz_count_ar} أسئلة</span>
          <span class="lang-en">Chapter Quiz ({quiz_count} questions)</span>
        </h2>
      </div>
      <p class="text-sm text-surface-600 leading-relaxed bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-2">
        <i data-lucide="info" class="w-4 h-4 text-amber-700 flex-shrink-0 mt-0.5"></i>
        <span class="lang-ar">الأسئلة على نمط الامتحان الفعلي وعلى هيئة سيناريوهات واقعية.</span>
        <span class="lang-en">Questions follow the real exam style — scenario-based.</span>
      </p>
      <div id="quiz-container" class="space-y-4"></div>
      <div id="quiz-final-result" class="hidden"></div>
    </section>

    {summary_html}

    {nav_html}
  </main>

  <footer class="bg-surface-900 text-surface-400 py-8 px-4 sm:px-6 text-center text-sm">
    <a href="../index.html" class="text-brand-300 hover:text-brand-100">
      <span class="lang-ar">← العودة للرئيسية</span>
      <span class="lang-en">← Back to home</span>
    </a>
  </footer>

  <script>
    const STORAGE_KEYS = {{ LANG:'dva_lang', COMPLETED:'dva_completed_chapters', QUIZ_RESULTS:'dva_quiz_results' }};
    function getLang() {{ return localStorage.getItem(STORAGE_KEYS.LANG) || 'ar'; }}
    function setLang(lang) {{
      const html = document.documentElement;
      html.lang = lang; html.dir = lang === 'ar' ? 'rtl' : 'ltr';
      localStorage.setItem(STORAGE_KEYS.LANG, lang);
      document.querySelectorAll('[data-lang-toggle]').forEach(el => el.textContent = lang === 'ar' ? 'EN' : 'ع');
      if (QuizEngine.currentChapter) QuizEngine.render();
    }}
    function toggleLang() {{ setLang(getLang() === 'ar' ? 'en' : 'ar'); }}
    function getCompletedChapters() {{ try {{ return JSON.parse(localStorage.getItem(STORAGE_KEYS.COMPLETED) || '[]'); }} catch {{ return []; }} }}
    function markChapterComplete(n) {{ const c = getCompletedChapters(); if (!c.includes(n)) {{ c.push(n); localStorage.setItem(STORAGE_KEYS.COMPLETED, JSON.stringify(c)); }} }}
    function unmarkChapterComplete(n) {{ localStorage.setItem(STORAGE_KEYS.COMPLETED, JSON.stringify(getCompletedChapters().filter(x => x !== n))); }}
    function isChapterComplete(n) {{ return getCompletedChapters().includes(n); }}
    function toggleComplete(n, btn) {{
      if (isChapterComplete(n)) {{
        unmarkChapterComplete(n);
        btn.querySelector('.btn-label').innerHTML = '<span class="lang-ar">وسم كمكتمل</span><span class="lang-en">Mark complete</span>';
        btn.classList.remove('bg-emerald-600', 'hover:bg-emerald-700');
        btn.classList.add('bg-brand-600', 'hover:bg-brand-700');
      }} else {{
        markChapterComplete(n);
        btn.querySelector('.btn-label').innerHTML = '<span class="lang-ar">مكتمل ✓</span><span class="lang-en">Completed ✓</span>';
        btn.classList.add('bg-emerald-600', 'hover:bg-emerald-700');
        btn.classList.remove('bg-brand-600', 'hover:bg-brand-700');
      }}
    }}
    function saveQuizResult(ch, score, total) {{
      const r = JSON.parse(localStorage.getItem(STORAGE_KEYS.QUIZ_RESULTS) || '{{}}');
      r[ch] = {{ score, total, percent: Math.round(score/total*100), timestamp: Date.now() }};
      localStorage.setItem(STORAGE_KEYS.QUIZ_RESULTS, JSON.stringify(r));
    }}
    function copyCode(btn) {{
      const pre = btn.closest('.code-block').querySelector('pre');
      navigator.clipboard.writeText(pre.querySelector('code').textContent).then(() => {{
        const orig = btn.innerHTML;
        btn.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5"></i><span class="lang-ar">تم</span><span class="lang-en">Copied</span>';
        if (window.lucide) lucide.createIcons();
        setTimeout(() => {{ btn.innerHTML = orig; if (window.lucide) lucide.createIcons(); }}, 1800);
      }});
    }}

    const QuizEngine = {{
      currentChapter: null, questions: [], answers: {{}}, revealed: {{}}, wrongOnly: false,
      init(ch, qs) {{ this.currentChapter = ch; this.questions = qs; this.answers = {{}}; this.revealed = {{}}; this.render(); }},
      render() {{
        const c = document.getElementById('quiz-container'); if (!c) return; c.innerHTML = '';
        this.questions.forEach((q, idx) => {{
          if (this.wrongOnly) {{
            if (this.answers[q.id] === undefined) return;
            if (this.isCorrect(q)) return;
          }}
          c.appendChild(this.renderQ(q, idx));
        }});
        if (window.lucide) lucide.createIcons();
      }},
      renderQ(q, idx) {{
        const card = document.createElement('div');
        card.className = 'bg-white rounded-2xl border border-surface-200 p-6 space-y-4';
        card.dataset.qId = q.id;
        const isMulti = q.type === 'multi';
        const revealed = this.revealed[q.id];
        const sel = this.answers[q.id];
        const badge = isMulti
          ? '<span class="text-xs px-2 py-0.5 bg-purple-100 text-purple-700 rounded-full font-medium"><span class="lang-ar">اختيارات متعدّدة</span><span class="lang-en">Multi-select</span></span>'
          : '<span class="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full font-medium"><span class="lang-ar">اختيار واحد</span><span class="lang-en">Single</span></span>';
        card.innerHTML = `<div class="flex items-start gap-3"><span class="flex-shrink-0 w-8 h-8 rounded-full bg-brand-100 text-brand-700 font-bold flex items-center justify-center text-sm">${{idx+1}}</span><div class="flex-1 min-w-0"><div class="mb-2">${{badge}}</div><p class="font-semibold text-surface-800 leading-relaxed">${{q.question}}</p></div></div><div class="space-y-2 quiz-options"></div><div class="feedback hidden"></div>`;
        const optsDiv = card.querySelector('.quiz-options');
        q.options.forEach((opt, oIdx) => {{
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'quiz-option w-full text-start p-4 rounded-xl border-2 border-surface-200 hover:border-brand-300 hover:bg-brand-50/30 transition-all flex items-start gap-3';
          btn.innerHTML = `<span class="flex-shrink-0 w-6 h-6 rounded-full border-2 border-surface-300 text-xs font-bold flex items-center justify-center option-letter">${{String.fromCharCode(65+oIdx)}}</span><span class="flex-1 text-sm leading-relaxed">${{opt}}</span>`;
          if (revealed) {{
            btn.disabled = true; btn.classList.add('opacity-70');
            const correct = isMulti ? q.correct.includes(oIdx) : q.correct === oIdx;
            const selected = isMulti ? (sel||[]).includes(oIdx) : sel === oIdx;
            if (correct) {{ btn.classList.add('!border-emerald-500', '!bg-emerald-50'); btn.querySelector('.option-letter').classList.add('!border-emerald-500', '!bg-emerald-500', '!text-white'); }}
            else if (selected) {{ btn.classList.add('!border-red-500', '!bg-red-50'); btn.querySelector('.option-letter').classList.add('!border-red-500', '!bg-red-500', '!text-white'); }}
          }} else {{
            btn.onclick = () => this.selectOpt(q, oIdx, card);
            if (isMulti && sel && sel.includes(oIdx)) btn.classList.add('!border-brand-500', '!bg-brand-50');
            else if (!isMulti && sel === oIdx) btn.classList.add('!border-brand-500', '!bg-brand-50');
          }}
          optsDiv.appendChild(btn);
        }});
        if (revealed) {{
          const fb = card.querySelector('.feedback'); fb.classList.remove('hidden');
          const ok = this.isCorrect(q);
          fb.className = `feedback mt-4 p-4 rounded-xl border ${{ok ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-red-50 border-red-200 text-red-800'}}`;
          fb.innerHTML = `<div class="flex items-start gap-2"><i data-lucide="${{ok ? 'check-circle' : 'x-circle'}}" class="w-5 h-5 flex-shrink-0 mt-0.5"></i><div class="flex-1 space-y-2"><p class="font-bold">${{ok ? '<span class="lang-ar">صحيح!</span><span class="lang-en">Correct!</span>' : '<span class="lang-ar">إجابة خاطئة</span><span class="lang-en">Incorrect</span>'}}</p><p class="text-sm leading-relaxed">${{q.explanation}}</p>${{q.wrongExplanations ? `<div class="text-sm space-y-1 pt-2 border-t border-current/10">${{q.wrongExplanations.map((e, i) => e ? `<p><strong>${{String.fromCharCode(65+i)}})</strong> ${{e}}</p>` : '').join('')}}</div>` : ''}}${{q.reference ? `<p class="text-xs text-current/70 pt-1"><i data-lucide="book-open" class="inline w-3 h-3"></i> <span class="lang-ar">راجع:</span><span class="lang-en">Review:</span> ${{q.reference}}</p>` : ''}}</div></div>`;
        }} else {{
          const sbtn = document.createElement('button');
          sbtn.type = 'button';
          sbtn.className = 'px-5 py-2 bg-brand-600 hover:bg-brand-700 disabled:bg-surface-300 disabled:cursor-not-allowed text-white text-sm font-semibold rounded-xl transition-all';
          sbtn.innerHTML = '<span class="lang-ar">تحقّق من الإجابة</span><span class="lang-en">Check Answer</span>';
          sbtn.disabled = sel === undefined || (isMulti && (!sel || sel.length === 0));
          sbtn.onclick = () => this.reveal(q, card);
          card.appendChild(sbtn);
        }}
        return card;
      }},
      selectOpt(q, oIdx, card) {{
        if (q.type === 'multi') {{
          if (!this.answers[q.id]) this.answers[q.id] = [];
          const a = this.answers[q.id]; const p = a.indexOf(oIdx);
          if (p >= 0) a.splice(p, 1); else a.push(oIdx);
        }} else {{ this.answers[q.id] = oIdx; }}
        const newCard = this.renderQ(q, this.questions.indexOf(q));
        card.replaceWith(newCard); if (window.lucide) lucide.createIcons();
      }},
      reveal(q, card) {{ this.revealed[q.id] = true; const newCard = this.renderQ(q, this.questions.indexOf(q)); card.replaceWith(newCard); if (window.lucide) lucide.createIcons(); this.checkAll(); }},
      isCorrect(q) {{
        const a = this.answers[q.id]; if (a === undefined) return false;
        if (q.type === 'multi') {{
          if (!Array.isArray(a) || !Array.isArray(q.correct)) return false;
          if (a.length !== q.correct.length) return false;
          return a.every(x => q.correct.includes(x));
        }}
        return a === q.correct;
      }},
      checkAll() {{
        const done = this.questions.filter(q => this.revealed[q.id]).length;
        if (done === this.questions.length) {{
          const score = this.questions.filter(q => this.isCorrect(q)).length;
          saveQuizResult(this.currentChapter, score, this.questions.length);
          this.renderResult(score, this.questions.length);
        }}
      }},
      renderResult(score, total) {{
        const el = document.getElementById('quiz-final-result'); if (!el) return;
        const pct = Math.round(score/total*100);
        let tone, tAr, tEn, aAr, aEn, icon;
        if (pct >= 80) {{ tone='from-emerald-500 to-emerald-600'; icon='🏆'; tAr='ممتاز!'; tEn='Excellent!'; aAr='فاهم الموضوع كويس. راجع الأسئلة الخاطئة وانتقل للشابتر التالي.'; aEn='Mastered. Review wrong answers and move on.'; }}
        else if (pct >= 60) {{ tone='from-amber-500 to-amber-600'; icon='📚'; tAr='جيّد — يحتاج مراجعة'; tEn='Good — needs review'; aAr='في تفاصيل ضايعة. راجع الأقسام المرتبطة بالأسئلة الخاطئة.'; aEn='Review the sections tied to wrong answers.'; }}
        else {{ tone='from-red-500 to-red-600'; icon='🔁'; tAr='أعد الدراسة'; tEn='Restudy recommended'; aAr='الشابتر يحتاج قراءة ثانية.'; aEn='Needs a second read.'; }}
        el.classList.remove('hidden');
        el.innerHTML = `<div class="bg-gradient-to-br ${{tone}} text-white rounded-2xl p-8 space-y-4 shadow-lg"><div class="flex items-center justify-between"><div><p class="text-white/80 text-sm font-medium"><span class="lang-ar">نتيجتك</span><span class="lang-en">Your score</span></p><p class="text-4xl font-bold mt-1">${{score}}/${{total}} <span class="text-2xl font-normal text-white/80">(${{pct}}%)</span></p></div><div class="text-5xl">${{icon}}</div></div><h3 class="text-2xl font-bold"><span class="lang-ar">${{tAr}}</span><span class="lang-en">${{tEn}}</span></h3><p class="text-white/90 leading-relaxed"><span class="lang-ar">${{aAr}}</span><span class="lang-en">${{aEn}}</span></p><div class="flex flex-wrap gap-2 pt-2"><button onclick="QuizEngine.retake()" class="px-4 py-2 bg-white text-surface-800 rounded-xl text-sm font-semibold hover:bg-white/90 transition-all flex items-center gap-2"><i data-lucide="rotate-ccw" class="w-4 h-4"></i><span class="lang-ar">إعادة الكويز</span><span class="lang-en">Retake</span></button><button onclick="QuizEngine.toggleWrong()" class="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-xl text-sm font-semibold transition-all flex items-center gap-2"><i data-lucide="filter" class="w-4 h-4"></i><span class="lang-ar">راجع الخاطئة فقط</span><span class="lang-en">Review wrong only</span></button></div></div>`;
        if (window.lucide) lucide.createIcons();
        el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
      }},
      retake() {{ this.answers = {{}}; this.revealed = {{}}; this.wrongOnly = false; const el = document.getElementById('quiz-final-result'); if (el) el.classList.add('hidden'); this.render(); document.getElementById('quiz-container')?.scrollIntoView({{ behavior: 'smooth' }}); }},
      toggleWrong() {{ this.wrongOnly = !this.wrongOnly; this.render(); }},
    }};

    const QUESTIONS = [
      {quiz_js}
    ];

    document.addEventListener('DOMContentLoaded', () => {{
      setLang(getLang());
      document.querySelectorAll('[data-lang-toggle]').forEach(b => b.addEventListener('click', toggleLang));
      QuizEngine.init({ch_n}, QUESTIONS);
      if (isChapterComplete({ch_n})) {{
        const b = document.getElementById('complete-btn');
        if (b) {{
          b.querySelector('.btn-label').innerHTML = '<span class="lang-ar">مكتمل ✓</span><span class="lang-en">Completed ✓</span>';
          b.classList.remove('bg-brand-600', 'hover:bg-brand-700');
          b.classList.add('bg-emerald-600', 'hover:bg-emerald-700');
        }}
      }}
      if (window.lucide) lucide.createIcons();
      if (window.Prism) Prism.highlightAll();
    }});
  </script>
</body>
</html>"""


def generate(spec_path: str, output_dir: str = "chapters"):
    """Load a chapter spec from JSON and write the HTML file."""
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)
    html_content = render_chapter(spec)
    ch_id = str(spec["n"]).zfill(2)
    out_path = Path(output_dir) / f"ch{ch_id}.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_content, encoding="utf-8")
    print(f"✓ Generated {out_path} ({len(html_content):,} bytes)")
    return out_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python gen_chapter.py <spec.json> [output_dir]")
        sys.exit(1)
    spec_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "chapters"
    generate(spec_path, output_dir)
