const exitSaveBtn = document.getElementById("SaveAndExit");
const saveForm = document.getElementById("saveForm");
const blurW = document.getElementById("blur");
const deleteReportsBtns = document.querySelectorAll(".delete-report");
const reportName = document.getElementById("reportName");
const saveButton = document.getElementById("saveButton");
const deleteButton = document.getElementById("deleteButton");

deleteReportsBtns.forEach((btn) => {
	btn.addEventListener("click", () => {
		saveForm.classList.add("showform");
		blurW.classList.add("showform");
		reportName.textContent = btn
			.closest(".report")
			.querySelector("h3")
			.textContent.split(": ")[1];
		deleteButton.value = `delete;${btn.closest(".report").querySelector("h3").id.split("-")[1]}`;
	});
});

blurW.addEventListener("click", () => {
	saveForm.classList.remove("showform");
	blurW.classList.remove("showform");
});

document.addEventListener("keydown", (event) => {
	if (event.key === "Escape") {
		saveForm.classList.remove("showform");
		blurW.classList.remove("showform");
	}
});

saveButton.addEventListener("click", () => {
	saveForm.classList.remove("showform");
	blurW.classList.remove("showform");
});
