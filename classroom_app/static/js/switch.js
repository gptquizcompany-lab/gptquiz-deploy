const tabs = document.querySelectorAll(".tab");
const contents = document.querySelectorAll(".tab-content");

let currentPage = "general";

function switchTab(tab) {
	if (tab === currentPage) return;

	tabs.forEach((btn) => {
		btn.classList.toggle("selected", btn.dataset.tab === tab);
		btn.classList.toggle("not", btn.dataset.tab !== tab);
	});
	contents.forEach((tg) => {
		tg.classList.toggle("hide", tg.dataset.content !== tab);
	});

	if (tab === "history") {
		console.log("Hello World!");
	}

	currentPage = tab;
}

tabs.forEach((btn) =>
	btn.addEventListener("click", () => switchTab(btn.dataset.tab)),
);