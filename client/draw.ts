import { RenderContext } from "./domain.js";
import { Vector, vector } from "./vectors.js";
import * as Vec from "./vectors.js";
 

export function drawGrid(c: RenderContext, viewOffset: Vector, width: number, height: number){
    function drawGridline(x1: number, y1: number, x2: number, y2: number){
        c.ctx.beginPath();
        c.ctx.strokeStyle = "black";
        c.ctx.lineWidth = 1;
        c.ctx.moveTo(x1, y1);
        c.ctx.lineTo(x2, y2);
        c.ctx.stroke();
        c.ctx.closePath();
    }

    function drawBounds(x1: number, y1: number, width: number, height: number){
        c.ctx.beginPath();
        c.ctx.rect(x1, y1, width, height);
        c.ctx.fillStyle = "black";
        c.ctx.fill();
        c.ctx.closePath();
    }
    let scale = c.scale;
    var n = scale;
    while(true){
        if(n > c.canvas.width+scale && n > c.canvas.height+scale){
            break;
        }
        if(scale < c.canvas.width){ 
            drawGridline(n, 0, n, c.canvas.height);
        }
        if(scale < c.canvas.height){ 
            drawGridline(0, n, c.canvas.width, n);
        }
        let localN = Vec.add(vector((n/scale)-1, (n/scale)-1), viewOffset);
        if(localN.x < 0 || localN.x >= width){
            drawBounds(n-scale, 0, scale, c.canvas.height);
        }
        if(localN.y < 0 || localN.y >= height){
            drawBounds(0, n-scale, c.canvas.width, scale);
        }
        n += scale;
    }
}

export function drawTile(c: RenderContext, position: Vector, tileId: string){
    let tileIndex: number = (() => {
        switch(tileId){
            default:
            case "ground":
                return 0;
            case "hero":
                return 27;

        }
    })();
    let tileX = tileIndex % c.tileset.nTilesPerRow;
    let tileY = Math.floor(tileIndex / c.tileset.nTilesPerRow);
    c.ctx.drawImage(c.tileset.img,
                    // tileset coordinates
                    tileX * c.tileset.tileWidth + tileX * c.tileset.margin,
                    tileY * c.tileset.tileHeight + tileY * c.tileset.margin,
                    // tileset tile size
                    c.tileset.tileWidth,
                    c.tileset.tileHeight,
                    // screen draw position
                    position.x * c.scale,
                    position.y * c.scale,
                    // screen draw
                    c.scale, c.scale
                   );
}



type DrawOptions = {
    fillColor?: string;
    strokeColor?: string;
}

export function drawRect(c: RenderContext, position: Vector, options: DrawOptions ){
    let scale = c.scale;
    c.ctx.beginPath()
    c.ctx.rect(position.x*scale, position.y*scale,
               scale, scale);
    if(options.fillColor){
        c.ctx.fillStyle = options.fillColor;
        c.ctx.fill();
    }
    if(options.strokeColor){
        c.ctx.strokeStyle = options.strokeColor;
        c.ctx.lineWidth = 2;
        c.ctx.stroke();
    }
    c.ctx.closePath();
}


