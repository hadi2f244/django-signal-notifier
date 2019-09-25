let es;
let message_number = 1;
let userID;

function eventListenerInit(user_id) {
    console.log(user_id);
    userID = user_id;
    es = new ReconnectingEventSource(`/objects/${user_id}/events/`);
    es.addEventListener("update", updateNumberNotifications, false);
    let divNumberSelector = document.getElementById("number_notifications");
    divNumberSelector.addEventListener("click",
        e => get_update_messages(e).then(data => addNotificationsMessage(data)),
        false);
}

function updateNumberNotifications(e) {
    let divSelector = document.getElementById("number_notifications");
    let dataJson = JSON.parse(e.data);
    divSelector.innerHTML = `${dataJson.number}<br>`;
}

async function get_update_messages(e) {
    let response = await fetch(`/insite_messaging/update_message/${userID}/`);
    let data = await response.json();
    return data['data']

}

async function seenUpdateMessage(messageID) {
    var xhr = new XMLHttpRequest();
    xhr.open("DELETE", `/insite_messaging/update_message/${userID}/${messageID}/`, true);
    xhr.onload = function (e) {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                console.log(xhr.responseText);
            } else {
                console.error(xhr.statusText);
            }
        }
    };
    xhr.onerror = function (e) {
        console.error(xhr.statusText);
    };
    xhr.send(null);
}

function addNotificationsMessage(data) {
    let divNotificationsMessages = document.getElementById("notifications_box");
    divNotificationsMessages.innerHTML = "";
    console.log(data);
    if (Object.keys(data).length > 0) {
        Object.keys(data).forEach(key => addNotificationMessage(divNotificationsMessages, key, data[key].guid, data[key].context));
        addFooterNotificationsMessages(divNotificationsMessages, Object.keys(data).length);
        divNotificationsMessages.style['display'] = 'block';
        seenUpdateMessage(0).then(e => console.log("Delete success"));
    } else {
        divNotificationsMessages.innerText = "No messages";
        divNotificationsMessages.style['display'] = 'block';
    }
}

function addNotificationMessage(divBase, key, uuid, context) {
    let divNotificationMessage = document.createElement("div",);
    divNotificationMessage.className = "notification_message_box";

    // create and add notification_context
    let notification_context = document.createElement("p");
    notification_context.className = "notification_context";
    notification_context.innerText = `${context}`;
    divNotificationMessage.appendChild(notification_context);

    divNotificationMessage.setAttribute("name", `notification_${key}`);
    divNotificationMessage.setAttribute("uuid", `${uuid}`);

    if (key !== '0') {
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
        seenUpdateMessage(message_number);
        document.getElementById("status_span_notification").innerText = `${message_number} of ${length}`;
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