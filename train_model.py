import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib

# Load the dataset
data = pd.read_csv('world_happiness_data.csv')  # Replace with your dataset path

# Define features and target
X = data[['GDP per capita', 'Social support', 'Healthy life expectancy', 
          'Freedom to make life choices', 'Generosity', 'Perceptions of corruption']]
y = data['Happiness Score']

# Split the dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Save the model
joblib.dump(model, 'happiness_model.pkl')
print("Model training complete. Model saved as 'happiness_model.pkl'.")
