/**
 * Sanitize user content before printing to the screen.
 *
 * At the moment, this just strips out `<` and `>` when they look like
 * HTML tags.
 */
export function sanitize(text: string): string {
    const pattern = /<(\/?[-_\sa-zA-Z0-9]*?)>/g;
    return text.replace(pattern, " $1 ");
}

/** 
 * Subscribe an event listener to the provided `HTMLInputElement` that constrains
 * the length of its value to `maxCharacters`. Returns a callback to unsubscibe the
 * event listener
 */
export function subscribeInputLimit(maxCharacters: number, element: HTMLInputElement){
    function limit(event: KeyboardEvent){
        if(element.value.length > maxCharacters){
            element.value = element.value.substring(maxCharacters);
        }
    }
    element.addEventListener("keypress", limit);
    return () => element.removeEventListener("keypress", limit);
}
