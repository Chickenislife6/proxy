window.addEventListener('load', main);
function main(){
    let mySocket = new WebSocket("ws://localhost:8080/ws");
    sendMsg();
    receiveMsg();
    
/*
    let form = document.getElementsByClassName("form");
    let input = document.getElementById("msg");
    form[0].addEventListener("submit", function (e) {
        input_text = input.value;
        mySocket.send(input_text);
        e.preventDefault()
    })
    */
}

//global variables
let msg="";

function sendMsg(){
    let txt = document.getElementById("msg");
    outgoing_msg = txt.value
    mySocket.send(outgoing_msg);

    let newElement = document.createElement("p")
    newElement.classList.add("this");
    newElement.innerHTML = msg;
    document.getElementById('chat').appendChild(newElement)

    document.getElementById("msg").value = "";
    msg = "";
}

function receiveMsg(){
    mySocket.onmessage = function (event) {
        let newElement = document.createElement("p")
        newElement.classList.add("that");
        newElement.innerHTML = event.data;
        document.getElementById('chat').appendChild(newElement)
    };

    
}

function closeForm(){
    
}
