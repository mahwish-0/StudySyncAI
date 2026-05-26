from sklearn.linear_model import LinearRegression
import numpy as np

def predict_study_hours(task):
    priority_map = {'Low': 1, 'Medium': 2, 'High': 3}
    difficulty_map = {'Easy': 1, 'Medium': 2, 'Hard': 3}

    # Training data: [priority, difficulty, days_left]
    X = np.array([
        [1, 1, 10],
        [1, 2, 7],
        [2, 2, 5],
        [2, 3, 4],
        [3, 2, 2],
        [3, 3, 1],
    ])

    # Output: recommended study hours
    y = np.array([1, 1.5, 2, 2.5, 3, 4])

    model = LinearRegression()
    model.fit(X, y)

    from datetime import date
    days_left = max((task.deadline - date.today()).days, 1)

    input_data = np.array([[
        priority_map.get(task.priority, 2),
        difficulty_map.get(task.difficulty, 2),
        days_left
    ]])

    prediction = model.predict(input_data)[0]
    return round(max(prediction, 1), 1)
