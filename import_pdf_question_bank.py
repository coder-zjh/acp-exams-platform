import json
import re
import unicodedata
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).parent
PDF = Path('/Users/zjh/Desktop/阿里云大模型ACP认证题库.pdf')


def clean(value: str) -> str:
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', value)).strip()


def key(value: str) -> str:
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', value)).lower()


questions: list[dict] = []
current: dict | None = None
section = 'single'
in_explanation = False
with pdfplumber.open(PDF) as document:
    for page in document.pages:
        for line in page.extract_text_lines():
            text = clean(line['text'])
            if text.startswith(('最后更新', '建议微信扫描', '库更新通知')):
                continue
            if text == '【单选题】':
                section = 'single'
                continue
            if text == '【多选题】':
                section = 'multi'
                continue
            numbered = re.match(r'^(\d+)\.\s*(.*)$', text)
            if numbered:
                if current and not current['options'] and current['text'].endswith(':') and int(numbered.group(1)) <= 3:
                    current['text'] += ' ' + numbered.group(2)
                    continue
                if current:
                    questions.append(current)
                current = {'text': numbered.group(2), 'options': {}, 'section': section}
                in_explanation = False
                continue
            option = re.match(r'^([A-F]):\s*(.*)$', text)
            if option and current:
                option_key = option.group(1)
                bold = any('Bold' in char.get('fontname', '') for char in line['chars'])
                bold = bold or (bool(line['chars']) and 'AAAAAF' in line['chars'][0].get('fontname', ''))
                current['options'][option_key] = {'text': option.group(2), 'correct': bold}
                continue
            if current and text.startswith('解析'):
                in_explanation = True
                continue
            if current and in_explanation:
                continue
            if current and current['options']:
                current['options'][list(current['options'])[-1]]['text'] += ' ' + text
            elif current and text:
                current['text'] += ' ' + text
if current:
    questions.append(current)

seen: set[str] = set()
unique: list[dict] = []
for question in questions:
    question_key = key(question['text'])
    if question_key in seen or not question['options']:
        continue
    seen.add(question_key)
    options = [
        {'key': option_key, 'text': option['text'], 'correct': option['correct']}
        for option_key, option in question['options'].items()
    ]
    answer = ''.join(option['key'] for option in options if option['correct'])
    if not answer:
        raise RuntimeError(f'No bold answer found: {question["text"]}')
    unique.append({'text': question['text'], 'options': options, 'answer': answer, 'section': question['section']})

single = [item for item in unique if item['section'] == 'single']
multi = [item for item in unique if item['section'] == 'multi']
for number, item in enumerate(single, 1):
    item['number'] = number
for number, item in enumerate(multi, 1):
    item['number'] = number
sets = [
    {'id': 'pdf-single', 'title': '阿里云大模型ACP认证题库（单选题）', 'questions': single},
    {'id': 'pdf-multi', 'title': '阿里云大模型ACP认证题库（多选题）', 'questions': multi},
]
(ROOT / 'quiz-data.js').write_text('window.QUIZ_SETS = ' + json.dumps(sets, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')

def sql(value: str) -> str:
    return "'" + value.replace('\\', '\\\\').replace("'", "''") + "'"


seed = ['USE acp_exams_platform;', 'START TRANSACTION;']
for item in unique:
    source_key = 'pdf-single' if item['section'] == 'single' else 'pdf-multi'
    seed.append(
        'INSERT INTO acp_questions (source_key, question_no, section, body, options_json, answer) VALUES '
        f'({sql(source_key)}, {item["number"]}, {sql(item["section"])}, {sql(item["text"])}, '
        f'{sql(json.dumps(item["options"], ensure_ascii=False, separators=(",", ":")))}, {sql(item["answer"])}) '
        'ON DUPLICATE KEY UPDATE body=VALUES(body), options_json=VALUES(options_json), answer=VALUES(answer);'
    )
seed.extend(['COMMIT;', ''])
(ROOT / 'database' / 'mysql-seed.sql').write_text('\n'.join(seed), encoding='utf-8')
print(json.dumps({'source_questions': len(questions), 'unique_questions': len(unique), 'duplicates_removed': len(questions) - len(unique), 'single': len(single), 'multi': len(multi)}, ensure_ascii=False))
