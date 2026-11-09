"""Behavioral checks for reusable reports; run with Python unittest."""
import base64
from pathlib import Path
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET

from render_report import ROOT, build, render

TABLE = '''# 测试报告

<!-- report:table data -->
| 阶段 | 数值 | 第二序列 |
| --- | ---: | ---: |
| 基线 | -2 | 0 |
| 优化 | 4 | 8 |

```report-chart
{"type":"bar","title":"结果","table":"data","label":"阶段","values":["数值","第二序列"]}
```
'''


class ReportTests(unittest.TestCase):
    def test_data_sync_and_download(self):
        first=render(TABLE,'测试.md')
        second=render(TABLE.replace('| 优化 | 4 |','| 优化 | 6 |'),'测试.md')
        self.assertIn('优化 · 数值: 6',second)
        self.assertNotEqual(re.findall(r'<rect[^>]+>',first),re.findall(r'<rect[^>]+>',second))
        snapshot=re.search(r'base64,([A-Za-z0-9+/=]+)',first)[1]
        self.assertEqual(base64.b64decode(snapshot).decode(),TABLE)
        self.assertNotIn('<script',first)

    def test_line_and_zero(self):
        for source in [TABLE.replace('"bar"','"line"'),TABLE.replace('| -2 | 0 |','| 0 | 0 |').replace('| 4 | 8 |','| 0 | 0 |')]:
            page=render(source,'test.md')
            svg=re.search(r'<svg.*?</svg>',page,re.S)[0]
            ET.fromstring(svg)
            self.assertNotIn('nan',svg)
            self.assertNotIn('inf',svg)

    def test_invalid_data_and_references(self):
        variants=[TABLE.replace('| -2 |','| — |'),TABLE.replace('"data"','"missing"'),TABLE.replace('"数值","第二序列"','"不存在"'),TABLE.replace('"bar"','"pie"'),TABLE.replace('| -2 |','| NaN |'),TABLE.replace('| -2 |','| 2% |')]
        for source in variants:
            with self.subTest(source=source),self.assertRaises(ValueError):
                render(source,'test.md')

    def test_injection_is_text(self):
        source=TABLE.replace('结果','<script>alert(1)</script>')+'\n<script>alert(2)</script>\n\n[危险](javascript:alert(3))\n'
        page=render(source,'evil".md')
        self.assertNotIn('<script>',page)
        self.assertNotIn('href="javascript:',page)
        self.assertIn('&lt;script&gt;',page)
        self.assertIn('download="evil&quot;.md"',page)

    def test_metrics_callouts_and_markdown(self):
        source='''# 示例

<!-- report:metrics -->
| 指标 | 值 |
| --- | --- |
| 用时 | 12 秒 |

> [!WARNING]
> **注意** 测量口径。

1. 第一项
   - 嵌套项

```python
print("hello")
```
'''
        page=render(source,'test.md')
        for text in ['class="metrics"','callout-warning','<strong>注意</strong>','<ol>','<ul>','language-python']:
            self.assertIn(text,page)

    def test_forward_reference_and_duplicate_id(self):
        before,chart=TABLE.split('```report-chart')
        render('```report-chart'+chart+'\n'+before,'test.md')
        with self.assertRaises(ValueError):
            render(TABLE+'\n'+before,'test.md')

    def test_atomic_output_and_source_preservation(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd(),prefix='report-test-') as tmp:
            src=Path(tmp)/'报告.md'
            dest=src.with_suffix('.html')
            src.write_text(TABLE,encoding='utf-8')
            build(src,dest)
            self.assertEqual(src.read_text(encoding='utf-8'),TABLE)
            old=dest.read_bytes()
            src.write_text(TABLE.replace('| -2 |','| 缺失 |'),encoding='utf-8')
            with self.assertRaises(ValueError):
                build(src,dest)
            self.assertEqual(dest.read_bytes(),old)
            with self.assertRaises(ValueError):
                build(src,src)

    def test_real_example(self):
        page=render((ROOT/'assets/example.md').read_text(encoding='utf-8'),'示例.md')
        self.assertEqual(page.count('<svg '),3)
        self.assertIn('Optimized · Throughput: 160req/s',page)
        self.assertIn('Demonstration only',page)


if __name__=='__main__':
    unittest.main()
