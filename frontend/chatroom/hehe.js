let append = localStorage.getItem("storedChatRoom") === null ? "" : localStorage.getItem("storedChatRoom");
let mySocket = new WebSocket("ws://127.0.0.1:8080/"+append);
let username = localStorage.getItem("storedUsername");
mySocket.onmessage = function (event) {
    console.log(event.data)
    add_message(event.data, className="that")
}


window.addEventListener('load', main);
function main(){
    document.getElementById("submitBtn").addEventListener("click", (event) => {
        event.preventDefault();
        let txt = document.getElementById("msg");
        outgoing_msg = txt.value
        outgoing_msg = username + ": " + outgoing_msg
        mySocket.send(outgoing_msg);
        add_message(outgoing_msg, className= "this");
        document.getElementById("msg").value = "";
    
})
    mySocket.send("Hello, you are chatting with " + localStorage.getItem("storedUsername"))
    
    //window.addEventListener('load', );
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
function add_message(value, className = "this") {
    let newElement = document.createElement("p")
    newElement.classList.add(className);
    newElement.innerHTML = value;
    document.getElementById('chat').appendChild(newElement);
}

    

function closeForm(){
    localStorage.clear();
}
