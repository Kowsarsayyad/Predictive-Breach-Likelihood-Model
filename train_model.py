import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

# Create simulated historical attack dataset
np.random.seed(42)

data = pd.DataFrame({
    "failed_logins": np.random.randint(0, 50, 500),
    "open_ports": np.random.randint(1, 20, 500),
    "outdated_patches": np.random.randint(0, 15, 500),
    "traffic_spike": np.random.randint(0, 100, 500),
    "phishing_reports": np.random.randint(0, 30, 500),
})

# Create breach condition logic
data["breach"] = (
    (data["failed_logins"] > 30) |
    (data["open_ports"] > 10) |
    (data["outdated_patches"] > 7) |
    (data["traffic_spike"] > 70)
).astype(int)

X = data.drop("breach", axis=1)
y = data["breach"]

model = RandomForestClassifier()
model.fit(X, y)

joblib.dump(model, "model.pkl")

print("✅ Model trained successfully!")