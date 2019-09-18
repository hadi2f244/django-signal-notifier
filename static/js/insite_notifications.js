let es;

function eventListenerInit(user_id) {
    console.log(user_id);
    es = new ReconnectingEventSource(`/objects/${user_id}/events/`);
    es.addEventListener("update", updateNumberNotifications, false)
}

function updateNumberNotifications(e) {
    let spanSelector = document.getElementById("number_notifications");
    let dataJson = JSON.parse(e.data);
    spanSelector.innerHTML = `${dataJson.number}<br>`;
}