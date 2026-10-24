from pathlib import Path
import json,re,sys
root=Path(__file__).resolve().parents[1]
errors=[]
for r in ['index.html','assets/style.css','assets/app.js','assets/social-card.svg','assets/favicon.svg','README.md','LICENSE','CONTENT_LICENSE.md','.github/workflows/pages.yml','data/chapters.js','data/routes.js','research/sources.md']:
 if not (root/r).is_file(): errors.append('Missing '+r)
js=(root/'data/chapters.js').read_text(encoding='utf-8')
match=re.search(r'window\.HANDBOOK_CHAPTERS\s*=\s*(\[.*\])\s*;',js,re.S)
if not match:errors.append('Chapter JSON not found')
else:
 data=json.loads(match.group(1))
 if len(data)!=20:errors.append('Expected 20 chapters')
 for i,d in enumerate(data):
  if d['num']!=f'{i:02d}':errors.append('Wrong chapter number')
  if not list((root/'chapters').glob(f'{i:02d}-*.md')):errors.append('Missing markdown chapter '+str(i))
html=(root/'index.html').read_text(encoding='utf-8')
for required in ['id="finder"','id="planner"','id="chapter-dialog"','id="calculator"','AIPMAndy','metaver.vip']:
 if required not in html:errors.append('Missing HTML content '+required)
for x in re.findall(r'(?:src|href)="(\./[^"]+)"',html):
 if not (root/x[2:]).exists():errors.append('Broken local ref '+x)
for a in ['AIPMAndy','https://metaver.vip/']:
 if a not in (root/'README.md').read_text(encoding='utf-8'):errors.append('Missing contact in README')
if errors:
 print('FAILED: '+'\n - '.join(errors));sys.exit(1)
print(f'PASS: {len(data)} chapters, {len(list((root/"templates").iterdir()))} templates, website assets, links, contacts and workflows')
