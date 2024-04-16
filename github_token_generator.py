import github
import requests
import jwt
import time
from interfaces.token_generator import ITokenGenerator
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from loguru import logger


class GitHubTokenGenerator(ITokenGenerator):
    def __init__(self, app_id: str, app_pem: str):
        self.app_id = app_id
        self.app_pem = app_pem

    # def get_jwt(self):
    #     f = open(self.app_pem, "rb")
    #     signing_key = serialization.load_pem_private_key(
    #         bytes(f.read()), password=None, backend=default_backend()
    #     )
    #     payload = {"iat": int(time.time()), "exp": int(time.time()) + 600, "iss": 402740}
    #     return jwt.encode(payload, signing_key, algorithm="RS256")
    def get_jwt(self):
        try:
            with open(self.app_pem, "rb") as f:
                
                signing_key = serialization.load_pem_private_key(
                    f.read(), password=None, backend=default_backend()
                )
                print(signing_key)
            payload = {
                # Issued at time
                'iat': int(time.time()),
                # JWT expiration time (10 minutes maximum)
                'exp': int(time.time()) + 600,
                # GitHub App's identifier
                'iss': 877572
            }

    
            encoded_jwt = jwt.encode(payload, signing_key, algorithm='RS256')
            return encoded_jwt
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_token(self, access_token_url: str, installation_id: str = None):
        for timeout in [5.5, 5.5, 10.5]:
            try:
                installation_id = 49653476
                jwt_token = self.get_jwt()
              
                headers = {
                    "Accept": "application/vnd.github+json",
                    "Authorization": "Bearer " + jwt_token,
                    "X-GitHub-Api-Version": "2022-11-28",
                }
                access_token_url = "https://api.github.com/app/installations/49653476/access_tokens"
                print(headers)
                response = requests.post(
                    access_token_url,
                    headers=headers,
                )
                obj = response.json()
                logger.info(f"jwt: {jwt_token}, token_res: {obj}")
                if "token" not in obj:
                    raise Exception("Could not get token")
                return obj["token"]
            except SystemExit:
                raise SystemExit
            except Exception as e:
                time.sleep(timeout)
        raise Exception(
            "Could not get token, please double check your PRIVATE_KEY and GITHUB_APP_ID in the .env file. Make sure "
            "to restart uvicorn after.")
