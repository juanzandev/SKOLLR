#!/usr/bin/env python3
"""Test script to debug Canvas data loading"""

from src.api.canvas_api import CanvasLMSAPI
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))


api_token = os.environ.get("CANVAS_API_TOKEN")
api_base_url = f'{os.getenv("CANVAS_BASE_URL", "")}/api/v1'

print(f"[TEST] API Token: {'*' * 20}...")
print(f"[TEST] Base URL: {api_base_url}")
print()

try:
    print("[TEST] Initializing Canvas API...")
    canvas_api = CanvasLMSAPI(api_token=api_token, base_url=api_base_url)

    print("[TEST] Fetching courses and grades...")
    courses = canvas_api.all_courses_and_grades()
    print(f"[TEST] Got {len(courses)} courses")
    print()

    print("[TEST] Result:")
    for course in courses:
        print(f"  - {course}")

except Exception as e:
    import traceback
    print(f"[ERROR] {e}")
    print("[TRACEBACK]")
    traceback.print_exc()
