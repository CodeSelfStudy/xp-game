import { World, Action } from "../common/domain.js";
import { sendAction, requestLogin } from "../common/server.js"
import * as io from "socket.io-client";

// hack -- to connect to the game, use this:
var socket = io("http://xp-game.codeselfstudy.com");
//var socket = io("http://localhost:5000");

interface AiConfig {
    name: string,
    respawnTime: number
}

export interface AiContext {
    act(action: Action): void;
    world: World;
}

/**
 * Connect to the socket server, and spawn an ai entity.  The ai entity is
 * controlled via the `update` function, which is called each tick with the
 * most recent game state, `World`.
 */
export function initialize(cfg: AiConfig,
                           update: (ctx: AiContext) => void) {
    function respawn() {
        requestLogin(socket, cfg.name);
    }
    function act(action: Action){
        sendAction(socket, action);
    }

    socket.on('connect', () => respawn());
    socket.on('despawn', () => {
        setTimeout(respawn, cfg.respawnTime);
    });
    socket.on('world', (world: World) => {
        update({act, world});
    });
}
