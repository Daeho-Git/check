let currentIndex = 0; // 현재 테스트 중인 데이터 인덱스
let intervalId;       // 인터벌 ID 저장

// 그래프 업데이트 함수
const updateGraph = (correct, incorrect) => {
    const graphDiv = document.getElementById('graph');
    if (!graphDiv) {
        console.error("Graph container not found");
        return;
    }
    const data = [{
        x: ['Correct', 'Incorrect'],
        y: [correct, incorrect],
        type: 'bar'
    }];
    const layout = {
        title: 'Prediction Accuracy',
        xaxis: { title: 'Categories' },
        yaxis: { title: 'Count' }
    };
    Plotly.newPlot('graph', data, layout);
};

// MNIST 전체 데이터 테스트 함수
const startTesting = async () => {
    const totalSamples = 70000; // MNIST 전체 데이터 (70,000개)

    // 10ms 간격으로 예측 실행
    intervalId = setInterval(async () => {
        if (currentIndex >= totalSamples) {
            clearInterval(intervalId); // 모든 테스트가 완료되면 중단
            alert('All test samples have been processed!');
            return;
        }

        console.log(`Testing sample index: ${currentIndex}`); // 디버깅 로그

        try {
            // 예측 요청
            const predictionResponse = await fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ index: currentIndex })
            });

            if (!predictionResponse.ok) {
                throw new Error("Prediction API error");
            }

            const result = await predictionResponse.json();

            // 그래프 업데이트
            console.log("Graph data:", result.correct, result.incorrect); // 디버깅 로그
            updateGraph(result.correct, result.incorrect);

            // 오답 이미지 업데이트
            if (result.incorrect > 0) {
                const incorrectContainer = document.getElementById('incorrect-container');
                if (!incorrectContainer) {
                    console.error("Incorrect container not found");
                    return;
                }

                const existingImg = document.getElementById(`incorrect-img-${result.incorrect}`);
                if (!existingImg) {
                    const img = document.createElement('img');
                    img.id = `incorrect-img-${result.incorrect}`;
                    img.src = `/static/images/incorrect_${result.incorrect}.png`;
                    img.alt = `Incorrect Prediction ${result.incorrect}`;
                    img.width = 100;
                    incorrectContainer.appendChild(img);
                }
            }

            currentIndex++; // 다음 데이터로 이동
        } catch (error) {
            console.error("Error during testing:", error);
        }
    }, 10); // 10ms 간격
};

// "Start Testing" 버튼 클릭 시 테스트 시작
document.getElementById('test-button').onclick = () => {
    console.log("Start Testing button clicked"); // 디버깅 로그 추가
    if (currentIndex === 0) { // 처음부터 시작
        startTesting();
    }
};

// 초기 그래프
updateGraph(0, 0);
