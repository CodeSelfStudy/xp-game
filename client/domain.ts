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
    ctx: CanvasRenderingContext2D;
    camera: { position: Vector; viewOffset: Vector; };
    scale: number;
    tileset: Tileset;
}

export type ActionKind = "Move" | "Attack" | "Spawn" | "Dash" | "Aimed Shot"; 

export type Action = {
    entity?: Entity;
    kind: ActionKind;
    direction?: Direction;
}

export type Ability = {
    color: string;
    reach: number; 
}


export type World = {
    width: number;
    height: number;
    entities: Entity[];
    tile_grid: Tile[][];
}

export type Entity = {
    position: Vector;
    client_id: string;
    health: number;
    currentAction?: { action: Action, ability: Ability };
}

export type Tile = {
    tile_id: string;
}
