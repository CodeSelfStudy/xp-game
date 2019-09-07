import { Direction } from "../common/vectors.js";
import { ActionKind } from "../common/domain.js";
import { initialize, AiContext } from "./base.js";

/**
 * This is a super simple ai implementation that moves and attacks randomly
 */


function update(context: AiContext){
    function direction(): Direction{
        let index = Math.floor(Math.random() * 4);
        let direction: Direction[] = ["North", "East", "West", "South"];
        return direction[index];
    }

    let rand = Math.random();
    if(!context.self.current_action && rand > 0.50){
        let kind: ActionKind = Math.random() >= 0.5 ? "Move" : "Attack";
        context.act({kind: kind, direction: direction()});
    }
}

initialize({name: "Dopey the Dwarf", respawnTime: 5000}, update);
