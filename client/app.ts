import { sendAction, requestLogin } from "./server.js";
import { chatData, initializeChatListener } from "./chat.js";
import { printMessage, EventType } from './eventBox.js';
import { vector, Vector } from "./vectors.js"
import * as Vec from "./vectors.js"
import { RenderContext, World, Entity, Action, ActionKind } from "./domain.js";
import { drawRect, drawGrid, drawTile } from "./draw.js"; 
import { getTileset } from "./tileset.js";
import { setHealth, setUsername } from "./stats.js";
import { sanitize } from "./sanitizer.js";

declare var io: any;

async function initialize(){
    // TODO: loading tiles blocks initialization; put this behind a load screen?
    const tileset = await getTileset();

    var socket = io('/');
    function respawn(){
        handleLogin(name => {
            setUsername(name);
            setHealth(0);
            requestLogin(socket, name);
        });
    }

    socket.on('connect', () => respawn());
    socket.on('despwan', () => respawn());
        
    const canvas = <HTMLCanvasElement>document.getElementById("canvas");
    const ctx = canvas.getContext("2d");
    let world: World = {
        width: 100,
        height: 100,
        entities: [],
        tile_grid: []
    };
    let getRenderContext = (): RenderContext => {
        let player = world.entities.find(e=> e.client_id == socket.id);
        let scale = 50
        let viewCenter = vector((canvas.width/scale/2)-1, (canvas.height/scale/2)-1);
        let cameraWorld = player ? player.position : viewCenter;
        return {
            ctx,
            scale: scale,
            camera: {position: cameraWorld, viewOffset: viewCenter},
            tileset
        };
    };

    // TODO - move to an input handling module that can be initialized here
    document.addEventListener("keydown", (e) => {
        let input = handleKeyDown(e);
        if(input){sendAction(socket, input)}
    }, false);
    document.addEventListener("keypress", handleKeyPress, false);
    socket.on('world', (state: World) => {
        world = state;
        render(getRenderContext(), world);
        let player = world.entities.find(e=> e.client_id == socket.id)
        if(player){
            setHealth(player.health)
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
        render(getRenderContext(), world);
    });
}


function render(c: RenderContext, world: World) {
    c.ctx.clearRect(0,0, c.ctx.canvas.width, c.ctx.canvas.height);
    let cameraOffset = Vec.subtract(c.camera.position, c.camera.viewOffset);
    function worldToView(worldPosition: Vector): Vector {
        return Vec.subtract(worldPosition, cameraOffset);
    }
    function viewToWorld(viewPosition: Vector): Vector {
        return Vec.add(viewPosition, cameraOffset);
    }

    // Layer 1: Terrain
    for(var y = 0; y < c.ctx.canvas.height/c.scale; y++){
        for(var x = 0; x < c.ctx.canvas.width/c.scale; x++){
            let worldPos = viewToWorld(vector(x, y))
            let inBounds = worldPos.x >= 0 && worldPos.x < world.width
                && worldPos.y >= 0 && worldPos.y < world.height;
            let tileId = inBounds ? world.tile_grid[worldPos.y][worldPos.x].tile_id : "ground";
            drawTile(c, {x, y}, tileId);
            
        }
    }
    // layer 2: gridlines
    drawGrid(c, cameraOffset, world.width, world.height);

    // Layer 3: player entities
    world.entities.forEach((e) => {
        let localPos = worldToView(e.position);
        drawTile(c, localPos, "hero");
        // TODO - split action rendering into a separate layer
        if(e.current_action){
            let actionColor = e.current_action.kind == "Move"
                ? "blue"
                : "red";
            let actionTarget = Vec.add(e.position, Vec.dirToVec(e.current_action.direction));
            drawRect(c, worldToView(actionTarget), {strokeColor:actionColor});
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

/**
 * Present the user with a prompt to enter a user name.  On a valid submission,
 * the prompt is hidden and a the `onLogin` callback is issued with the name
 */
function handleLogin(onLogin: (name: string) => void){
    const loginDiv: HTMLElement = document.getElementById("login");
    loginDiv.style.display = null;
    const loginForm: HTMLElement = document.getElementById("loginForm");
    function subscribe(e: Event){
        e.preventDefault()
        const loginFormMessageInput = <HTMLInputElement>document.getElementById("loginFormInput");
        const name: string = sanitize(loginFormMessageInput.value.trim());
        if(name){
            loginForm.removeEventListener("submit", subscribe)
            loginDiv.style.display = "none";
            onLogin(name);
        }
    }
    loginForm.addEventListener("submit", subscribe)
}


window.addEventListener("load", () => initialize());
