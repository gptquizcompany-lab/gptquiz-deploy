const imgInput = document.getElementById('imageQuestion');
const img = document.getElementById('imageBtn');

imgInput.addEventListener('change', event => {
   img.src = "/library/images/correct.png" 
});
