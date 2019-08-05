import { sendAction } from "./server.js";
import {
    chatData,
    initializeChatListener,
} from "./chat.js";
import { printMessage, EventType } from './eventBox.js';
import { vector } from "./vectors.js"
import * as Vec from "./vectors.js"
import { RenderContext, World, Entity, Action, ActionKind } from "./domain.js";
import { drawRect, drawGrid } from "./draw.js";

declare var io: any;

export function initialize(){
    var socket = io('/');
    let scale = 50;
    const canvas = <HTMLCanvasElement>document.getElementById("canvas");
    const ctx = canvas.getContext("2d");
    let world: World = {
        width: 100,
        height: 100,
        entities: []
    };

    let getRenderContext = (): RenderContext => {
        let player = world.entities.find(e=> e.client_id == socket.id);
        let viewCenter = vector(4,3);
        let cameraWorld = player ? player.position : viewCenter;
        return {canvas, ctx, camera: {position: cameraWorld, viewOffset: viewCenter}};
    }

    // TODO - move to an input handling module that can be initialized here
    document.addEventListener("keydown", (e) => {
        let input = handleKeyDown(e);
        if(input){sendAction(socket, input)}
    }, false);
    document.addEventListener("keypress", handleKeyPress, false);
    socket.on('world', (state: World) => {
        world = state;
        update(getRenderContext(), world, scale, socket.id);
        if(!world.entities.find(e=> e.client_id == socket.id)){
            sendAction(socket, {"kind": "Spawn"});
        }
    });
    // Load chat messages from the initial data (if any)
    chatData.forEach(msg => printMessage(msg, EventType.ChatMessage));

    // Boot the chat system
    initializeChatListener(socket);
    // listen for mid-update actions performed by other players
    socket.on('view', (actionEvent: { entity: Entity, action: Action }) => {
        let entity = world.entities.find(e=> e.client_id == actionEvent.entity.client_id);
        if(entity){
            entity.current_action = actionEvent.action;
        }
        update(getRenderContext(), world, scale, socket.id);
    });
}


function update(c: RenderContext, world: World, scale: number, clientId?: string) {
    let player = world.entities.find(e=> e.client_id == clientId);
    c.ctx.clearRect(0,0, c.canvas.width, c.canvas.height);
    let cameraOffset = Vec.subtract(c.camera.position, c.camera.viewOffset);
    drawGrid(c, cameraOffset, world.width, world.height, scale);
    world.entities.forEach((e) => {
        let localPos = Vec.subtract(e.position, cameraOffset);
        let color = clientId == e.client_id ? "blue" : "red";
        drawRect(c, localPos, scale, {fillColor: color});
        if(e.current_action){
            let actionColor = e.current_action.kind == "Move"
                ? "blue"
                : "red";
            let actionTarget = Vec.add(e.position, Vec.dirToVec(e.current_action.direction));
            drawRect(c, Vec.subtract(actionTarget, cameraOffset), scale, {strokeColor:actionColor});
        }
    });
}


// TODO - move to an input module
let ATK_PRESSED = false;
function handleKeyPress(event: KeyboardEvent){
    switch (event.key){
        case "a":
        case "A":
            ATK_PRESSED = true;
            break;
    }
}

function handleKeyDown(event: KeyboardEvent): Action | undefined {
    // if the attack button has been pressed, set the action to Attack
    // and clear the ATK_PRESSED input state 
    let action: ActionKind = ATK_PRESSED ? "Attack" : "Move";
    ATK_PRESSED = false;

    switch (event.key) {
        case "ArrowLeft":
            event.preventDefault();
            return { direction: "West", kind: action };
        case "ArrowRight":
            event.preventDefault();
            return { direction: "East", kind: action };
        case "ArrowUp":
            event.preventDefault();
            return { direction: "North", kind: action };
        case "ArrowDown":
            event.preventDefault();
            return { direction: "South", kind: action };
    }
    return undefined;
}


window.addEventListener("load", () => initialize());
