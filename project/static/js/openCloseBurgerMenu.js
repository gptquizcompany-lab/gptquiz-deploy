const burgerBtn = document.getElementById("burgerMenuBtn")
const burgerBtnImg = burgerBtn.querySelector("img")
const burgerBlur = document.getElementById("blurrr")
const aside = document.getElementById("aside")
let opened = false

burgerBtn.onclick = () => {
    if (opened) {
        aside.classList.remove("opened")
        burgerBlur.classList.remove("opened")
        burgerBtnImg.src = "/static/images/menu.svg"
    } else {
        aside.classList.add("opened")
        burgerBlur.classList.add("opened")
        burgerBtnImg.src = "/static/images/cross.svg"
    }
    opened = !opened
}