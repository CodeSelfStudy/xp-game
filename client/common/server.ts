import { Action } from "./domain.js";

type ClientEvent = {
    kind: "login" 
    detail:  {character_name: string}
}

export function sendAction(socket: any, action: Action){
    socket.emit('action', action);
}

export function requestLogin(socket: any, username: string){
    let event: ClientEvent ={
        kind: "login",
        detail: {
            character_name: username
        }
    };
    socket.emit('event', event);
}

export function sendChatMessage(socket: any, message: string){
    socket.emit("chat", {
        body: message,
    });
}
