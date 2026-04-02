const descs = document.querySelectorAll('.description');

descs.forEach(desc => {
    const text = desc.textContent;
    if (text.length > 90) {
        desc.textContent = text.slice(0, 90) + '...';
    }
});