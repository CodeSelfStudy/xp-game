/**
 * This module contains logic that deals with the chat functionality.
 *
 * Updating the DOM is handled in the eventBox module.
 */
import { sendChatMessage } from "../common/server.js";
import { printMessage, EventType } from './eventBox.js';

// Represents a chat message
export interface Message {
    id: string;
    body: string;
}

// If we need to pre-populate the chat with previous messages, they get
// loaded from here.
export const chatData: Message[] = [
    // TODO change or remove this initial chat message
    {
        id: 'system',
        body: 'You find yourself in a verdant forest...'
    }
];

/**
 * Send new messages
 */
export function initializeChatListener(socket): void {
    const chatForm: HTMLElement = document.getElementById("chatForm");

    chatForm.addEventListener("submit", (e): void => {
        e.preventDefault();
        const chatMessageInput = <HTMLInputElement>(
            document.getElementById("chatMessageInput")
        );
        const chatMessage: string = chatMessageInput.value.trim();
        chatMessageInput.value = "";
        if (chatMessage) {
            sendChatMessage(socket, chatMessage);
        }
    });

    socket.on("chat", (message): void => {
        console.log("from server:", message);
        printMessage(message, EventType.ChatMessage);
    });
}
