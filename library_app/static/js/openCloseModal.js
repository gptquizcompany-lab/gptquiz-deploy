const exitSaveBtn = document.getElementById('SaveAndExit')
const deleteBtn = document.getElementById("Delete")
const saveForm = document.getElementById('saveForm')
const deleteForm = document.getElementById('deleteForm')
const blurW = document.getElementById('blur')
const inputImg = document.getElementById('imageQuiz')
const labelImg = document.getElementById('uploadLabel')
const closeBtn = document.getElementById("closeBtn")

exitSaveBtn.addEventListener(
    'click',
    function (){
        saveForm.classList.add('showform')
        blurW.classList.add('showform')
    }
)
deleteBtn.addEventListener(
    'click',
    function (){
        deleteForm.classList.add('showform')
        blurW.classList.add('showform')
    }
)

blurW.addEventListener('click', () => {
    deleteForm.classList.remove("showform")
    saveForm.classList.remove('showform')
    blurW.classList.remove('showform')
})
closeBtn.addEventListener('click', () => {
    deleteForm.classList.remove("showform")
    blurW.classList.remove('showform')
})



inputImg.addEventListener('change', event => {
    const reader = new FileReader();
    reader.onload = function (event) {
        const imgElement = document.createElement('img');
        imgElement.src = event.target.result;
        labelImg.innerHTML = '';
        labelImg.appendChild(imgElement); 

    };
    reader.readAsDataURL(event.target.files[0]);
})

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        deleteForm.classList.remove("showform")
        saveForm.classList.remove('showform')
        blurW.classList.remove('showform')
    }
});