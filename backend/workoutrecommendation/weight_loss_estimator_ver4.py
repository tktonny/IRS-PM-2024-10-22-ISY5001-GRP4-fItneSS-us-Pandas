import pandas as pd
import tensorflow as tf
import joblib
import math
import os

class WeightLossEstimator:
    def __init__(self):
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # FATAL
        tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

        # 获取当前文件的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 构建模型文件的完整路径
        model_path = os.path.join(current_dir, 'calories_prediction_model.keras')
        preprocessor_path = os.path.join(current_dir, 'preprocessor.joblib')

        # 添加调试信息
        print(f"Attempting to load model from: {model_path}")
        print(f"Attempting to load preprocessor from: {preprocessor_path}")

        if os.path.exists(model_path):
            print("Model file found")
        else:
            print("Model file not found")

        if os.path.exists(preprocessor_path):
            print("Preprocessor file found")
        else:
            print("Preprocessor file not found")

        # 加载模型和预处理器
        self.model = tf.keras.models.load_model(model_path)
        self.preprocessor = joblib.load(preprocessor_path)

        self.activities = [
            {'name': 'Walking', 'intensity': 0.5},
            {'name': 'Jogging', 'intensity': 0.7},
            {'name': 'Swimming', 'intensity': 0.6},
            {'name': 'Sit-ups', 'intensity': 0.6},
            {'name': 'Squats', 'intensity': 0.65},
            {'name': 'Jumping Jacks', 'intensity': 0.7}
        ]

    # 其余方法保持不变
    def predict_calories(self, gender, age, height, weight, heart_rate):
        input_data = pd.DataFrame({
            'Gender': [gender],
            'Age': [age],
            'Height': [height],
            'Weight': [weight],
            'Duration': [30],  # Fixed at 30 minutes
            'Heart_Rate': [heart_rate]
        })
        input_preprocessed = self.preprocessor.transform(input_data)
        return self.model.predict(input_preprocessed, verbose=0)[0][0]

    def calculate_target_heart_rate(self, age, intensity):
        max_heart_rate = 220 - age
        target_heart_rate = max_heart_rate * intensity
        return round(target_heart_rate)

    def calculate_bmr(self, gender, weight, height, age):
        if gender.lower() == 'male':
            return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

    def estimate_weight_loss_time(self, gender, age, height, current_weight, target_weight):
        weight_to_lose = current_weight - target_weight
        if weight_to_lose <= 0:
            return "You've already reached or exceeded your target weight!", []

        daily_calorie_intake = 2000 if gender.lower() == 'male' else 1500
        results = []

        for activity in self.activities:
            heart_rate = self.calculate_target_heart_rate(age, activity['intensity'])
            
            weight = current_weight
            total_days = 0
            previous_sets = 0
            stages = []

            initial_calories = self.predict_calories(gender, age, height, current_weight, heart_rate)

            while weight > target_weight:
                bmr = self.calculate_bmr(gender, weight, height, age)
                calorie_difference = daily_calorie_intake - bmr

                calories_per_session = self.predict_calories(gender, age, height, weight, heart_rate)
                sets_needed = math.ceil(calorie_difference / calories_per_session) + 4

                if sets_needed != previous_sets or weight == current_weight:
                    minutes = sets_needed * 30
                    if stages:
                        stages[-1]['days'] = total_days - stages[-1]['start_day']
                    stages.append({
                        'weight': round(weight, 1),
                        'minutes': minutes,
                        'start_day': total_days
                    })
                    previous_sets = sets_needed

                calories_burned = calories_per_session * sets_needed
                net_calorie_loss = calories_burned - calorie_difference
                weight_loss = net_calorie_loss / 7700  # Approximate calories per kg of fat
                weight -= weight_loss
                total_days += 1

            # 更新最后一个阶段的天数
            if stages:
                stages[-1]['days'] = total_days - stages[-1]['start_day']

            # 移除 start_day，只保留关键信息
            simplified_stages = [{'weight': stage['weight'], 'minutes': stage['minutes'], 'days': stage['days']} for stage in stages]

            results.append({
                'name': activity['name'],
                'heart_rate': heart_rate,
                'total_days': total_days,
                'stages': simplified_stages,
                'initial_calories': initial_calories
            })

        return f"You need to lose {weight_to_lose:.1f} kg to reach your target weight.", results

    def get_estimate_object(self, gender, age, height, current_weight, target_weight):
        message, results = self.estimate_weight_loss_time(gender, age, height, current_weight, target_weight)
        return {
            'message': message,
            'results': results,
            'input_params': {
                'gender': gender,
                'age': age,
                'height': height,
                'current_weight': current_weight,
                'target_weight': target_weight
            }
        }

    def get_weight_loss_estimate(self, gender, age, height, current_weight, target_weight):
        message, results = self.estimate_weight_loss_time(gender, age, height, current_weight, target_weight)
        return {
            'message': message,
            'results': results
        }

    def print_estimate(self, estimate):
        print(estimate['message'])
        print("\nEstimated results for each exercise:")
        for activity in estimate['results']:
            print(f"\n- {activity['name']}:")
            print(f"  Target heart rate: {activity['heart_rate']} bpm")
            print(f"  Total estimated days to reach target weight: {activity['total_days']}")
            print(f"  Calories burned in 30 minutes at current weight: {activity['initial_calories']:.2f}")
            print("  Exercise stages:")
            for stage in activity['stages']:
                print(f"    At {stage['weight']:.1f} kg: {stage['minutes']} minutes daily for {stage['days']} days")

        print("\nRemember:")
        print("- These estimates account for decreasing calorie burn as you lose weight.")
        print("- A combination of exercises is recommended for better results and overall fitness.")
        print("- A safe and sustainable weight loss is about 0.5-1 kg per week.")
        print("- Combine exercise with a balanced diet for best results.")
        print("- Gradually increase intensity and duration of exercises as your fitness improves.")
        print("- Consult with a healthcare professional before starting any new exercise regime.")
        
    def get_estimate_string(self, estimate):
        result = estimate['message'] + "\n\n"
        result += "Estimated results for each exercise:\n\n"

        for activity in estimate['results']:
            result += f"- {activity['name']}:\n"
            result += f"  Target heart rate: {activity['heart_rate']} bpm\n"
            result += f"  Total estimated days to reach target weight: {activity['total_days']}\n"
            result += f"  Calories burned in 30 minutes at current weight: {activity['initial_calories']:.2f}\n"
            result += "  Exercise stages:\n"
            for stage in activity['stages']:
                result += f"    At {stage['weight']:.1f} kg: {stage['minutes']} minutes daily for {stage['days']} days\n"
            result += "\n"

        result += "Remember:\n"
        result += "- These estimates account for decreasing calorie burn as you lose weight.\n"
        result += "- A combination of exercises is recommended for better results and overall fitness.\n"
        result += "- A safe and sustainable weight loss is about 0.5-1 kg per week.\n"
        result += "- Combine exercise with a balanced diet for best results.\n"
        result += "- Gradually increase intensity and duration of exercises as your fitness improves.\n"
        result += "- Consult with a healthcare professional before starting any new exercise regime.\n"

        return result

# 使用示例
if __name__ == "__main__":
    estimator = WeightLossEstimator()
    estimate = estimator.get_estimate_object('Male', 30, 165, 100, 70)
    
    print(estimate['message'])
    print(f"\nInput Parameters:")
    for key, value in estimate['input_params'].items():
        print(f"  {key.capitalize()}: {value}")

    for activity in estimate['results']:
        print(f"\n{activity['name']}:")
        print(f"  Target heart rate: {activity['heart_rate']} bpm")
        print(f"  Total days to reach target weight: {activity['total_days']}")
        print(f"  Initial calories burned in 30 minutes: {activity['initial_calories']:.2f}")
        print("  Exercise stages:")
        for stage in activity['stages']:
            print(f"    At {stage['weight']:.1f} kg: {stage['minutes']} minutes daily for {stage['days']} days")

    print("\nRemember:")
    print("- These estimates account for decreasing calorie burn as you lose weight.")
    print("- A combination of exercises is recommended for better results and overall fitness.")
    print("- A safe and sustainable weight loss is about 0.5-1 kg per week.")
    print("- Combine exercise with a balanced diet for best results.")
    print("- Gradually increase intensity and duration of exercises as your fitness improves.")
    print("- Consult with a healthcare professional before starting any new exercise regime.")