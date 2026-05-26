from sklearn.svm import SVC
import numpy as np
from datetime import date

def predict_priority_svm(task):
    difficulty_map = {
        'Easy': 1,
        'Medium': 2,
        'Hard': 3
    }

    # Training data: [difficulty, hours, days_left]
    X = np.array([
        [1, 1, 10],
        [1, 2, 7],
        [2, 2, 5],
        [2, 3, 4],
        [3, 4, 2],
        [3, 5, 1],
        [3, 6, 1],
        [2, 5, 2],
    ])

    # Output: 0 = Low, 1 = Medium, 2 = High
    y = np.array([0, 0, 1, 1, 2, 2, 2, 2])

    model = SVC(kernel='linear')
    model.fit(X, y)

    days_left = max((task.deadline - date.today()).days, 1)

    input_data = np.array([[
        difficulty_map.get(task.difficulty, 2),
        task.hours,
        days_left
    ]])

    prediction = model.predict(input_data)[0]

    priority_map = {
        0: 'Low',
        1: 'Medium',
        2: 'High'
    }

    return priority_map[prediction]
