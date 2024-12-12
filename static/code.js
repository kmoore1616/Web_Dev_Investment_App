var socket = io();
var key = 46c5a0a4eba75f027bf2623f2e948972;


function deposit(){
                var amount = document.getElementById("cash_add").value;
                if(amount <= 0 || !(typeof amount === "number")){
                                alert("Invalid entry. Enter a positive number...");
                }else{
                                socket.emit("deposit", amount);
                }
}

function withdraw(){
                var amount = document.getElementById("cash_remove").value;
                if(amount <= 0 || !(typeof amount === "number")){
                                alert("Invalid entry. Enter a positive number...");
                }else{
                                socket.emit("withdraw", amount);
                }
}
