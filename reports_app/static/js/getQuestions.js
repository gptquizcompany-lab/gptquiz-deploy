function renderQuestions(questions) {
	const container = document.querySelector(".questions-container");
	container.innerHTML = "";

	questions.forEach((q, index) => {
		const block = document.createElement("div");

		let variantsHTML = "";

		q.variants.forEach((variant) => {
			variantsHTML += `<div class="question-block">
                <p>${variant}</p>
            </div>`;
		});

		block.innerHTML = `
            <h3>${index + 1}. ${q.question_text}</h3>
            <p>Варіанти відповіді:</p>
            <div class="questions-block">
                ${variantsHTML}
            </div>
            <div class="progress-bar">
                ${q.percentage.correct !== 0 ? `<div class="progress correct-bar" style="width: ${q.percentage.correct}%"></div>` : ""}
                ${q.percentage.incorrect !== 0 ? `<div class="progress incorrect-bar" style="width: ${q.percentage.incorrect}%"></div>` : ""}
                ${q.percentage.skipped !== 0 ? `<div class="progress skipped-bar" style="width: ${q.percentage.skipped}%"></div>` : ""}
            </div>
            <div class="numbers">
                <div class="number-container">
                    <span>${q.numbers.correct}</span>
                    <p>правильних</p>
                </div>
                <div class="number-container">
                    <span>${q.numbers.incorrect}</span>
                    <p>неправильних</p>
                </div>
                <div class="number-container">
                    <span>${q.numbers.skipped}</span>
                    <p>пропущених</p>
                </div>
            </div>
        `;

		container.appendChild(block);
	});
}

function loadQuestions() {
	fetch(`/reports/${roomId}/questions`)
		.then((response) => {
			if (!response.ok) {
				throw new Error("Ошибка загрузки");
			}
			return response.json();
		})
		.then((data) => {
			renderQuestions(data);
		})
		.catch((error) => {
			console.error("Fetch error:", error);
		});
}
