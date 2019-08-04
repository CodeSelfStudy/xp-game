import { Tileset } from "./domain";


export async function getTileset(): Promise<Tileset> {
    let src = "/static/tilemaps/kenney/colored.png";
    let img = await loadTileset(src);
    return {
        tileWidth: 16,
        tileHeight: 16,
        nRows: 32,
        nTilesPerRow: 32,
        margin: 1,
        img
    }
}

function loadTileset(srcPath: string): Promise<HTMLImageElement> {
    return new Promise((resolve, reject) => {
        var img = new Image();
        img.src = srcPath;
        img.onload = () => resolve(img);
        img.onerror = () => {
            reject("Failed to load tileset");
        };
    });
}
