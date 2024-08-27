import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)
os.makedirs("log", exist_ok=True)
logging.basicConfig(filename="log/api.log", encoding="utf-8", level=logging.DEBUG)

logger.info(f"Server started at {datetime.now()}")
