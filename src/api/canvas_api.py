import requests
import json
from utils.data_transformer import canva_courses_with_grade, canvas_course_assignments, canvas_course_modules_and_files


class CanvasLMSAPI:
    def __init__(self, api_token, base_url):
        self.api_token = api_token
        self.base_url = base_url
        self.courses = []
        self.__init_course()


    def __init_course(self):
        path = "courses"
        params = {
            "enrollment_state": "active",
            "include": ["term"],
            "per_page": 10
        }
        courses = self.__canvas_api_request(path, params_additions=params, reason="init")
        for course in courses:
            self.courses.append({"name": course["name"], "id": course["id"], "course_code": course["course_code"]})
        # print(self.courses)


    def __canvas_api_request(self, url_path, params_additions=0, reason="data"):
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        params = {
            "user_id": "self"
        }
        if params_additions:
            params.update(params_additions)
        full_path = f'{self.base_url}/{url_path}'
        try:
            if reason != "init":
                print(f"Fetching {reason} from Canvas...")
            response = requests.get(full_path, headers=headers, params=params)
            # Check if request was successful
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"Error: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return None


    def __get_canvas_courses(self):
        path = "courses"
        params = {
            "enrollment_state": "active",
            "include": ["term", "total_scores"],
            "per_page": 10
        }
        courses = self.__canvas_api_request(path, params_additions=params, reason=path)
        for course in courses:
            # if course["id"] not in self.courses and course["name"] not in self.courses:
            self.courses.append({"name": course["name"], "id": course["id"]})
        return courses


    def __get_course_assignments(self, course_id):
        path = f"courses/{course_id}/assignments"
        params = {
            "order_by": "due_at",
            "bucket": "future"
        }
        assignments = self.__canvas_api_request(path, params_additions=params, reason="assignments")
        return assignments


    def __get_course_files(self, course_id):
        path = f"courses/{course_id}/modules"
        params = {
            "include": "items"
        }
        modules = self.__canvas_api_request(path,params_additions=params, reason="files")
        return modules

    # def get_announcements(self):
    #     path = "announcements"
    #     # ids = []
    #     # for c_id in self.courses:
    #     #     ids.append(c_id["course_code"])
    #     # print(ids)
    #     params = {
    #         "context_codes[]": "12408.202610"
    #     }
    #     annoucements = self.__canvas_api_request(url_path=path, reason=path, params_additions=params)
    #     return annoucements

    def all_courses_and_grades(self):
        return canva_courses_with_grade(self.__get_canvas_courses())


    def all_assignments(self):
        all_assignments = []
        for course in self.courses:
            cleaned_assignments = canvas_course_assignments(self.__get_course_assignments(course["id"]), course["name"])
            all_assignments.append(cleaned_assignments)
        return all_assignments


    def all_files(self):
        all_files = []
        for course in self.courses:
            cleaned_files = canvas_course_modules_and_files(self.__get_course_files(course["id"]), course["name"])
            all_files.append(cleaned_files)
        return all_files

