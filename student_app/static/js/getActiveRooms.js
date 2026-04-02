const POLL_INTERVAL = 20_000;
let pollingTimer = null;

function getAnswerText(n) {
	if (n === 0) return `${n} учасників`;
	const lastDigit = n % 10;
	const lastTwoDigits = n % 100;
	if (lastDigit === 1 && lastTwoDigits !== 11) {
		return `${n} учасник`;
	} else if (lastDigit >= 2 && lastDigit <= 4 && (lastTwoDigits < 10 || lastTwoDigits >= 20)) {
		return `${n} учасники`;
	} else {
		return `${n} учасників`;
	}
}

async function fetchActiveQuizes(classroomId) {
	try {
		const res = await fetch(`/student/get_active_quizes/${classroomId}`);
		const data = await res.json();
		renderActiveQuizes(data);
	} catch (err) {
		console.error("Ошибка при получении квизов:", err);
	}
}

function renderActiveQuizes(data) {
	const container = document.getElementById("activeQuizes");
    container.innerHTML = ""

	if (data.status !== 200 || !data.response.length) {
		return;
	}
    container.innerHTML = "<h3>Знайдено запущені вікторини!</h3>"
	container.innerHTML += data.response.map(
			(quiz) => `
                <div class="quiz-card">
                    <p class="quiz-topic">${quiz.topic}</p>
                    <div class="quiz-meta">
                        <span class="badge badge-q">${quiz.text}</span>
                        <span class="badge badge-s">${getAnswerText(quiz.count_students)}</span>
                    </div>
                    <a class="join-btn" href="/execution?code=${quiz.code}">Приєднатися →</a>
                </div>
            `,
		).join("");
    container.innerHTML += "<hr>"
}

function startPolling(classroomId) {
	fetchActiveQuizes(classroomId);
	pollingTimer = setInterval(() => {
		fetchActiveQuizes(classroomId);
	}, POLL_INTERVAL);
}

function stopPolling() {
	if (pollingTimer) {
		clearInterval(pollingTimer);
		pollingTimer = null;
	}
}

startPolling(document.getElementById("classroomId").value);
window.addEventListener("beforeunload", stopPolling);
