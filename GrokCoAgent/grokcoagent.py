import uno
import unohelper
from com.sun.star.task import XJobExecutor
import json
import urllib.request
import urllib.error

# ================== CONFIG ==================
# Get your free xAI API key at https://x.ai/api (or console.x.ai)
API_KEY = "YOUR_XAI_API_KEY_HERE"   # ← CHANGE THIS
MODEL = "grok-beta"                 # or "grok-4" / latest available in 2026
API_URL = "https://api.x.ai/v1/chat/completions"

# Simple system prompt for agentic + co-creation behavior
SYSTEM_PROMPT = """You are GrokCoAgent, an autonomous AI agent inside LibreOffice.
You help with workflow automation and co-creation across Writer, Calc, Impress, Draw.
- Read the provided document context and user goal.
- Think step-by-step (ReAct style: Thought → Action → Observation).
- If needed, suggest or directly output the exact change (text, table, formula, slide layout).
- Always preserve formatting when possible.
- Return ONLY the final action/result in JSON: {"thought": "...", "action": "insert|replace|create_table|...", "content": "..."}"""

# ===========================================

g_ImplementationHelper = unohelper.ImplementationHelper()

class GrokCoAgentJob(unohelper.Base, XJobExecutor):
    def __init__(self, ctx):
        self.ctx = ctx

    def _call_grok(self, user_prompt, context=""):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context (current document):\n{context}\n\nUser goal: {user_prompt}"}
        ]
        data = {
            "model": MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2048
        }
        req = urllib.request.Request(
            API_URL,
            data=json.dumps(data).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"ERROR: {str(e)}"

    def trigger(self, args):
        # Get current document
        desktop = self.ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", self.ctx)
        model = desktop.getCurrentComponent()
        if not model:
            # Fallback: open Writer
            model = desktop.loadComponentFromURL("private:factory/swriter", "_blank", 0, ())

        # Extract context based on component type
        component = model.getImplementationName()
        context = ""
        selection = ""

        if "Writer" in component or "TextDocument" in component:
            text = model.Text
            cursor = model.getCurrentController().getSelection().getByIndex(0)
            if cursor:
                selection = cursor.getString()
            context = selection or text.getString()[:2000]  # first 2000 chars

        elif "Calc" in component or "SpreadsheetDocument" in component:
            sheet = model.getCurrentController().getActiveSheet()
            selection = sheet.getSelection()
            if selection:
                context = "Selected cells data (CSV-like):\n" + "\n".join([str(cell) for cell in selection])[:2000]

        elif "Impress" in component or "PresentationDocument" in component:
            context = "Current slide/presentation mode - generate content or layout"

        else:
            context = "Unknown component - general assistance"

        # Get user goal (simple input via msgbox + fallback)
        from com.sun.star.awt import MessageBoxType, MessageBoxButtons
        parent = desktop.getCurrentFrame().getContainerWindow()
        box = self.ctx.ServiceManager.createInstanceWithContext("com.sun.star.awt.Toolkit", self.ctx).createMessageBox(
            parent, MessageBoxType.MESSAGEBOX, MessageBoxButtons.BUTTONS_OK_CANCEL, "GrokCoAgent",
            "Enter your goal / prompt (e.g. 'Summarize this', 'Create quarterly report table', 'Make 5-slide pitch from notes'):"
        )
        result = box.execute()
        if result != 1:  # OK button
            return
        user_prompt = box.getTitle()  # placeholder; in real extensions use a proper dialog

        # For demo we use a simple prompt; you can replace with a real XDialog later
        user_prompt = input("Enter your AI goal: ") if "__name__" == "__main__" else "Automate workflow: " + (selection or "co-create document")

        # Call Grok (agentic reasoning)
        response = self._call_grok(user_prompt, context)
        print("Grok raw response:", response)  # debug

        try:
            action = json.loads(response)
        except:
            # Fallback if not perfect JSON
            action = {"thought": "Parsed response", "action": "insert", "content": response}

        # Execute the action across suite
        if "Writer" in component or "TextDocument" in component:
            text = model.Text
            cursor = model.getCurrentController().getSelection().getByIndex(0) or text.createTextCursor()
            if action.get("action") == "replace" or selection:
                cursor.setString(action["content"])
            else:
                text.insertString(cursor, "\n\n" + action["content"] + "\n", False)

        elif "Calc" in component or "SpreadsheetDocument" in component:
            # Example: insert table or formula
            sheet = model.getCurrentController().getActiveSheet()
            cell = sheet.getCellByPosition(0, 0)
            cell.setString(action["content"])

        elif "Impress" in component or "PresentationDocument" in component:
            # Placeholder: insert text into current slide
            pass  # extend as needed

        # Feedback
        msg = self.ctx.ServiceManager.createInstanceWithContext("com.sun.star.awt.Toolkit", self.ctx).createMessageBox(
            parent, MessageBoxType.INFOBOX, MessageBoxButtons.BUTTONS_OK,
            "GrokCoAgent", f"✅ Done!\nThought: {action.get('thought','')}\nAction applied."
        )
        msg.execute()

# Registration
g_ImplementationHelper.addImplementation(
    GrokCoAgentJob,
    "org.grokcoagent.main.GrokCoAgentJob",
    ("com.sun.star.task.Job",),
)

# Debugging main()
def main():
    ctx = uno.getComponentContext() if hasattr(uno, "getComponentContext") else None
    if not ctx:
        import officehelper
        ctx = officehelper.bootstrap()
    job = GrokCoAgentJob(ctx)
    job.trigger("")

if __name__ == "__main__":
    main()
