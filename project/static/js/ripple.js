document.addEventListener('click', function (event) {
    const button = event.target.closest('.create-btn-ripple');
    
    if (button) {
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        
        ripple.style.width = ripple.style.height = `${size}px`;
        ripple.style.left = `${event.clientX - rect.left - size / 2}px`;
        ripple.style.top = `${event.clientY - rect.top - size / 2}px`;
        
        ripple.classList.add('ripple-effect');
        button.appendChild(ripple);
      
        ripple.addEventListener('animationend', function () {
            ripple.remove();
        });
    }
});