import pandas as pd
import random
from datetime import datetime, timedelta
from credit_card_tokenisation.src.logger_config import setup_logger
import warnings
from tqdm import tqdm

tqdm.pandas()
warnings.filterwarnings('ignore')
logger = setup_logger(__name__)

def create_data_to_be_tokenised(sample_size):
    """ The module is used to generate dummy data for use in the tokenisation program demonstration.
        It generates: policy id's, credit card numbers and expiration dates, and converts the information from a
        dictionary to a dataframe which is then used for processing.
    """
    logger.info(f'******** : Create Sample Data : ********')
    sample = sample_size
    records = generate_bulk(sample)
    cc_numbers_to_tokenise = pd.DataFrame(records)
    logger.debug(f'Total Records Generated: {len(cc_numbers_to_tokenise)}')
    logger.debug(cc_numbers_to_tokenise.head(10))
    return cc_numbers_to_tokenise

def generate_policy_id():
    """Generate a random 9-digit policy ID."""
    return ''.join(random.choices('0123456789', k=9))

def generate_credit_card_number():
    """Generate a random credit card number (14–16 digits)."""
    length = random.choice([14, 15, 16])
    return ''.join(random.choices('0123456789', k=length))

def generate_expiration_date():
    """Generate a future expiration date in MM/YY format (within 5 years)."""
    today = datetime.today()
    future_date = today + timedelta(days=random.randint(365, 5 * 365))
    return future_date.strftime("%m/%y")

def generate_bulk(count=1000):
    """Generate a list of dictionaries with policy ID, credit card number, and expiration date."""
    return [
        {
            'policy_id': generate_policy_id(),
            'credit_card_number': generate_credit_card_number(),
            'expiration_date': generate_expiration_date()
        }
        for _ in range(count)
    ]
