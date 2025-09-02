from huggingface_hub import HfApi
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("HF_API_KEY")

api = HfApi()
user_info = api.whoami(token=api_key)
print(user_info)

