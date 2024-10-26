# Import necessary libraries
import cv2
import os
import pandas as pd
import re
import numpy as np
from ultralytics import YOLO
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import seaborn as sns
import matplotlib.pyplot as plt
import joblib  # For saving and loading models
import warnings

warnings.filterwarnings("ignore")
plt.rcParams['font.sans-serif'] = ['SimHei']  # Set font for Chinese characters

# Define parameters
dataset_dir = r'dataset_fitness'  # Dataset directory, modify according to actual path
output_image_dir = 'output_images'  # Folder for saving frame images
output_csv_path = 'output_keypoints_data.csv'  # Path for saving joint data as CSV
os.makedirs(output_image_dir, exist_ok=True)

# Define names for 17 keypoints
KEYPOINT_NAMES = [
    "Nose", "Right Eye", "Left Eye", "Right Ear", "Left Ear",
    "Right Shoulder", "Left Shoulder", "Right Elbow", "Left Elbow",
    "Right Wrist", "Left Wrist", "Right Hip", "Left Hip",
    "Right Knee", "Left Knee", "Right Ankle", "Left Ankle"
]

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

# Define function to calculate new origin and normalize coordinates
def calculate_new_origin(keypoints_data):
    right_shoulder = keypoints_data[5][:2]
    left_shoulder = keypoints_data[6][:2]
    right_hip = keypoints_data[11][:2]
    left_hip = keypoints_data[12][:2]

    valid_points = [p for p in [right_shoulder, left_shoulder, right_hip, left_hip] if p[0] != 0 and p[1] != 0]
    if len(valid_points) == 0:
        raise ValueError("Missing keypoints for right shoulder, left shoulder, right hip, and left hip; unable to calculate new origin")

    x0 = sum([p[0] for p in valid_points]) / len(valid_points)
    y0 = sum([p[1] for p in valid_points]) / len(valid_points)
    return x0, y0

def get_min_max_of_new_coords(keypoints_data, x0, y0):
    x_new_values = []
    y_new_values = []

    for keypoint in keypoints_data:
        x, y, conf = keypoint
        if conf > 0:  # Only calculate valid keypoints
            x_new = x - x0
            y_new = -(y - y0)  # Y-axis grows from bottom to top
            x_new_values.append(x_new)
            y_new_values.append(y_new)

    x_min_new, x_max_new = min(x_new_values), max(x_new_values)
    y_min_new, y_max_new = min(y_new_values), max(y_new_values)

    return x_min_new, x_max_new, y_min_new, y_max_new

def parse_keypoints_with_custom_origin(results):
    parsed_keypoints_list = []
    for i in range(len(results)):
        keypoints_data = results[i].keypoints.data.cpu().numpy()[0]  # Get keypoints (17, 3)

        # Calculate new origin coordinates
        try:
            x0, y0 = calculate_new_origin(keypoints_data)
        except ValueError as e:
            print(f"Unable to calculate new origin for object {i}: {e}")
            continue  # Skip this object

        # Calculate max and min values for x_new and y_new in new coordinate system
        x_min_new, x_max_new, y_min_new, y_max_new = get_min_max_of_new_coords(keypoints_data, x0, y0)

        object_keypoints = {"object_id": i}
        keypoint_dict = {}

        # Calculate normalized coordinates for each keypoint relative to new origin
        for j, keypoint in enumerate(keypoints_data):
            x, y, conf = keypoint
            if x == 0 and y == 0:
                keypoint_dict[KEYPOINT_NAMES[j]] = None
            else:
                # Coordinates in the new system, Y-axis grows from bottom to top
                x_new = x - x0
                y_new = -(y - y0)

                # Normalize the new coordinates
                if x_max_new != x_min_new:
                    x_normalized = (x_new - x_min_new) / (x_max_new - x_min_new)
                else:
                    x_normalized = 0  # Avoid division by zero if max equals min

                if y_max_new != y_min_new:
                    y_normalized = (y_new - y_min_new) / (y_max_new - y_min_new)
                else:
                    y_normalized = 0  # Avoid division by zero if max equals min

                keypoint_dict[KEYPOINT_NAMES[j]] = {
                    "name": KEYPOINT_NAMES[j],
                    "x": x_normalized,
                    "y": y_normalized,
                    "confidence": conf
                }

        object_keypoints["keypoints"] = keypoint_dict
        parsed_keypoints_list.append(object_keypoints)

    return parsed_keypoints_list

# Initialize list to save data
all_data = []

# Load YOLOv8 pose model
model = YOLO('yolov8n-pose.pt')

