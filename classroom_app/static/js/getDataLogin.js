const btn1 = document.getElementById("getDataLogin");
const closebtnMode = document.getElementById("okbtn");
const modalInfo = document.getElementById("modalInfo");
const loginSpan = document.getElementById("login");
const passwordSpan = document.getElementById("password");
const classroomId = document.getElementById("classroomId").value;
const copyBtn = document.getElementById("copybtn");
const blurrr = document.getElementById("blur");

btn1.addEventListener("click", async () => {
	const idStudent = btn1.value;
	try {
		btn1.style.cursor = "wait";
		btn1.disabled = true;
		const response = await fetch(
			`/classrooms/get-student-info/${idStudent}/${classroomId}`,
		);
		const data = await response.json();
		if (data.status == 403) {
			throw Error(
				`Forbidden (${data.status}): You don't have permissions to get this info`,
			);
		} else if (data.status == 404) {
			throw Error(
				`Not found (${data.status}): Student not found by this id`,
			);
		} else if (data.status != 200) {
			throw Error(`Internal Server error (${data.status})`);
		}
		const login = data.login;
		const password = data.password;
		loginSpan.textContent = login;
		passwordSpan.textContent = password;
		copyBtn.onclick = async () => {
			await navigator.clipboard.writeText(
				`Логін: ${login}\nПароль: ${password}`,
			);
			copyBtn.querySelector("img").src = "/host/images/check-mark.svg";
			setTimeout(() => {
				copyBtn.querySelector("img").src = "/host/images/copy.svg";
			}, 2000);
		};
		blurrr.classList.remove("hideform");
		modalInfo.classList.remove("hideform");
		btn1.style.cursor = "pointer";
		btn1.disabled = false;
	} catch (error) {
		console.error("error", error);
		btn1.style.cursor = "pointer";
		btn1.disabled = false;
	}
});

closebtnMode.addEventListener("click", () => {
	blurrr.classList.add("hideform");
	modalInfo.classList.add("hideform");
	loginSpan.textContent = "";
	passwordSpan.textContent = "";
});
blurrr.addEventListener("click", () => {
	blurrr.classList.add("hideform");
	modalInfo.classList.add("hideform");
});
