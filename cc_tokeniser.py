'''
    @Name: Credit Card Tokenisation
    @Author: Noel Singh
    @Description:
    The following application is used to tokenise credit card number using a AES Encryption method and FPE Encryption.

    AES Encryption
    AES is a symmetric-key block cipher — meaning it uses the same key for both encryption and decryption. It is widely used due to its strength and efficiency in modern cryptographic applications.
    Symmetric-key: The same key encrypts and decrypts.
    Block cipher: It encrypts data in fixed-size blocks (typically 128 bits or 16 bytes).
    Key sizes: AES supports key lengths of 128, 192, or 256 bits.

    FPE Encryption
    Format-Preserving Encryption (FPE) is a class of encryption algorithms where the ciphertext has the same format as the plaintext.
    ✅ Tokenization with reversibility
    ✅ Keeps legacy systems happy (they expect data of certain lengths/formats)
    ✅ No schema changes needed in databases (because formats don’t change)
    ✅ PCI compliance friendliness (often used in credit card/token vaults)

    FPE encrypts data while respecting a specific format using standard block ciphers like AES under the hood — it wraps these in special constructions like:
    FF1 / FF3: NIST-approved algorithms for FPE over strings/numbers
    Feistel networks: for splitting and recombining data in predictable formats
'''

#import statement
import logging
import colorlog
import random
import pandas as pd
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
import base64
import pyffx

#FPE Encryption Key
fpe_key = b'mysecretkey12345'

def logger_function():
    """Function that is used to capture the configuration for the logger."""
    logging_level = logging.DEBUG
    log_colors = {'INFO': 'bold_blue',
                  'DEBUG': 'cyan',
                  'WARNING': 'yellow',
                  'ERROR': 'red',
                  'CRITICAL': 'bold_red',}
    formatter = colorlog.ColoredFormatter('%(log_color)s[%(levelname)s]: %(message)s', log_colors=log_colors)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = colorlog.getLogger('bot_logger')
    logger.setLevel(logging_level)
    logger.addHandler(handler)
    return logger

def create_data_to_be_tokenised():
    """ The module is used to generate dummy data for use in the tokenisation program demonstration.
        It generates: policy id's, credit card numbers and expiration dates, and converts the information from a
        dictionary to a dataframe which is then used for processing.
    """
    logger.info(f'******** : Create Sample Data : ********')
    sample = 18000
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

def data_exploration(cc_numbers_to_tokenise):
    logger.info(f'******** : Checking Data to Tokenise : ********')
    """
    Check the character length of each field in all records.
    Returns a list of any records that fail the expected lengths.
    """
    invalid_pol = policy_id_checks(cc_numbers_to_tokenise)
    invalid_cc = cc_number_checks(cc_numbers_to_tokenise)
    total_rows_with_special = check_special_characters(cc_numbers_to_tokenise)

    if len(invalid_pol) != 0 or len(invalid_cc) != 0 or total_rows_with_special != 0:
        status = 'Errors'
    else:
        status = 'No_Errors'
    return status

def policy_id_checks(data: pd.DataFrame) -> list:
    ''''''
    logger.info(f'----- : Policy ID Checks : -----')
    invalid_pol = []
    for index, row in data.iterrows():
        pol_len = len(row['policy_id'])
        if pol_len != 9:
            invalid_pol.append(index)

    if len(invalid_pol) > 0:
        logger.warning(invalid_pol)
    else:
        logger.debug('No data length issues found')
    return invalid_pol

def cc_number_checks(data: pd.DataFrame) -> list:
    logger.info(f'----- : Credit Card Checks : -----')
    invalid_cc = []
    for index, row in data.iterrows():
        cc_len = len(row['credit_card_number'])
        if cc_len < 16:
            invalid_cc.append(index)

    #If Errors Found Report
    if len(invalid_cc) > 0:
        # logger.warning(invalid_cc)
        logger.debug(f'Total CC Length Errors: {len(invalid_cc)}')
    else:
        logger.debug('No data length issues found')
    return invalid_cc

def check_special_characters(data: pd.DataFrame) -> list:
    logger.info(f'----- : Checking for Special Characters : -----')
    special_char_pattern = r'[^A-Za-z0-9]'
    # Check for special characters in 'policy_id' and 'credit_card_number'
    data['policy_id_has_special'] = data['policy_id'].str.contains(special_char_pattern)
    data['card_has_special'] = data['credit_card_number'].str.contains(special_char_pattern)

    # Count of rows with special characters in each column
    policy_id_special_count = data['policy_id_has_special'].sum()
    card_special_count = data['card_has_special'].sum()

    # Total rows with special characters in either field
    total_rows_with_special = (data['policy_id_has_special'] | data['card_has_special']).sum()

    logger.debug(f'Total Errors: {total_rows_with_special} \n'
                 f'Total Policy Number: {policy_id_special_count} \n'
                 f'Total CC Number: {card_special_count}')
    return total_rows_with_special

def clean_data_before_tokenisation(cc_numbers_to_tokenise: pd.DataFrame) -> pd.DataFrame:
    logger.info(f'******** : Checking Data to Tokenise : ********')
    # cc_numbers_to_tokenise = remove_white_spaces(cc_numbers_to_tokenise)
    cc_numbers_to_tokenise = fix_cc_length_issues(cc_numbers_to_tokenise)

    return cc_numbers_to_tokenise

def remove_white_spaces(cc_numbers_to_tokenise):
    logger.debug('Removing White spaces from credit card numbers')
    #TODO: Complete functionality

def fix_cc_length_issues(cc_numbers_to_tokenise):
    logger.debug('----- : Checking CC length : -----')
    for index, row in cc_numbers_to_tokenise.iterrows():
        cc_len = len(cc_numbers_to_tokenise['credit_card_number'])
        if cc_len != 16:
            cc_numbers_to_tokenise['clean_credit_card_number'] = cc_numbers_to_tokenise['credit_card_number'].astype(str).str.zfill(16)
        else:
            cc_numbers_to_tokenise['clean_credit_card_number'] = cc_numbers_to_tokenise['credit_card_number']
    return cc_numbers_to_tokenise

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


def run_program():
    cc_numbers_to_tokenise = create_data_to_be_tokenised()
    status = data_exploration(cc_numbers_to_tokenise)
    cc_numbers_to_tokenise = clean_data_before_tokenisation(cc_numbers_to_tokenise)
    cc_numbers_to_tokenise = aes_cc_tokenisation(cc_numbers_to_tokenise)
    cc_numbers_to_tokenise = format_preserving_encryption_tokenisation(cc_numbers_to_tokenise, fpe_key)

if __name__ == '__main__':
    logger = logger_function()
    run_program()


