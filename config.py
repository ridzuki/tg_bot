import dotenv
import os

dotenv.load_dotenv()

TG_TOKEN = os.getenv('TG_TOKEN')
AI_TOKEN = os.getenv('AI_TOKEN')
ADMIN_ID= os.getenv('ADMIN_ID')