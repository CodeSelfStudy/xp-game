import { sendAction } from "./server.js";
import {
    chatData,
    formatMessage,
    printMessage,
    initializeChatListener,
} from "./chat.js";
import { vector } from "./vectors.js"
import * as Vec from "./vectors.js"
import { Canvas, World, Entity, Action } from "./domain.js";
import { draw, drawGrid } from "./draw.js"; 

declare var io: any;


export function initialize(){
    var socket = io("http://localhost:5000");
    let scale = 50;
    const canvas = <HTMLCanvasElement>document.getElementById("canvas");
    const ctx = canvas.getContext("2d");
    let world: World = {
        width: 100,
        height: 100,
        entities: []
    };

    document.addEventListener("keydown", (e) => { sendAction(socket, handleInput(e)); }, false);
    socket.on("world", (state: World) => {
        world = state;
        update({canvas, ctx}, world, scale, socket.id);
    });

    // Load chat messages from the initial data (if any)
    const chatMessages: HTMLElement[] = chatData.map(msg => formatMessage(msg));
    chatMessages.forEach(msg => printMessage(msg));

    // Boot the chat system
    initializeChatListener(socket);
    // listen for mid-update actions performed by other players
    socket.on('actions', (actionEvent: { entity: Entity, action: Action }) => {
        let entity = world.entities.find(e=> e.client_id == actionEvent.entity.client_id);
        if(entity){
            entity.current_action = actionEvent.action;
        }
        update({canvas, ctx}, world, scale, socket.id);
    });
}

function update(c: Canvas, world: World, scale: number, clientId?: string) {
    c.ctx.clearRect(0,0, c.canvas.width, c.canvas.height);
    let player = world.entities.find(e=> e.client_id == clientId);
    let viewCenter = vector(4,3);
    let cameraWorld = player ? player.position : viewCenter;
    let viewOffset = Vec.subtract(cameraWorld, viewCenter);
    drawGrid(c, viewOffset, world.width, world.height, scale);
    world.entities.forEach((e) => {
        let localPos = Vec.subtract(e.position, viewOffset);
        let color = clientId == e.client_id ? "blue" : "red";
        draw(c, localPos, color, scale);
    });
}

function handleInput(event: KeyboardEvent): Action | undefined {
    switch (event.key) {
        case "ArrowLeft":
            return { direction: "West", kind: "Move" };
        case "ArrowRight":
            return { direction: "East", kind: "Move" };
        case "ArrowUp":
            return { direction: "North", kind: "Move" };
        case "ArrowDown":
            return { direction: "South", kind: "Move" };
    }
    return undefined;
}

window.addEventListener("load", () => initialize());
