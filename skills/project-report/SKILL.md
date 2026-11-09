---
name: project-report
description: Create or update project reports, research summaries, and experiment reviews as editable Markdown plus offline HTML with charts. Also use for 项目报告、调研报告、实验总结、阶段复盘. Excludes ordinary chat replies and tasks explicitly requesting other formats.
license: MIT
metadata:
  runtime: "Python 3.10+ and markdown-it-py >=3,<5"
---

# 双格式项目报告

以 `.md` 为正文和数据的唯一主稿，用本 Skill 的脚本生成同名 `.html`。用户明确指定格式时优先遵从。不要生成 Word，也不要分别编写两份正文。

## 工作方式

1. 阅读用户资料及已有主稿。报告先给主要结论，再提供数据、分析、限制与建议；章节按任务调整，不照搬参考报告的技术内容。
2. 阅读 [格式约定](references/format.md)。使用普通 Markdown 标题、列表、代码和表格；关键指标采用标记表格，重点采用提示引用。图表引用 MD 表格，不复制数值。普通 MD 阅读器仍能读到所有正文和数据。
3. 参考 [示例主稿](assets/example.md) 和 `assets/report.html` 的样式。蓝色表示一般指标，绿色表示有依据的正向结果，橙色表示限制；不要只靠颜色表达结论。按内容选图：类别比较用 bar，有序等间隔观测用 line。无数据就不强行画图。不同测量口径、单位不能混为同一序列。
4. 在项目报告目录保存主稿，执行：

   ```text
   python <本技能目录>/scripts/render_report.py <报告.md>
   ```

   需要 Python 3.10+ 与 `markdown-it-py>=3,<5`。若未安装，使用项目虚拟环境安装 `requirements.txt`，不要假定另一台机器已经配置。HTML 内嵌 CSS、SVG 与主稿下载内容，图表无需联网。外部图片不会被脚本自动打包，离线报告使用本地相对图片并一并交付。
5. 检查生成结果：核对结论与原始数据；在浏览器检查桌面和窄屏布局、图表标签、表格与代码块。未知或缺失数据保留为未知，不填造数值。脚本拒绝无效图表数据时修正主稿，不静默省略图表。
6. 交付 MD 和 HTML 的链接。修改报告时只编辑最新 MD，再重新生成 HTML；保留用户手动修改，不从旧副本覆盖。HTML 页尾含主稿摘要和下载，便于确认对应版本。

## 维护

- 通用视觉改动修改 `assets/report.html`；渲染行为修改 `scripts/render_report.py`；格式变更同步 `references/format.md`。
- 运行 `python <技能目录>/scripts/test_render_report.py` 检查数据同步、图表、错误处理和 HTML 转义。
- `assets/example.md` 使用明确标注的虚构演示数据，不可作为真实项目结论。社区包不包含私人参考报告。
