import { Action } from "./domain.js";

export function sendAction(socket: any, action: Action){
    socket.emit('action', action);
}

export function sendChatMessage(socket: any, message: string){
    socket.emit("chat", {
        body: message,
    });
}
