import { sendAction } from "./server.js";
import {
    chatData,
    formatMessage,
    printMessage,
    initializeChatListener,
} from "./chat.js";
import { vector } from "./vectors.js"
import * as Vec from "./vectors.js"
import { RenderContext, World, Entity, Action } from "./domain.js";
import { drawRect, drawGrid } from "./draw.js"; 

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

    let getRenderContext = (entities: Entity[]): RenderContext => {
        let player = world.entities.find(e=> e.client_id == socket.id);
        let viewCenter = vector(4,3);
        let cameraWorld = player ? player.position : viewCenter;
        return {canvas, ctx, camera: {position: cameraWorld, viewOffset: viewCenter}};
    }
    
    document.addEventListener("keydown", (e) => { sendAction(socket, handleInput(e)) }, false);
    socket.on('world', (state: World) => {
        world = state;
        update(getRenderContext(state.entities), world, scale, socket.id);
    });
    // Load chat messages from the initial data (if any)
    const chatMessages: HTMLElement[] = chatData.map(msg => formatMessage(msg));
    chatMessages.forEach(msg => printMessage(msg));

    // Boot the chat system
    initializeChatListener(socket);
    // listen for mid-update actions performed by other players
    socket.on('view', (actionEvent: { entity: Entity, action: Action }) => {
        let entity = world.entities.find(e=> e.client_id == actionEvent.entity.client_id);
        if(entity){
            entity.current_action = actionEvent.action;
        }
        update(getRenderContext(world.entities), world, scale, socket.id);
    });
}


function update(c: RenderContext, world: World, scale: number, clientId?: string) {
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
