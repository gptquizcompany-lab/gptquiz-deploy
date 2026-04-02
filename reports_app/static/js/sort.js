document.addEventListener("DOMContentLoaded", function () {
	let ascending = true;

	const sortBtn = document.getElementById("sortBtn");
	const container = document.getElementById("studentsContainer");

	if (!sortBtn || !container) return;

	sortBtn.textContent = ascending ? "<" : ">";

	sortBtn.addEventListener("click", () => {
		const students = Array.from(
			container.querySelectorAll(".student-card"),
		);

		students.sort((a, b) => {
			const getPercent = (el) => {
				const node = el.querySelector(".percent");
				if (!node) return 0;
				const digits = node.textContent.replace(/\D/g, "");
				return parseInt(digits || "0", 10);
			};

			const percentA = getPercent(a);
			const percentB = getPercent(b);

			return ascending ? percentA - percentB : percentB - percentA;
		});

		students.forEach((student) => container.appendChild(student));

		ascending = !ascending;
		sortBtn.textContent = ascending ? "<" : ">";
	});
});
