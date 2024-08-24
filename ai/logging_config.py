import logging
import sys

def setup_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler("../ai/logs/poker_ai.log", mode='a')
                        ])

    # Disable automatic flushing for performance
    logging.getLogger().handlers[0].flush = lambda: None
    logging.getLogger().setLevel(logging.INFO)
