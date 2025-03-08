import os
import sys

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from loguru import logger

logger.remove(0)
logger.add(sys.stderr, colorize=True, format="<green>{time:MMMM-D-YYYY}</green> | <black>{time:HH:mm:ss}</black> | <level>{level}</level> | <cyan>{message}</cyan> | <magenta>{name}:{function}:{line}</magenta> | <yellow>{extra}</yellow>")

# Load environment variables from .env file
load_dotenv()

# Access environment variables
logger.info("Loading environment variables")
APP_NAME: str = os.environ.get('APP_NAME')
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
logger.info("Loaded environment variables")

logger.debug("Initializing conversational llm")
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
logger.debug("Initialized conversational llm")

unprotected_routes: set = {
    "/health"
}

common_routes: set = set()
callback_routes: set = set()
admin_routes: set = set()