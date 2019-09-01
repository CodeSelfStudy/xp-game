import { Direction } from "../common/vectors.js";
import { ActionKind } from "../common/domain.js";
import { initialize, AiContext } from "./base.js";

/**
 * This is a super simple ai implementation that moves randomly
 * every so often.
 */

function direction(): Direction{
    let index = Math.floor(Math.random() * 4);
    let direction: Direction[] = ["North", "East", "West", "South"];
    return direction[index];
}

function update(context: AiContext){
    var rand = Math.random();
    var kind: ActionKind = Math.random() >= 0.5 ? "Move" : "Attack";
    if(rand > 0.90){
        context.act({kind: kind, direction: direction()});
    }
}

initialize({name: "Dopey the Dwarf", respawnTime: 5000}, update);
