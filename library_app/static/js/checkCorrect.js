const checkboxes = document.getElementsByClassName("correct-answer");
const input = document.getElementById('enterAnswer')
const button = document.getElementsByClassName("button-save")[0];
function updateButtonState() {
    const isChecked = Array.from(checkboxes).some(cb => cb.checked);

    if (isChecked) {
        button.disabled = false;
    } else {
        button.disabled = true;
    }
}
Array.from(checkboxes).forEach(cb => cb.addEventListener("change", updateButtonState));
input.addEventListener("input", () => {
    if(input.value.trim() == ""){
        button.disabled = true;

    }
    else{
        button.disabled = false;
    }
    
});