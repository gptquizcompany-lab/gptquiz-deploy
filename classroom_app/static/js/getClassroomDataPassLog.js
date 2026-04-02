const btnCopy = document.getElementById("copy-btn");
const textCopy = document.getElementById("text-copy");
const imageCopy = document.getElementById("img-copy");

btnCopy.addEventListener("click", async () => {
	try {
		btnCopy.style.cursor = "wait";
		btnCopy.disabled = true;
		const response = await fetch(
			`/classrooms/get-login-data-students/${classroomId}`,
		);
		const data = await response.json();
		if (data.status == 403) {
			throw Error(
				`Forbidden (${data.status}): You don't have permissions to get this info`,
			);
		} else if (data.status == 404) {
			throw Error(
				`Not found (${data.status}): classroom not found by this id`,
			);
		} else if (data.status != 200) {
			throw Error(`Internal Server error (${data.status})`);
		}
		await navigator.clipboard.writeText(data.data);
		imageCopy.src = "/host/images/check-mark.svg";
		textCopy.textContent = "Дані студентів скопійовані до буфера обміну!";
		setTimeout(() => {
			imageCopy.src = "/host/images/copy.svg";
			textCopy.textContent = "";
			btnCopy.style.cursor = "pointer";
			btnCopy.disabled = false;
		}, 4000);
	} catch (error) {
		console.error("error", error);
		btnCopy.style.cursor = "pointer";
		btnCopy.disabled = false;
		textCopy.textContent = "Помилка при копіюванні даних студентів!";
	}
});
