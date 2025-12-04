import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_study_tips(course_name, assignments, modules):
    model = genai.GenerativeModel('gemini-2.5-flash')

    current_date = datetime.now().strftime("%Y-%m-%d")

    course_context = {
        "course_name": course_name,
        "current_date": current_date,
        "assignments": [],
        "modules": []
    }

    if assignments:
        for a in assignments:
            course_context["assignments"].append({
                "title": a.get('assignment_name', 'Unknown'),
                "due_date": a.get('due_at', 'No Date')
            })

    if modules:
        for module in modules:
            mod_data = {
                "module_title": module.get("module_name", "General Module"),
                "files": []
            }
            for f in module.get("files", []):
                mod_data["files"].append(f.get("name", "Untitled File"))

            course_context["modules"].append(mod_data)

    context_json_str = json.dumps(course_context, indent=2)

    prompt = (
        f"You are a helpful tutor. I am giving you course data in JSON. **Today is {current_date}.**\n\n"
        f"Please provide a **short, concise response** (max 150 words) that includes:\n"
        f"1. **The Focus:** Identify the next upcoming assignment.\n"
        f"2. **Tutor Tip:** Give ONE key conceptual tip or insight related to that assignment's topic.\n"
        f"3. **Prep Strategy:** Bullet point 2-3 specific files or modules to review right now to be ready for it.\n\n"
        f"Do not lecture. Go straight to the advice.\n\n"
        f"Data:\n```json\n{context_json_str}\n```"
    )

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error contacting Gemini: {str(e)}"
