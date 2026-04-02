document
.getElementById("searchForm")
.addEventListener("submit", async function (e) {
    e.preventDefault();

    const searchText = document.getElementById("searchInput").value;

    const response = await fetch("/search-quizes/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ search: searchText }),
    });

    const data = await response.json();
    const container = document.querySelector(".quizes");
    container.innerHTML = "";

    if (data.length === 0) {
        container.innerHTML =
            '<h4 style="color: white;">Нічого не знайдено</h4>';
        return;
    }

    data.forEach((quiz) => {
        const el = document.createElement("a");
        el.className = "quiz";
        el.href = `/host/${quiz.id}`;
        el.innerHTML = `
        <img src="/library/${quiz.image}">
        <h3>${quiz.name}</h3>
        <p class="quiz-description">${quiz.description}</p>
        <hr>
        <p>${quiz.count_questions} запитань</p>
        <p>Автор: ${quiz.author?.surname || ""} ${quiz.author?.name || ""}</p>
    `;
        container.appendChild(el);
    });
});
