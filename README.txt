@Name: Credit Card Tokenisation using Python
@Author: Noel Singh
@Date: 14th April 2025
@Description: The following application is used to create a unique token for credit cards which belong to different
policies / accounts. The credit cards need to be in a 16-digit format, and are generated using random values within
a given range.

--------------------------------------------------------------------------------------------------------------------
@version: 1.0
@date = 14th April 2025
@includes:
    > Creation of test data i.e. policy numbers, credit card numbers and expiration dates
    > Generation of bulk records for testing
    > Checks performed on data including:
        - special characters in data
        - data lengths and consistency
--------------------------------------------------------------------------------------------------------------------
@version: 2.0
@date: 21st April 2025
@includes:
    > separate module for creation of test data to use for tokenisation
    > logger_config.py creation to reuse across modules.
    > separate fpe and aes modules
    > update to main function
