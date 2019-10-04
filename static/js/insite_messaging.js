class InsiteMessaging {
    defaultOptions = {
        notificationNumberElement: document.getElementById("number_notifications"),
        notificationBoxElement: document.getElementById("notifications_box"),
        divNotificationMessageClass: "notification_message_box",
        notificationContextClass: "notification_context",
        nextButtonClass: "next_button_style",
        backButtonClass: "back_button_style",
        statusSpanClass: "status_span",
        closeNotificationsButtonClass: "close_button",

    };

    constructor(userId, options = {}) {
        this.userID = userId;
        this.messageNumber = 0;
        let es = new ReconnectingEventSource(`/objects/${this.userID}/events/`);
        es.addEventListener("update", e => this.updateNumberNotifications(this, e), false);
        if (options) {
            Object.keys(this.defaultOptions).forEach(key => {
                if (options.hasOwnProperty(key)) {
                    this.defaultOptions[key] = options[key]
                }
            })
        }
        this.defaultOptions.notificationNumberElement.addEventListener("click",
            e => this.getUpdateMessages(e).then(data => this.addNotificationsMessage(data)),
            false);
    }

    updateNumberNotifications(self, e) {
        let dataJson = JSON.parse(e.data);
        self.defaultOptions.notificationNumberElement.innerHTML = `${dataJson.number}<br>`;
    }

    async getUpdateMessages(e) {
        let response = await fetch(`/insite_messaging/messages/unread/`);
        let data = await response.json();
        return data['data']
    }

    async seenUpdateMessage(messageID) {
        var xhr = new XMLHttpRequest();
        xhr.open("DELETE", `/insite_messaging/messages/${messageID}/`, true);
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

    addNotificationsMessage(data) {
        this.defaultOptions.notificationBoxElement.innerHTML = "";
        if (data.length > 0) {
            data.forEach((message, i) => this.addMessage(i, message.uid, message.context));
            this.addFooterNotificationsMessage(data.length);
            this.addCloseNotificationsButton();
            this.defaultOptions.notificationBoxElement.removeAttribute("hidden");
            this.seenUpdateMessage(data[0].uid).then(e => console.log("Message read"));
        } else {
            this.defaultOptions.notificationBoxElement.innerText = "No messages";
            this.addCloseNotificationsButton();
            this.defaultOptions.notificationBoxElement.removeAttribute("hidden");
        }
    }

    addMessage(key, uid, context) {
        let divNotificationMessage = document.createElement("div",);
        divNotificationMessage.className = this.defaultOptions.divNotificationMessageClass;

        // create and add notification_context
        let notification_context = document.createElement("p");
        notification_context.className = this.defaultOptions.notificationContextClass;
        notification_context.innerText = `${context}`;
        divNotificationMessage.appendChild(notification_context);

        divNotificationMessage.setAttribute("name", `notification_${key}`);
        divNotificationMessage.setAttribute("uuid", `${uid}`);

        if (key !== 0) {
            divNotificationMessage.hidden = true;
        }

        this.defaultOptions.notificationBoxElement.appendChild(divNotificationMessage);
    }

    addFooterNotificationsMessage(length) {

        // create and add next button
        let nextButton = document.createElement("button");
        nextButton.className = this.defaultOptions.nextButtonClass;
        nextButton.innerText = ">";
        nextButton.addEventListener("click", e => this.nextButtonClick(length), false);
        this.defaultOptions.notificationBoxElement.appendChild(nextButton);

        // create and add next button
        let backButton = document.createElement("button");
        backButton.className = this.defaultOptions.backButtonClass;
        backButton.innerText = "<";
        backButton.addEventListener("click", e => this.backButtonClick(length), false);
        this.defaultOptions.notificationBoxElement.appendChild(backButton);

        // create and add status span
        let statusSpan = document.createElement("span");
        statusSpan.className = this.defaultOptions.statusSpanClass;
        statusSpan.setAttribute("id", "status_span_notification");
        statusSpan.innerText = `1 of ${length}`;
        this.defaultOptions.notificationBoxElement.appendChild(statusSpan);
    }

    nextButtonClick(length) {
        if (this.messageNumber < length - 1) {
            document.getElementsByName(`notification_${this.messageNumber}`)[0].hidden = true;
            this.messageNumber += 1;
            let newNotificationElement = document.getElementsByName(`notification_${this.messageNumber}`)[0];
            newNotificationElement.hidden = false;
            let messageId = newNotificationElement.getAttribute("uuid");
            this.seenUpdateMessage(messageId);
            document.getElementById("status_span_notification").innerText = `${this.messageNumber + 1} of ${length}`;
        }
    }

    backButtonClick(length) {
        if (this.messageNumber > 0) {
            document.getElementsByName(`notification_${this.messageNumber}`)[0].hidden = true;
            this.messageNumber -= 1;
            document.getElementsByName(`notification_${this.messageNumber}`)[0].hidden = false;
            document.getElementById("status_span_notification").innerText = `${this.messageNumber + 1} of ${length}`;
        }
    }

    addCloseNotificationsButton() {
        let closeButton = document.createElement("div");
        closeButton.className = this.defaultOptions.closeNotificationsButtonClass;
        closeButton.innerText = "x";
        closeButton.addEventListener('click', e => this.defaultOptions.notificationBoxElement.hidden = true, false);
        this.defaultOptions.notificationBoxElement.appendChild(closeButton);
    }

}
