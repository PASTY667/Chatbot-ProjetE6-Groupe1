const selectWindow = document.getElementById("selectWindow");
const currentWindow = document.getElementById("currentWindow");
let currentTab = "";

document.getElementById("log").addEventListener("click", function() {
    currentTab = "";
    Object.assign(currentWindow.style, {
        visibility: "visible"
    });
    console.log("aaaaaa");
    
});

document.getElementById("closeWindow").addEventListener("click", function() {
    Object.assign(currentWindow.style, {
        visibility: "hidden"
    });
    console.log("aaaaaa");
    
});