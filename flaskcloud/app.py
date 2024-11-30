# application.py
from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
from sklearn.datasets import fetch_openml
import os
import shutil
import matplotlib
matplotlib.use('Agg')  # GUI 백엔드 비활성화
import matplotlib.pyplot as plt
import warnings
from threading import Lock

# 경고 무시
warnings.filterwarnings("ignore", message="X does not have valid feature names")

app = Flask(__name__)

# 모델 로드
model = joblib.load('mnist_model.pkl')

# MNIST 데이터 로드
mnist = fetch_openml('mnist_784', version=1, as_frame=False)
X, y = mnist.data, mnist.target.astype(int)  # y를 정수형으로 변환

# 오답 이미지를 저장할 폴더
os.makedirs('static/images', exist_ok=True)

# 정답 및 오답 통계
correct = 0
incorrect = 0

# Lock 객체 생성
lock = Lock()

@app.route('/')
def index():
    return render_template('index.html', correct=correct, incorrect=incorrect)

@app.route('/predict', methods=['POST'])
def predict():
    global correct, incorrect

    # 사용자가 전송한 데이터
    data = request.json
    idx = data.get('index')  # 테스트 데이터의 인덱스

    # 인덱스 유효성 검사
    if idx is None or not (0 <= idx < len(X)):
        return jsonify({'error': 'Invalid index provided.'}), 400

    # 샘플 데이터와 실제 레이블
    image = X[int(idx)].reshape(1, -1)
    true_label = y[int(idx)]

    # 모델 예측
    prediction = model.predict(image)[0]

    # Lock을 사용하여 상태 업데이트 안전하게 수행
    with lock:
        is_incorrect = False
        if int(prediction) == int(true_label):
            correct += 1
        else:
            incorrect += 1
            is_incorrect = True
            # 오답 이미지를 저장 (고유한 파일명 사용)
            plt.figure(figsize=(2,2))
            plt.imshow(X[int(idx)].reshape(28, 28), cmap='gray')
            plt.axis('off')
            filename = f'static/images/incorrect_{incorrect}.png'
            plt.savefig(filename, bbox_inches='tight', pad_inches=0)
            plt.close()  # 현재 그림 닫기

        # 디버깅 로그
        print(f'Index: {idx}, Prediction: {int(prediction)}, True Label: {int(true_label)}, Correct: {correct}, Incorrect: {incorrect}')

    # 결과 반환
    return jsonify({
        'prediction': int(prediction),
        'true_label': int(true_label),
        'correct': correct,
        'incorrect': incorrect,
        'is_incorrect': is_incorrect
    })

@app.route('/reset', methods=['POST'])
def reset():
    global correct, incorrect

    with lock:
        correct = 0
        incorrect = 0
        # 오답 이미지를 저장할 폴더의 내용을 삭제
        images_folder = 'static/images'
        for filename in os.listdir(images_folder):
            file_path = os.path.join(images_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

    # 디버깅 로그
    print('Testing has been reset.')

    return jsonify({
        'message': 'Testing has been reset.',
        'correct': correct,
        'incorrect': incorrect
    })

if __name__ == '__main__':
    app.run(debug=True)
