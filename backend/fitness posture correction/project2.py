# Import necessary libraries
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import joblib  # For saving and loading models
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings("ignore")
plt.rcParams['font.sans-serif'] = ['SimHei']  # Set font for Chinese characters

# Load previously saved data
data = pd.read_csv('output_keypoints_data.csv')

# Define keypoints to keep
keypoints_to_keep = [
    'Right Shoulder', 'Left Shoulder', 'Right Elbow', 'Left Elbow',
    'Right Wrist', 'Left Wrist', 'Right Hip', 'Left Hip',
    'Right Knee', 'Left Knee', 'Right Ankle', 'Left Ankle'
]

# Construct column names to process
keypoint_columns = []
for kp in keypoints_to_keep:
    keypoint_columns.append(f'{kp}_x')
    keypoint_columns.append(f'{kp}_y')

# Data cleaning and mean filling
data[keypoint_columns] = data.groupby(['action_name', 'standard_type'])[keypoint_columns].transform(
    lambda group: group.fillna(group.mean())
)

# Separate data for standard and non-standard actions
standard_data = data[data['standard_type'] == 'standard']
nonstandard_data = data[data['standard_type'] != 'standard']

# Ensure non-standard actions exist in standard actions
standard_action_names = standard_data['action_name'].unique()
nonstandard_data = nonstandard_data[nonstandard_data['action_name'].isin(standard_action_names)]

# Prepare three-frame combination features for standard action data
grouped_data_standard = []
group_size = 3  # Each group consists of 3 frames

for name, group in standard_data.groupby(['action_name', 'sequence']):  # Group standard data by action_name and sequence
    if len(group) >= group_size:  # Check if the group contains at least 3 frames
        for i in range(0, len(group) - group_size + 1, 1):  # e.g., if there are 5 frames, iterates frames 0-2, 1-3, 2-4
            frames = group.iloc[i:i + group_size]  # Select frames i to i + group_size to form a subset of 3 frames
            second_frame = frames.iloc[1][keypoint_columns].values  # Extract keypoint coordinates of the middle frame
            first_diff = frames.iloc[0][keypoint_columns].values - frames.iloc[1][keypoint_columns].values  # Calculate displacement from first to second frame
            third_diff = frames.iloc[2][keypoint_columns].values - frames.iloc[1][keypoint_columns].values

            combined_features = np.hstack([second_frame, first_diff, third_diff])
            # The feature vector contains position info of the middle frame and displacement info of adjacent frames
            grouped_data_standard.append({
                'action_name': name[0],
                'sequence': name[1],
                'features': combined_features,
                'second_frame_keypoints': second_frame  # Save keypoints of the middle frame
            })

# Convert to DataFrame: Contains action name, stage, combined features, and is the result of standard action feature extraction
grouped_df_standard = pd.DataFrame(grouped_data_standard)

# One-hot encode action_name to include all categories
onehot_encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
onehot_encoder.fit(grouped_df_standard[['action_name']])

# Save OneHotEncoder
joblib.dump(onehot_encoder, 'action_onehot_encoder.pkl')

# Combine one-hot encoded category features with other numeric features
X_standard = np.hstack((onehot_encoder.transform(grouped_df_standard[['action_name']]),
                        np.vstack(grouped_df_standard['features'].values)))  # Features

# Get sequence labels
y_sequence_standard = grouped_df_standard['sequence']  # Action stage classification labels

# Feature standardization
scaler = StandardScaler()
X_standard_scaled = scaler.fit_transform(X_standard)

# Save scaler
joblib.dump(scaler, 'feature_scaler.pkl')

# Train the model on standard action data
rf_model_sequence = RandomForestClassifier(n_estimators=1000, random_state=42)

# Randomly split into training and validation sets
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X_standard_scaled, y_sequence_standard, test_size=0.4, random_state=42)

# Train the model
rf_model_sequence.fit(X_standard_scaled, y_sequence_standard)

# Evaluate the model
y_pred = rf_model_sequence.predict(X_test)

# Evaluate model accuracy
accuracy_standard = accuracy_score(y_test, y_pred)
print(f"Accuracy of classification of standard action stages: {accuracy_standard:.2f}")

# Print classification report
print("Standard action stage classification report:")
print(classification_report(y_test, y_pred))

# Plot confusion matrix
conf_matrix_standard = confusion_matrix(y_sequence_standard, y_pred_standard)
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix_standard, annot=True, fmt="d", cmap="Blues")
plt.title("Confusion Matrix for Standard Action Stage Classification")
plt.xlabel("Predicted Stage")
plt.ylabel("True Stage")
plt.tight_layout()
plt.show()

# Save action stage classification model
joblib.dump(rf_model_sequence, 'action_stage_model.pkl')

# Calculate and save mean keypoints for standard actions
grouped_data_standard_mean = []
for name, group in standard_data.groupby(['action_name', 'sequence']):
    keypoints_mean = group[keypoint_columns].mean().values
    grouped_data_standard_mean.append({
        'action_name': name[0],
        'sequence': name[1],
        'second_frame_keypoints': keypoints_mean
    })

standard_keypoints_mean = pd.DataFrame(grouped_data_standard_mean)

# Save mean keypoints for standard actions
standard_keypoints_mean.to_pickle('standard_keypoints_mean.pkl')

