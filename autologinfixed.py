import requests

class AutoLogin:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    def login(self, email, password):
        login_url = f"{self.base_url}/login"
        payload = {"email": email, "password": password}

        try:
            response = self.session.post(login_url, json=payload)

            # Check if response is JSON
            try:
                data = response.json()
            except ValueError:
                print("Login failed. Server did not return JSON.")
                print("Status Code:", response.status_code)
                print("Response Text:", response.text)
                return None

            if response.status_code == 200:
                print("Login successful.")
                return data
            else:
                print(f"Login failed with status {response.status_code}: {data}")
                return None

        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None
