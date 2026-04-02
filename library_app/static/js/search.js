document.getElementById('searchForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const searchText = document.getElementById('searchInput').value;

    const response = await fetch('/search-library/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ search: searchText })
    });

    const data = await response.json();
    const container = document.querySelector('.quizes');
    container.innerHTML = '';

    if (data.length === 0) {
        container.innerHTML = '<h4 style="color: white;">Нічого не знайдено</h4>';
        return;
    }

    data.forEach(quiz => {
        const el = document.createElement('a');
        el.className = 'quiz';
        el.href = `/host/${quiz.id}`;
        el.innerHTML = `
            <img src="/library/${quiz.image}" alt="">
            <div class="quiz-info">
                <h3>${quiz.name}</h3>
                <div>
                    <p class="desc">${quiz.description}</p>
                    <hr>
                    <p>${quiz.count_questions} Запитань</p>
                    <hr>
                    <p>Було використано для <br> проходженння: ${quiz.codes.length}</p>
                </div>
            </div>
        `;
        container.appendChild(el);
    });
});