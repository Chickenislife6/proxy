let append = localStorage.getItem("storedChatRoom") === null ? "" : localStorage.getItem("storedChatRoom");
let mySocket = new WebSocket("ws://127.0.0.1:8080/"+append);

mySocket.onmessage = function (event) {
    console.log(event.data)
    let newElement = document.createElement("p")
    newElement.classList.add("that");
    newElement.innerHTML = event.data;
    document.getElementById('chat').appendChild(newElement)
}


window.addEventListener('load', main);
function main(){
    //alert(localStorage.getItem("storedUsername"));
    console.log(document.getElementById("submitBtn").className)
    document.getElementById("submitBtn").addEventListener("click", (event) => {
        event.preventDefault();
        let txt = document.getElementById("msg");
        outgoing_msg = txt.value
        mySocket.send(outgoing_msg);

        let newElement = document.createElement("p")
        newElement.classList.add("this");
        newElement.innerHTML = outgoing_msg;
        document.getElementById('chat').appendChild(newElement)

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


    

function closeForm(){
    localStorage.clear();
}
