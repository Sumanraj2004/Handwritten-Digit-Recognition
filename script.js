let canvas = document.getElementById("canvas");
let ctx = canvas.getContext("2d");
let drawing = false;

ctx.fillStyle = "white";
ctx.fillRect(0, 0, canvas.width, canvas.height);

canvas.addEventListener("mousedown", () => drawing = true);
canvas.addEventListener("mouseup", () => {
    drawing = false;
    ctx.beginPath();
});
canvas.addEventListener("mousemove", draw);

function draw(e) {
    if (!drawing) return;

    ctx.lineWidth = 22;
    ctx.lineCap = "round";
    ctx.strokeStyle = "black";

    let rect = canvas.getBoundingClientRect();
    ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
}

function clearCanvas() {
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}

async function predictDigit() {
    let image = canvas.toDataURL("image/png");

    let response = await fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image })
    });

    let result = await response.json();
    document.getElementById("result").innerText = "Prediction: " + result.digit;
}
