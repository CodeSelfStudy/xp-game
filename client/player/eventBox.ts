import { Message } from "./chat.js";
import { sanitize } from "./sanitizer.js";

// TODO define these
export enum EventType {
    ChatMessage,
    // ActionMessage, ?
}

/**
 * Take a string and event type. Print to the event box.
 */
export function printMessage(
    content: Message, // add other allowed types here
    eventType: EventType,
    targetId: string = "messages"
): void {
    const messageOutputArea = document.getElementById(targetId);

    // Create the HTML based on the event type (see private functions
    // below).
    let html: HTMLElement | null = null;
    switch(eventType) {
        case EventType.ChatMessage:
            html = formatChatMessage(content);
            break;
    }

    // append the HTML to the DOM
    messageOutputArea.appendChild(html);
    scrollMessages();
}

/**
 * Scroll the latest chat message into view.
 *
 * TODO: this should probably do this on initial load (if there are
 * pre-loaded event messages), and _not_ scroll when the user has
 * intentionally scrolled up and is trying to read old event messages.
 */
function scrollMessages(): void {
    const container = document.querySelector("#chat #messages");
    const messages = document.querySelectorAll("#chat .message");

    container.scrollTop = container.scrollHeight;
}


// The templating functions should sanitize the user-created string.

/**
 * Take in a `Message` object and return an HTML element with the chat
 * message.
 */
function formatChatMessage(data: Message): HTMLElement {
    const div = document.createElement("div");
    div.classList.add("message");

    const cleanedBody = sanitize(data.body);

    // TODO: a username or user ID would be better than a sliced random
    // ID here.
    div.innerHTML = `
        <span class="username">${data.id.slice(
            -7
        )}</span> <span class="message-body">${cleanedBody}</span>
    `;
    return div;
}
