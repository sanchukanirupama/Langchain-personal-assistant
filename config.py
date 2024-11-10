# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API keys and other secrets
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ZAPIER_NLA_API_KEY = os.getenv("ZAPIER_NLA_API_KEY")
