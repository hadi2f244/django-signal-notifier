let es;

function eventListenerInit(user_id) {
    console.log(user_id);
    es = new ReconnectingEventSource(`/objects/${user_id}/events/`);
    es.addEventListener("update", updateNumberNotifications, false);
    let divNumberSelector = document.getElementById("number_notifications");
    divNumberSelector.addEventListener("click",
        e => get_update_messages(e, user_id).then(data => addNotificationsMessage(data)),
        false);
}

function updateNumberNotifications(e) {
    let divSelector = document.getElementById("number_notifications");
    let dataJson = JSON.parse(e.data);
    divSelector.innerHTML = `${dataJson.number}<br>`;
}

async function get_update_messages(e, id) {
    let response = await fetch(`/insite_notifications/update_message/${id}/`);
    let data = await response.json();
    return data['data']
}

function addNotificationsMessage(data) {
    let divNotificationsMessages = document.getElementById("notifications_box");
    divNotificationsMessages.innerHTML = "";
    console.log(data);
    Object.keys(data).forEach(key => {
        divNotificationsMessages.innerHTML += `<h2 class="notifications_title">${data[key].title}</h2>`;
        divNotificationsMessages.innerHTML += `<h6 class="notifications_description">${data[key].description}</h6>`;
        console.log(key);
    });
    divNotificationsMessages.style['display'] = 'block'
}