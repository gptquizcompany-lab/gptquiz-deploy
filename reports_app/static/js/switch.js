const tabs = document.querySelectorAll(".tabs button");
const contents = document.querySelectorAll(".tab-content");
const roomId = document.getElementById("room_id").value;
const select = document.querySelector("#selectedOptionGraphic");

let currentPage = "general";


function switchTab(tab) {
    if (tab === currentPage) return;

    tabs.forEach(btn => {
        btn.classList.toggle("selected", btn.dataset.tab === tab);
        btn.classList.toggle("not", btn.dataset.tab !== tab);
    });
    contents.forEach(tg => {
        tg.classList.toggle("hide", tg.dataset.content !== tab);
    });

    if (tab === "graphic") {
        triggerChart(select.value);
    } else if (tab === "questions") {
        loadQuestions(roomId);
    }

    currentPage = tab;
}

tabs.forEach(btn => btn.addEventListener("click", () => switchTab(btn.dataset.tab)));