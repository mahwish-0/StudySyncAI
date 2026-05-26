import google.generativeai as genai
from django.conf import settings

genai.configure(api_key=getattr(settings, "GEMINI_API_KEY", ""))

def fallback_reply(message):
    msg = message.lower()
    if "stress" in msg:
        return "Take a short break, breathe, then start one small pending task."
    if "exam" in msg:
        return "Focus on nearest deadlines and high-priority tasks first."
    if "focus" in msg:
        return "Use a 25-minute focus session and keep only one subject open."
    return "I can help with study planning, focus, stress, deadlines, and motivation."

def ask_gemini(message, tasks=None):
    try:
        task_context = ""

        if tasks:
            for task in tasks[:8]:
                task_context += (
                    f"Subject: {task.subject}, Hours: {task.hours}, "
                    f"Deadline: {task.deadline}, Priority: {task.priority}, "
                    f"Difficulty: {task.difficulty}, Completed: {task.completed}\\n"
                )

        prompt = f"""
You are StudySync AI Coach.
Use the student's actual tasks to give personalized study advice.

Student tasks:
{task_context}

User message:
{message}

Reply in short, simple, practical points.
"""

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text

    except Exception:
        return fallback_reply(message)