# Traverse the dataset_fitness directory and find all video files
for root, dirs, files in os.walk(dataset_dir):
    for file in files:
        if file.endswith('.MOV') or file.endswith('.mov'):  # Process video files
            input_video_path = os.path.join(root, file)
            # Print the video file currently being processed
            print(f"Processing video: {input_video_path}")
            # Extract action name and standard type
            video_info = input_video_path.split(os.sep)[-2:]  # Extract the last two parts as action name and standard
            action_name = re.sub(r'^\d+\s*', '', video_info[0])  # Remove leading numbers and spaces
            standard_type = video_info[1].split('.')[0]

            # Open video file
            cap = cv2.VideoCapture(input_video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps

            # Capture 5 frames every 0.5 seconds
            frames_per_half_second = int(fps / 2)
            max_duration = 3.0  # Only process the first 3 seconds of the video
            max_frame_to_process = int(fps * max_duration)

            frame_indices = []
            for i in range(0, max_frame_to_process, frames_per_half_second):
                # Capture 3 frames at intervals from the 5 frames
                for j in [0, 2, 4]:  # Capture 1st, 3rd, and 5th frames
                    frame_index = i + j
                    if frame_index < max_frame_to_process:
                        frame_indices.append(frame_index)

            frame_indices = sorted(set(frame_indices))  # Ensure unique frames, sorted order

            # Process video frame by frame
            frame_number = 0
            sequence_number = 0

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_number in frame_indices:
                    # Use model for detection
                    results = model(frame)
                    parsed_keypoints = parse_keypoints_with_custom_origin(results)

                    # Assign the same sequence number: frames within 0.5 seconds share the same sequence number
                    sequence_number = frame_number // frames_per_half_second

                    for obj in parsed_keypoints:
                        keypoints = obj['keypoints']
                        row_data = {
                            'action_name': action_name,
                            'standard_type': standard_type,
                            'frame_index': frame_number,
                            'sequence': sequence_number,
                        }
                        # Store each keypoint's coordinates in row_data
                        for kp_name in KEYPOINT_NAMES:
                            kp_info = keypoints.get(kp_name, None)
                            if kp_info:
                                row_data[f'{kp_name}_x'] = kp_info['x']
                                row_data[f'{kp_name}_y'] = kp_info['y']
                            else:
                                row_data[f'{kp_name}_x'] = None
                                row_data[f'{kp_name}_y'] = None

                        all_data.append(row_data)

                    # Save processed frame image
                    processed_frame = results[0].plot()

                    image_output_path = os.path.join(output_image_dir,
                                                     f"{action_name}_{standard_type}_{frame_number}_{sequence_number}.jpg")
                    cv2.imwrite(image_output_path, processed_frame)  # Save detection result image

                frame_number += 1

            # Release video resources
            cap.release()

# Convert all data to DataFrame
columns = ['action_name', 'standard_type', 'frame_index', 'sequence'] + [f'{k}_x' for k in KEYPOINT_NAMES] + [f'{k}_y' for k in KEYPOINT_NAMES]
data = pd.DataFrame(all_data, columns=columns)

# Save data to CSV file
data.to_csv(output_csv_path, index=False)
print("Data extraction completed and saved to CSV file.")

# Data cleaning and mean filling
# Use groupby to group by action_name and standard_type, filling missing values in coordinate columns with group mean
data[keypoint_columns] = data.groupby(['action_name', 'standard_type'])[keypoint_columns].transform(
    lambda group: group.fillna(group.mean())
)

# Check for any remaining missing values and handle exceptions
if data[keypoint_columns].isnull().sum().sum() > 0:
    print("Some groups of action_name and standard_type have NaN means, may need further handling.")
else:
    print("All missing values successfully filled!")

# Prepare features and labels
features = keypoint_columns
X = data[features]  # Keypoint coordinates
y = data['action_name']  # Classification labels (action names)

# Encode labels as numbers
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Save label encoder
joblib.dump(label_encoder, 'action_label_encoder.pkl')

# Split into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.3, random_state=42)

# Create and train KNN model
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, y_train)

# Make predictions
y_pred = knn.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy of KNN action classification: {accuracy:.2f}")

# Generate and evaluate confusion matrix
conf_matrix = confusion_matrix(y_test, y_pred)

# Visualize confusion matrix
plt.figure(figsize=(12, 10))
sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues", xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
plt.title("Action Classification Confusion Matrix")
plt.xlabel("Predicted Class")
plt.ylabel("True Class")
plt.tight_layout()
plt.show()

# Print classification report (including precision, recall, F1 score)
print("Action Classification Report:")
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

# Save action classification model
joblib.dump(knn, 'action_classification_model.pkl')

