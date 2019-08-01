import { Vector } from "./vectors";

export type Canvas = {
    canvas: HTMLCanvasElement,
    ctx: CanvasRenderingContext2D
}


export type Direction = "North" | "South" | "East" | "West";
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
