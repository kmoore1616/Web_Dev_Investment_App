var socket = io();
var key = 46c5a0a4eba75f027bf2623f2e948972;


function get_stock_info(symbol, date){
                var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
                                if(this.readyState === 4 && this.status === 200){
                                                var json = parse(this.responseText);
                                                console.log(json);
                                                return json;
                                }
                                xhttp.open("GET", "http://api.marketstack.com/v1/eod/" + date + "? access_key = 46c5a0a4eba75f027bf2623f2e948972& symbols = "+ symbol);
                                xhttp.send();
                }
};


socket.on("get_stock_info", function(symbol, date){
                var stock_info = [];
                stock_info.push(get_stock_info(symbol, date));
                stock_info.push(get_stock_info(symbol, "latest"));
                socket.send(stock_info);
});
