const teacherBtn = document.getElementById("teacher")
const studentBtn = document.getElementById("student")
const btnSubmit = document.getElementById("btnSubmit")
teacherBtn.addEventListener(
    "click",
    event => {
        if (btnSubmit.value === "teacher") {
            return
        }
        console.log(btnSubmit.value)
        teacherBtn.classList.add("selected")
        studentBtn.classList.remove("selected")
        btnSubmit.setAttribute('value', 'teacher')
    }
)
studentBtn.addEventListener(
    "click",
    event => {
        if (btnSubmit.value === "student") {
            return
        }
        teacherBtn.classList.remove("selected")
        studentBtn.classList.add("selected")
        btnSubmit.setAttribute('value', 'student')
    }
)

