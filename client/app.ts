import { sendMessage } from "./server.js";
declare var io: any;

type Canvas = {
    canvas: HTMLCanvasElement,
    ctx: CanvasRenderingContext2D
}

type Action = "Up" | "Down" | "Left" | "Right";

type Vector = { x: number, y: number }

type World = {
    width: number;
    height: number;
    entities: Entity[];
}

type Entity = {
    position: Vector;
    client_id: string;
}

export function initialize(){
    var socket = io('http://localhost:5000');
    let clientId: string;
    socket.on('connect', () => {
        sendMessage(socket, "connected")
        clientId = socket.id;
    });
    let scale = 50;
    const canvas = <HTMLCanvasElement>document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    let world: World = {
        width: 100,
        height: 100,
        entities: []
    };
    document.addEventListener("keydown", (e) => { sendMessage(socket, handleInput(e)) }, false);
    socket.on('world', (state: World) => { world = state; });
    setInterval(() => update({canvas, ctx}, world, scale), 100, clientId);
}

function update(c: Canvas, world: World, scale: number, clientId?: string) {
    c.ctx.clearRect(0,0, c.canvas.width, c.canvas.height);
    drawGrid(c, scale);
    world.entities.forEach((e) => {
        draw(c, e, scale, clientId);
    })
}

function drawGrid(c: Canvas, scale: number){
    function drawGridline(x1: number, y1: number, x2: number, y2: number){
        c.ctx.beginPath();
        c.ctx.moveTo(x1, y1);
        c.ctx.lineTo(x2, y2);
        c.ctx.stroke();
        c.ctx.closePath();
    }
    
    var n = scale;
    while(true){
        if(n >= c.canvas.width && n >= c.canvas.height){
            break;
        }

        if(scale < c.canvas.width){ 
            drawGridline(n, 0, n, c.canvas.height);
        }
        if(scale < c.canvas.height){ 
            drawGridline(0, n, c.canvas.width, n);
        }
        n += scale;
    }
}

function draw(c: Canvas, thing: Entity, scale: number, clientId: string){
    c.ctx.beginPath()
    c.ctx.rect(thing.position.x*scale, thing.position.y*scale,
               scale, scale);
    c.ctx.fillStyle = clientId == thing.client_id ? "blue" : "red";
    c.ctx.fill();
    c.ctx.closePath();
}

function handleInput(event: KeyboardEvent): Action | undefined {
    switch (event.key) {
        case "ArrowLeft":
            return "Left";
        case "ArrowRight":
            return "Right"
        case "ArrowUp":
            return "Up";
        case "ArrowDown":
            return "Down";
    }
    return undefined;
};


window.addEventListener('load', () => initialize())
