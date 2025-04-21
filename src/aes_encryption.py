from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from logger_config import setup_logger
import warnings
from tqdm import tqdm
import os
import base64

tqdm.pandas()
warnings.filterwarnings('ignore')
logger = setup_logger(__name__)


def aes_cc_tokenisation(cc_numbers_to_tokenise):
    logger.info(f'******** : AES Tokenisation : ********')
    cc_numbers_to_tokenise['aes_token'] = cc_numbers_to_tokenise['clean_credit_card_number'].apply(lambda x: encrypt_cc_number(x))
    logger.debug(cc_numbers_to_tokenise[['credit_card_number','clean_credit_card_number','aes_token']].head(10))
    return cc_numbers_to_tokenise

def encrypt_cc_number(cc_number: str) -> str:
    key = os.urandom(16)
    # Convert to bytes
    data = cc_number.encode()

    # Pad the data
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()

    # Generate a random IV for each encryption
    iv = os.urandom(16)

    # Create AES cipher
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(padded_data) + encryptor.finalize()

    cc_token = base64.b64encode(iv + encrypted).decode()

    # Return base64 encoded (IV + encrypted data)
    return cc_token

def decrypt_cc_number(token, key):
    # Decode base64
    token_bytes = base64.b64decode(token)

    # Extract IV and encrypted data
    iv = token_bytes[:16]
    encrypted_data = token_bytes[16:]

    # Create cipher
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()

    # Remove padding
    unpadder = padding.PKCS7(128).unpadder()
    decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()

    return decrypted.decode()