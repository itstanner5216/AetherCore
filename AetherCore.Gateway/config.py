"""
Configuration Management for AetherCore Gateway

Loads configuration from environment variables and config files.
Handles secrets, API keys, and runtime settings.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class Config:
    """
    Central configuration management for gateway

    Loads from:
    1. Environment variables (highest priority)
    2. .env file
    3. Default values (lowest priority)
    """

    def __init__(self):
        """Initialize configuration from environment"""

        # Load environment variables
        self._load_env_file()

        # Core settings
        self.environment = os.getenv("ENVIRONMENT", "production")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.port = int(os.getenv("PORT", "8000"))
        self.host = os.getenv("HOST", "0.0.0.0")

        # API Keys
        self.api_keys = self._load_api_keys()

        # Skills configuration
        self.skills_config_path = os.getenv(
            "SKILLS_CONFIG_PATH", "../AetherCore.System/skills_config.json"
        )

        # Rate limiting
        self.rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # seconds

        # CORS settings
        self.cors_origins = os.getenv(
            "CORS_ORIGINS", "https://chat.openai.com,https://chatgpt.com"
        ).split(",")

        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

        # OAuth (placeholder for future)
        self.oauth_client_id = os.getenv("OAUTH_CLIENT_ID", "")
        self.oauth_client_secret = os.getenv("OAUTH_CLIENT_SECRET", "")

        # External services
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")

        # Search providers
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID", "")
        self.brave_api = os.getenv("BRAVE_API", "")
        self.serper_api_key = os.getenv("SERPER_API_KEY", "")

        # Scrape providers
        self.webscraping_api_key = os.getenv("WEBSCRAPING_API_KEY", "")
        self.scrapingant_api_key = os.getenv("SCRAPINGANT_API_KEY", "")

        # Validate configuration
        self._validate()

    def _load_env_file(self):
        """Load environment variables from .env file"""
        env_path = Path(".env")
        if not env_path.exists():
            return

        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    try:
                        key, value = line.split("=", 1)
                        # Only set if not already in environment
                        if key not in os.environ:
                            os.environ[key] = value
                    except ValueError:
                        logger.warning(f"Invalid .env line: {line}")

    def _load_api_keys(self) -> List[str]:
        """
        Load API keys from environment

        Supports:
        - Single key: API_KEY=key123
        - Multiple keys: API_KEYS=key1,key2,key3
        - JSON array: API_KEYS_JSON=["key1","key2"]
        """
        keys = []

        # Single key
        single_key = os.getenv("API_KEY")
        if single_key:
            keys.append(single_key)

        # Multiple keys (comma-separated)
        multi_keys = os.getenv("API_KEYS")
        if multi_keys:
            keys.extend([k.strip() for k in multi_keys.split(",") if k.strip()])

        # JSON array
        json_keys = os.getenv("API_KEYS_JSON")
        if json_keys:
            try:
                keys.extend(json.loads(json_keys))
            except json.JSONDecodeError:
                logger.error("Invalid JSON in API_KEYS_JSON")

        if not keys:
            logger.warning("No API keys configured - authentication disabled!")

        return keys

    def _validate(self):
        """Validate critical configuration"""

        if self.environment == "production":
            if not self.api_keys:
                logger.error("PRODUCTION: No API keys configured!")

            if self.debug:
                logger.warning("PRODUCTION: Debug mode enabled (not recommended)")

        # Check skills config exists
        if not Path(self.skills_config_path).exists():
            logger.error(f"Skills config not found: {self.skills_config_path}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Export configuration as dictionary (safe for logging)

        Returns:
            Configuration dict with secrets redacted
        """
        return {
            "environment": self.environment,
            "debug": self.debug,
            "port": self.port,
            "host": self.host,
            "api_keys_count": len(self.api_keys),
            "skills_config_path": self.skills_config_path,
            "rate_limit_requests": self.rate_limit_requests,
            "rate_limit_window": self.rate_limit_window,
            "cors_origins": self.cors_origins,
            "log_level": self.log_level,
            "oauth_configured": bool(self.oauth_client_id and self.oauth_client_secret),
            "gemini_configured": bool(self.gemini_api_key),
        }

    def __repr__(self) -> str:
        """String representation of config"""
        return f"Config(environment={self.environment}, debug={self.debug})"


# Singleton instance
_config_instance = None


def get_config() -> Config:
    """
    Get global configuration instance

    Returns:
        Config singleton
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
