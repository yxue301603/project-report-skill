"""Validate public skill metadata and required package files."""
from pathlib import Path
import re
import yaml

root = Path(__file__).resolve().parents[1]
skill = root / 'skills' / 'project-report'
text = (skill / 'SKILL.md').read_text(encoding='utf-8')
front = re.match(r'^---\n(.*?)\n---\n', text, re.S)
assert front, 'Missing YAML frontmatter'
meta = yaml.safe_load(front[1])
assert meta['name'] == skill.name
assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', meta['name'])
assert len(meta['name']) <= 64
assert isinstance(meta['description'], str) and 0 < len(meta['description']) <= 1024
assert meta['license'] == 'MIT'
assert all(isinstance(k,str) and isinstance(v,str) for k,v in meta['metadata'].items())
assert len(text.splitlines()) < 500
for relative in ['README.md','README.zh-CN.md','LICENSE','CONTRIBUTING.md','CODE_OF_CONDUCT.md','SECURITY.md','.github/workflows/ci.yml','.github/PULL_REQUEST_TEMPLATE.md']:
    assert (root / relative).is_file(), relative
for relative in ['assets/example.md','assets/report.html','scripts/render_report.py','references/format.md','agents/openai.yaml','LICENSE']:
    assert (skill / relative).is_file(), relative
assert not (skill / 'assets/reference.html').exists(), 'Do not publish private reference reports'
for path in (root / '.github/ISSUE_TEMPLATE').glob('*.md'):
    form = yaml.safe_load(path.read_text(encoding='utf-8').split('---')[1])
    assert form.get('name') and form.get('about'), path.name
print('Skill metadata and community package checks passed.')
