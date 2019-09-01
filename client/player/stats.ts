export function setHealth(value: number){
    let hpElement = document.getElementById('current-hp');
    hpElement.innerText = String(value);
}

export function setUsername(value: string){
    let nameElement = document.getElementById('username');
    nameElement.innerText = value;
}
