from datetime import datetime
from dotenv import load_dotenv
import os
load_dotenv()
CANVAS_BASE_URL = f'{os.getenv("CANVAS_BASE_URL")}'


def format_time(time):
    if time:
        dt_local = datetime.fromisoformat(time.replace("Z", "+00:00")).astimezone()
        return dt_local.strftime("%b %d, %Y %I:%M %p %Z")
    else:
        return None


def canva_courses_with_grade(courses):
    # print("Cleaning Data...")
    cleaned = []
    for course in courses:
        cleaned.append(
            {
                "course_name": course["name"],
                "current_grade": course["enrollments"][0]["computed_current_grade"],
                "current_percentage": course["enrollments"][0]["computed_current_score"]
            }
        )
    return cleaned


def canvas_course_assignments(assignments, course_name):
    # print("Cleaning Data...")
    cleaned = {"course_name": course_name}
    all_assignments = []
    for assignment in assignments:
        all_assignments.append(
            {
                "assignment_name": assignment["name"],
                "total_points": assignment["points_possible"],
                "due_at": format_time(assignment["due_at"]),
                "url": assignment["html_url"]
            }
        )
    cleaned["assignments"] = all_assignments
    return cleaned


def canvas_course_modules_and_files(modules: list[dict], course_name):
    cleaned = {}
    for module in modules:
        mod_name = module["name"]
        if course_name not in cleaned:
            cleaned[course_name] = []
        files = []

        # Check if 'items' exists and is a list to be safe
        for item in module.get("items", []):
            files.append(
                {
                    "name": item["title"],
                    "type": item["type"],
                    "url": item.get("html_url", "#")
                }
            )
        cleaned[course_name].append({
            "module_name": mod_name,
            "files": files
        })

    return cleaned

