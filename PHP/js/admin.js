const selectWindow = document.getElementById("selectWindow");
const currentWindow = document.getElementById("currentWindow");
const logWindow = document.getElementById("logWindow");

document.getElementById("log").addEventListener("click", function() {
    Object.assign(currentWindow.style, {
        visibility: "visible"
    });
    Object.assign(currentWindow.style, {
        visibility: "visible"
    });
    
});

document.getElementById("closeWindow").addEventListener("click", function() {
    Object.assign(currentWindow.style, {
        visibility: "hidden"
    });
    console.log("aaaaaa");
    
});