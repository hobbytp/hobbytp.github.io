import os
from dotenv import load_dotenv

load_dotenv()

class EnvConfig:
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
    GOOGLE_SEARCH_API_KEY = os.getenv('GOOGLE_SEARCH_API_KEY')
    GOOGLE_SEARCH_ENGINE_ID = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
    SERPER_API_KEY = os.getenv('SERPER_API_KEY')
    BRAVE_SEARCH_API_KEY = os.getenv('BRAVE_SEARCH_API_KEY')
    METASOSEARCH_API_KEY = os.getenv('METASOSEARCH_API_KEY')

env_config = EnvConfig()
