const quizesContainer = document.querySelector('.quizes > div')
const leftBtn = document.querySelector('.scroll-left-btn')
const rightBtn = document.querySelector('.scroll-right-btn')

leftBtn.onclick = () => {
    quizesContainer.scrollBy({ left: -238, behavior: 'smooth' })
    setTimeout(updateButtons, 300)
}

rightBtn.onclick = () => {
    quizesContainer.scrollBy({ left: 238, behavior: 'smooth' })
    setTimeout(updateButtons, 300)
}

let scrollAmount = 0
let isScrolling = false

quizesContainer.addEventListener('wheel', e => {
    e.preventDefault()
    scrollAmount += e.deltaY
    if (!isScrolling) smoothScroll()
})

function smoothScroll() {
    isScrolling = true
    const step = scrollAmount * 0.1
    quizesContainer.scrollLeft += step
    scrollAmount -= step
    if (Math.abs(scrollAmount) > 0.5) {
        requestAnimationFrame(smoothScroll)
    } else {
        isScrolling = false
        scrollAmount = 0
    }
    updateButtons()
}

function updateButtons() {
    const maxScroll = quizesContainer.scrollWidth - quizesContainer.clientWidth
    leftBtn.style.display = quizesContainer.scrollLeft <= 0 ? 'none' : 'block'
    rightBtn.style.display = quizesContainer.scrollLeft >= maxScroll - 1 ? 'none' : 'block'
}

quizesContainer.addEventListener('scroll', updateButtons)
window.addEventListener('load', updateButtons)