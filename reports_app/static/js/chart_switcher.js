document.addEventListener("DOMContentLoaded", function () {
    const select = document.querySelector("#selectedOptionGraphic");
    if (!select) return;

    select.addEventListener("change", function () {
        const roomId = document.querySelector("#room_id").value;
        document.querySelector("#questionsChart").innerHTML = "";

        if (this.value === "successful") {
            loadRoomStats(roomId);
        } else if (this.value === "timeSpent") {
            loadTimeStats(roomId);
        }
    });
});

function triggerChart(value) {
    const roomId = document.querySelector("#room_id").value;
    if (!document.querySelector("#questionsChart").innerHTML.trim()) {
        if (value === "successful") {
            loadRoomStats(roomId);
        } else if (value === "timeSpent") {
            loadTimeStats(roomId);
        }
    }
}