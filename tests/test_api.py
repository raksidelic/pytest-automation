# tests/test_api.py:

import pytest
import allure
from utilities.api_client import APIClient

# Using JSONPlaceholder instead of Reqres as it is more stable
API_BASE_URL = "https://jsonplaceholder.typicode.com"

@allure.feature("API Test Scenarios")
class TestAPI:

    def setup_method(self):
        # Initialize Client before each test
        self.client = APIClient(API_BASE_URL)

    @allure.story("Fetch User List (GET)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_users(self):
        with allure.step("Sending GET /users request"):
            response = self.client.get("/users")
        
        with allure.step("Status Code and Data Verification"):
            assert response.status_code == 200
            data = response.json()
            
            # JSONPlaceholder returns a list directly, not inside a 'data' object
            assert isinstance(data, list), "API did not return a list!"
            assert len(data) > 0, "User list is empty!"
            
            # Email check for the first user
            assert "@" in data[0]["email"]
            print(f"\n[API SUCCESS] User fetched: {data[0]['name']}")

    @allure.story("Create New Post (POST)")
    @pytest.mark.parametrize("title, body, userId", [
        ("Company Test", "QA Lead Task", 1),
        ("Python Automation", "API Testing", 1)
    ])
    def test_create_post(self, title, body, userId):
        payload = {
            "title": title,
            "body": body,
            "userId": userId
        }
        
        with allure.step(f"Sending POST /posts request (Title: {title})"):
            # JSONPlaceholder uses /posts endpoint for POST
            response = self.client.post("/posts", payload)
        
        with allure.step("Verifying created data"):
            # Successful creation code is 201
            assert response.status_code == 201
            json_response = response.json()
            
            # Did the same data we sent return?
            assert json_response["title"] == title
            assert json_response["body"] == body
            assert json_response["userId"] == userId
            assert "id" in json_response
            print(f"\n[API SUCCESS] Post created ID: {json_response['id']}")