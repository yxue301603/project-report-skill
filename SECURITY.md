# Security policy

Security fixes target the latest code on the default branch. No response-time guarantee is offered.

Please use the repository's **Security → Report a vulnerability** feature to report sensitive findings privately. Include a minimal reproduction with synthetic data, expected versus actual behavior, affected version or commit, and impact. Do not put credentials, personal information, or exploit details in public issues.

## Relevant boundaries

- Raw HTML is escaped and chart text is encoded. The renderer does not execute scripts embedded in report Markdown.
- Markdown may include remote links or images. Opening the generated HTML can contact the specified image hosts. Review untrusted content before opening it.
- The full Markdown source is embedded for download, including comments. Sharing HTML shares that source too.
- `--output` replaces the selected HTML file after a successful build. Keep input/output paths under your control.
- Very large documents or chart tables may consume substantial CPU, memory, or browser resources. This tool is designed for local authoring, not as a hardened public upload service.
