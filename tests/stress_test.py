from locust import HttpUser, task, between
import random
import pandas as pd

# Load customer IDs from the dataset
df = pd.read_csv("data/sample_data.csv")
valid_customers = df["customer_id"].unique().tolist()

class RecommendationStressTest(HttpUser):
    wait_time = between(1, 3)  # Simulates realistic user behavior

    @task
    def recommend(self):
        if not valid_customers:
            print("⚠️ No valid customer IDs found in dataset.")
            return

        customer_id = random.choice(valid_customers)  # ✅ Pick a real customer ID
        top_n = random.choice([3, 5, 10])  # Test different `top_n` values

        response = self.client.get(f"/recommend/?customer_id={customer_id}&top_n={top_n}")

        if response.status_code != 200:
            print(f"❌ Failed request: {response.status_code}, {response.text}")
