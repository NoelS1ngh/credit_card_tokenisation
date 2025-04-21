import pyffx
from logger_config import setup_logger
import warnings
from tqdm import tqdm
import pandas as pd

tqdm.pandas()
warnings.filterwarnings('ignore')
logger = setup_logger(__name__)

def format_preserving_encryption_tokenisation(cc_numbers_to_tokenise: pd.DataFrame, fpe_key: str) -> pd.DataFrame:
    '''FPE Encryption:     Format-Preserving Encryption (FPE) is a class of encryption algorithms where the ciphertext has the same format as the plaintext.
    ✅ Tokenization with reversibility
    ✅ Keeps legacy systems happy (they expect data of certain lengths/formats)
    ✅ No schema changes needed in databases (because formats don’t change)
    ✅ PCI compliance friendliness (often used in credit card/token vaults)

    FPE encrypts data while respecting a specific format using standard block ciphers like AES under the hood — it wraps these in special constructions like:
    FF1 / FF3: NIST-approved algorithms for FPE over strings/numbers
    Feistel networks: for splitting and recombining data in predictable formats
    '''
    fpe = pyffx.String(fpe_key, alphabet='0123456789', length=20)
    cc_numbers_to_tokenise['fpe_token'] = cc_numbers_to_tokenise['clean_credit_card_number'].apply(lambda x: fpe.encrypt(x.zfill(20)))
    logger.debug(cc_numbers_to_tokenise[['credit_card_number','clean_credit_card_number','fpe_token']].head(10))
    return cc_numbers_to_tokenise