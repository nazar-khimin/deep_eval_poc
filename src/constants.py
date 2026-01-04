"""Contains test environment constants and configuration."""

import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup logger
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Constants:
    """This class contains test environment constants."""

    # API Keys
    OPENAI_API_KEY: str = os.environ["OPENAI_API_KEY"]


# Create singleton instance
const = Constants()
