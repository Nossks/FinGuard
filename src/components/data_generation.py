import os
import sys
import pandas as pd
import random
from faker import Faker
from dataclasses import dataclass
from src.exception import CustomException
from src.logger import logging


# --- Configuration ---
@dataclass
class DataGenerationConfig:
    """
    Defines where the output file should be saved.
    """
    raw_data_path: str = os.path.join('data', 'financial_synthetic.csv')

# --- Main Component ---
class DataGenerator:
    def __init__(self):
        self.generation_config = DataGenerationConfig()
        self.fake = Faker()
        
        # Vocabulary for "Normal" Transactions
        self.merchants = ['Starbucks', 'Walmart', 'Amazon', 'Uber', 'Netflix', 'Target', 'Whole Foods', 'Shell Station']
        self.categories = ['groceries', 'entertainment', 'transport', 'utilities', 'dining', 'shopping']
        
        # Vocabulary for "Fraud" Transactions (The Signal)
        self.fraud_keywords = ['offshore', 'urgent', 'crypto', 'gift card', 'unverified', 'suspicious', 'shell company']
        self.suspicious_countries = ['Cayman Islands', 'Panama', 'Unknown', 'Russia', 'Cyprus']

    def _generate_normal_transaction(self):
        """Creates a boring, standard transaction."""
        merchant = random.choice(self.merchants)
        amount = round(random.uniform(5.0, 300.0), 2)
        date = self.fake.date_this_year()
        
        # The text to be embedded
        description = f"Purchase at {merchant} for {random.choice(self.categories)}. Date: {date}. Status: Cleared."
        
        return {
            "text": description,
            "amount": amount,
            "label": 0,  # 0 = Normal
            "metadata": f"merchant:{merchant}"
        }

    def _generate_fraud_transaction(self):
        """Creates a transaction with semantic 'red flags'."""
        keyword = random.choice(self.fraud_keywords)
        country = random.choice(self.suspicious_countries)
        amount = round(random.uniform(1000.0, 50000.0), 2)
        
        # The text to be embedded (High Semantic Signal)
        description = f"Urgent wire transfer detected. Keyword: {keyword}. Destination: {country}. Amount: ${amount}. Risk: High."
        
        return {
            "text": description,
            "amount": amount,
            "label": 1,  # 1 = Fraud
            "metadata": f"keyword:{keyword}"
        }

    def initiate_data_generation(self, num_rows=100):
        """
        Main function to trigger data generation.
        """
        logging.info("Entered the Data Generation method or component")
        try:
            data = []
            
            # 1. Generate the data loop
            logging.info(f"Generating {num_rows} synthetic transactions...")
            for _ in range(num_rows):
                # 5% chance of being fraud
                if random.random() < 0.05:
                    data.append(self._generate_fraud_transaction())
                else:
                    data.append(self._generate_normal_transaction())

            # 2. Convert to DataFrame
            df = pd.DataFrame(data)
            
            # 3. Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.generation_config.raw_data_path), exist_ok=True)

            # 4. Save to CSV
            df.to_csv(self.generation_config.raw_data_path, index=False, header=True)
            
            logging.info(f"Data generation completed. Saved to {self.generation_config.raw_data_path}")
            
            return self.generation_config.raw_data_path

        except Exception as e:
            raise CustomException(e, sys)
        
# if __name__ == "__main__":
#     gen = DataGenerator()
#     path = gen.initiate_data_generation(1000)
#     print(f"check at path{path}")