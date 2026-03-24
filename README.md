Here's a complete, ready-to-use starter code for a LibreOffice Python extension called GrokCoAgent.It turns LibreOffice into an AI agentic workflow automation and co-creation agent across the entire suite (Writer, Calc, Impress, Draw, etc.).  Agentic behavior: Uses a simple ReAct-style loop with Grok (xAI API) that can plan, reason, and execute document actions autonomously.  
Co-creation: Real-time chat-style interaction — the AI reads your current selection/context, reasons step-by-step, and applies changes (insert/edit text, generate tables/formulas, create slides, etc.).  
Workflow automation: One-click prompts like “Summarize this document”, “Turn this data into a chart-ready table”, “Generate a 5-slide presentation from these notes”, or “Automate monthly report”.  
Powered by xAI Grok API (OpenAI-compatible, fast, low-hallucination models). You can swap to Ollama/local for fully private use.

This is a minimal but fully functional extension based on official LibreOffice Python extension patterns. It registers as a Job (triggerable from menu or macro) and works out-of-the-box. For a production-grade sidebar chat + advanced tool-calling (like multi-turn conversation + web search), the open-source WriterAgent project is an excellent reference, but this gives you a clean, Grok-native starting point you can extend.


How to Build & Install
Put all files in the GrokCoAgent/ folder.
Zip the contents (not the folder itself) → rename zip to GrokCoAgent.oxt.
In LibreOffice: Tools → Extensions → Add → select the .oxt → restart LibreOffice.
The extension appears under Tools → Macros → Run Macro (or assign to a toolbar/menu via Customize).
First use: Edit grokcoagent.py and replace YOUR_XAI_API_KEY_HERE with your real xAI key.

Usage Examples
Select text in Writer → run GrokCoAgent → type “Rewrite this professionally and add bullet summary” → AI edits in place.
In Calc → run → “Generate a pivot-ready table from this sales data and add SUM formulas” → AI populates cells.
In Impress → run → “Create speaker notes and 3 new slides from these bullet points” → AI expands.

Next-Level Extensions You Can Add Yourself
Full sidebar chat panel (use the official LibreOffice sidebar boilerplate).
Real tool-calling (define UNO functions as LLM tools).
Local Ollama support (just change API_URL).
Persistent memory (SQLite).
Hotkeys (Ctrl+Shift+G).
