import logging
import sys

def setup_logging():

    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makdirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, 'poker_ai.log')

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler("./ai/logs/poker_ai.log", mode='a')
                        ])

    # Disable automatic flushing for performance
    logging.getLogger().handlers[0].flush = lambda: None
    logging.getLogger().setLevel(logging.INFO)

    logging.info("Logging session Started")