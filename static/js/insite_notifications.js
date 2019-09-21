let es;
let message_number = 1;
let messages_read = new Set([1]);

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
        addNotificationMessage(divNotificationsMessages, key, data[key].title, data[key].description);
        console.log(key);
    });
    addFooterNotificationsMessages(divNotificationsMessages, Object.keys(data).length);
    divNotificationsMessages.style['display'] = 'block'
}

function addNotificationMessage(divBase, key, title, description) {
    let divNotificationMessage = document.createElement("div",);
    divNotificationMessage.className = "notification_message_box";

    // create and add notification_title
    let notification_title = document.createElement("h3");
    notification_title.className = "notification_title";
    notification_title.innerText = `${title}`;
    divNotificationMessage.appendChild(notification_title);

    // create and add notification_description
    let notification_description = document.createElement("h5");
    notification_description.className = "notification_description";
    notification_description.innerText = `${description}`;
    divNotificationMessage.appendChild(notification_description);

    divNotificationMessage.setAttribute("name", `notification_${key}`);
    if (key !== '1') {
        divNotificationMessage.style['display'] = "none"
    }
    divBase.appendChild(divNotificationMessage);
}

function addFooterNotificationsMessages(divBase, length) {

    // create and add next button
    let nextButton = document.createElement("button");
    nextButton.className = "next_button_style";
    nextButton.innerText = ">";
    nextButton.addEventListener("click", e => nextButtonClick(length), false);
    divBase.appendChild(nextButton);

    // create and add next button
    let backButton = document.createElement("button");
    backButton.className = "back_button_style";
    backButton.innerText = "<";
    backButton.addEventListener("click", e => backButtonClick(length), false);
    divBase.appendChild(backButton);

    // create and add status span
    let statusSpan = document.createElement("span");
    statusSpan.className = "status_span";
    statusSpan.setAttribute("id", "status_span_notification");
    statusSpan.innerText = `1 of ${length}`;
    divBase.appendChild(statusSpan);
}

function nextButtonClick(length) {
    if (message_number < length) {
        document.getElementsByName(`notification_${message_number}`)[0].style['display'] = "none";
        document.getElementsByName(`notification_${message_number + 1}`)[0].style['display'] = "block";
        message_number += 1;
        messages_read.add(message_number);
        document.getElementById("status_span_notification").innerText = `${message_number} of ${length}`;
        console.log(messages_read)
    }
}

function backButtonClick(length) {
    if (message_number > 0) {
        document.getElementsByName(`notification_${message_number}`)[0].style['display'] = "none";
        document.getElementsByName(`notification_${message_number - 1}`)[0].style['display'] = "block";
        message_number -= 1;
        document.getElementById("status_span_notification").innerText = `${message_number} of ${length}`;
    }
}