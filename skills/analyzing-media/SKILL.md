---
name: analyzing-media
description: Analyzes PDFs, images, screenshots, diagrams, and documents using Gemini multimodal. Extracts text, tables, forms; interprets visuals, architecture diagrams, flowcharts, ERDs. Use when user mentions PDFs, images, screenshots, document extraction, OCR, visual analysis, diagram interpretation, or form processing. Do not use for web searching or shell commands.
allowed-tools: Task
---

# Gemini Media Analysis

Spawn the **gemini-media-analyst** agent for image and PDF analysis.

```
Task(subagent_type="gemini-media-analyst", prompt="Analyze @<file-path>: <what to look for>")
```

Use for screenshots, architecture diagrams, PDFs, flowcharts, or any visual content analysis.
