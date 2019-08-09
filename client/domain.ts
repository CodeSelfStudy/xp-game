import { Vector, Direction } from "./vectors";

export interface Tileset {
    tileWidth: number;
    tileHeight: number;
    margin: number;
    img: HTMLImageElement;
    nRows: number;
    nTilesPerRow: number;
}

export type RenderContext = {
    canvas: HTMLCanvasElement;
    ctx: CanvasRenderingContext2D;
    camera: { position: Vector; viewOffset: Vector; };
    scale: number;
    tileset: Tileset;
}


export type ActionKind = "Move" | "Attack" | "Spawn";
export type Action = { direction?: Direction, kind: ActionKind }


export type World = {
    width: number;
    height: number;
    entities: Entity[];
    tile_grid: Tile[][]
}

export type Entity = {
    position: Vector;
    client_id: string;
    current_action?: Action;
    health: number;
}


export type Tile = {
    tile_id: string
}
