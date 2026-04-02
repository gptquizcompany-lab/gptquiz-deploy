const btns = document.querySelectorAll("#add");
const forms = document.querySelectorAll(".create-form");
const blurr = document.getElementById("blur");
const closebtn = document.querySelectorAll(".close");

btns.forEach((btn) => {
	btn.addEventListener("click", () => {
		console.log(btn.dataset);
		const form = document.querySelector(`.create-form[data-content="${btn.dataset.label}"]`);
		form.classList.remove("hideform");
		blurr.classList.remove("hideform");
	});
});

closebtn.forEach((btn) => {
	btn.addEventListener("click", () => {
		const form = document.querySelector(`.create-form:not(.hideform)`);
		form.classList.add("hideform");
		blurr.classList.add("hideform");
	});
});
blurr.addEventListener("click", () => {
	const form = document.querySelector(`.create-form:not(.hideform)`);
	if (form) {
		form.classList.add("hideform");
	}
	blurr.classList.add("hideform");
});