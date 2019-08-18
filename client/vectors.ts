export type Vector = { x: number, y: number }
export type Direction = "North" | "South" | "East" | "West";
type V2 = Vector;

export function vector(x: number, y: number): Vector {
    return {x: Math.round(x), y: Math.round(y) };
}
export function equals(a: V2, b: V2): boolean { return a.x == b.x && a.y == b.y; }
export function add(a: V2, b: V2): V2 {
    return {
        x: a.x + b.x,
        y: a.y + b.y
    }
}
export function subtract(a: V2, b: V2): V2 {
    return {
        x: a.x - b.x,
        y: a.y - b.y
    }
}
export function multiply(a: V2, scalar: number) { return vector(a.x*scalar, a.y*scalar); }
export function zero(): V2 { return vector(0, 0); }
export function up(){ return vector(0, -1); }
export function down(){ return vector(0, 1); }
export function left(){ return vector(-1, 0); }
export function right(){ return vector(1, 0); }

export function dirToVec(direction: Direction){
    switch(direction){
        default: return zero();
        case "North": return up();
        case "South": return down();
        case "West": return left();
        case "East": return right();
    };
}
