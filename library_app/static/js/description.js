const descs = document.querySelectorAll('.desc');

descs.forEach(desc => {
    const text = desc.textContent;
    if (text.length > 125) {
        desc.textContent = text.slice(0, 125) + '...';
    }
});