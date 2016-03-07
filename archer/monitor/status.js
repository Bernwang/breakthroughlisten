<!-- GBT status indicator-->
$("#gbt-indicatorTxt").load("/status/indicator.py #gbt-statusTxt")
$("#gbt-indicatorImg").load("/status/indicator.py #gbt-statusImg")
time = setInterval(function(){
        $("#gbt-indicatorTxt").load("/status/indicator.py #gbt-statusTxt");
        $("#gbt-indicatorImg").load("/status/indicator.py #gbt-statusImg")
},1000);

<!-- GBT short status-->
$("#gbt-short").load("/status/status-short.py #gbt-target");
time = setInterval(function(){
        $("#gbt-short").load("/status/status-short.py #gbt-target");
},1000);

<!-- GBT full status-->
$("#gbt-meta").load("/status/status-full.py #gbtMeta");
time = setInterval(function(){
        $("#gbt-meta").load("/status/status-full.py #gbtMeta");
},1000);

<!-- GBT ADC-->
var gbtADC0 = document.getElementById("gbtADC0");
var gbtADC0URL = "/status/images/ADC0SNAP.png";
var gbtADC1 = document.getElementById("gbtADC1");
var gbtADC1URL = "/status/images/ADC1SNAP.png";
setInterval(function() {
        gbtADC0.src = gbtADC0URL + '?t=' + new Date().getTime();
        gbtADC1.src = gbtADC1URL + '?t=' + new Date().getTime();
}, 61000);

<!-- GBT aitoff-->
var gbtAitoff = document.getElementById("gbtAitoff");
var gbtAitoffURL = "/status/images/gbtAitoff.png";
setInterval(function() {
        gbtAitoff.src = gbtAitoffURL + '?t=' + new Date().getTime();
}, 61000);


<!-- GBT MWA skymap-->
var gbtAitoff = document.getElementById("gbtMWAsky");
var gbtAitoffURL = "/status/images/gbtmwasky.png";
setInterval(function() {
        gbtAitoff.src = gbtAitoffURL + '?t=' + new Date().getTime();
}, 61000);


