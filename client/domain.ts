import { Vector, Direction } from "./vectors";

export type RenderContext = {
    canvas: HTMLCanvasElement,
    ctx: CanvasRenderingContext2D
    camera: { position: Vector; viewOffset: Vector; }
}


export type ActionKind = "Move" | "Attack";
export type Action = { direction: Direction, kind: ActionKind }


export type World = {
    width: number;
    height: number;
    entities: Entity[];
}

export type Entity = {
    position: Vector;
    client_id: string;
    current_action?: Action;
}
