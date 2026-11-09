# 报告格式

使用 UTF-8 Markdown。第一个一级标题作为页面标题；二、三级标题自动进入目录。支持表格、代码块、嵌套列表、链接、图片、删除线。原始 HTML 作为文本显示，不执行。暂不支持数学公式排版或 Mermaid；需要时扩展脚本，不能声称已渲染。

## 指标卡片

标记紧邻普通表格。前两列是名称与显示值，第三列是说明（可选）。MD 中是表格，HTML 中是卡片。多个卡片自动换行。

```markdown
<!-- report:metrics -->
| 指标 | 数值 | 说明 |
| --- | --- | --- |
| 最终 MFU | 23.46% | 60 迭代长跑 |
| 显存峰值 | 72.1 GB | 8 卡轮询 |
```

## 重点提示

使用 GitHub 风格的引用，支持 NOTE、TIP、IMPORTANT、WARNING、CAUTION。引用里的正文仍是正常 Markdown。

```markdown
> [!IMPORTANT]
> **主要结论：** 最优配置在统一测量协议下得到验证。
```

## 图表与单一数据来源

1. 用 `<!-- report:table 唯一标识 -->` 给紧邻表格命名，标识限英文数字、下划线和连字符。
2. 用 `report-chart` 围栏代码块给出 JSON 配置；可在表格前或后引用。
3. 表格是数据源，图表只保存引用和展示配置。原始数据表仍在 HTML 中完整展示，辅助阅读和核对。

````markdown
<!-- report:table throughput -->
| 阶段 | 吞吐 |
| --- | ---: |
| 基线 | 100 |
| 优化后 | 150 |

```report-chart
{"type":"bar","title":"吞吐对比","table":"throughput","label":"阶段","values":["吞吐"],"unit":"tokens/s"}
```
````

必填：`type`（bar 或 line）、`title`、`table`、`label`、`values`（一个或多个数值列名）。可选 `unit` 为整张图共用单位。不支持其他配置键；拼错会报错。

- bar：横向分组条形图，统一零基线，支持正负数。
- line：一个或多个序列；横轴按表格行等间隔排列，仅用于等间隔观测或明确的有序类别，不用于不等间隔时间／数值横轴。
- 数值支持负号、小数、科学计数、标准千位逗号和百分号。百分号保持百分数显示单位（23.46% 画为 23.46），所有列必须使用相同单位；缺值、NaN、无穷、混合单位字符串如 `72.1 GB` 会报错。单位写在列名或 `unit`。
- 列名必须唯一，引用必须精确匹配；图表标题和来源说明应解释测量口径。多序列用同一量纲。
- SVG 包含标题和悬停数据提示；数据表作为可访问的文字替代。不依赖外部图表 CDN。

## 命令

```text
python scripts/render_report.py report.md
python scripts/render_report.py report.md --output preview.html
python scripts/render_report.py report.md --watch
```

默认同目录、同文件名输出 HTML。`--watch` 每秒检查主稿变化并重新生成，Ctrl+C 停止；浏览器手动刷新即可。生成失败保留旧 HTML 并显示错误。脚本不会修改 MD，不能直接编辑 HTML 后反向同步。

`assets/report.html` 使用 `@@TITLE@@`、`@@BODY@@`、`@@TOC@@`、`@@SOURCE_NAME@@`、`@@SOURCE_B64@@`、`@@SOURCE_HASH@@` 占位符。HTML 自带下载按钮，可下载生成时的 MD 快照；之后主稿改变需要重新生成。
