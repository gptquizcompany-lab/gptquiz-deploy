const descs = document.querySelectorAll('.quiz-description');

descs.forEach(desc => {
    const text = desc.textContent;
    if (text.length > 60) {
        desc.textContent = text.slice(0, 60) + '...';
    }
});