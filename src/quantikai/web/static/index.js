var CLASSIC = "classic"
var ANALYSIS = "analysis"

function enableNextMoveClick(isAble) {
    if (isAble) {
        document.getElementById("buttonNextMove").onclick = onClickNextMove
    } else { document.getElementById("buttonNextMove").onclick = null }
}

function enableAllCellClicks(isAble) { 
    let cells = document.getElementsByClassName("cell")
    for (let cell of cells) { 
        if (isAble) {
            cell.onclick = function(e){onClickCell(cell.getAttribute("x"), cell.getAttribute("y"))}
        } else {
            cell.onclick = null
        }
    }
}
function updateBoard(new_moves) { 
    for (idx in new_moves) {
        const new_move = new_moves[idx]
        cell = document.getElementById('cell-' + new_move["x"] + '-' + new_move["y"])
        cell.textContent = new_move["pawn"]
        cell.setAttribute("class", "cell " + new_move["color"])
        // update the pawn list
        if (new_move["color"] == "BLUE") { 
            document.getElementById(new_move["pawn"]).remove()
        }
    }
}

function applyPlayerTurn(jsonResponse) { 
    // update the board
    updateBoard(jsonResponse["new_moves"])
    // Win or lose message
    if (jsonResponse["game_is_over"]) { 
        document.getElementById("msgBox").innerHTML = `<p class="win msg">`+jsonResponse["win_message"]+`</p>`
    }
    return jsonResponse["game_is_over"]
}
function to_json(response) {
    if (response.ok) {
        return response.json();
    }
    return response.json().then(response => {throw new Error(response.text)})
}
function botTurn() { 
    document.getElementById("msgBox").innerHTML = `<p class="wait msg">The bot is thinking...</p>`
    fetch("http://127.0.0.1:5000/bot", {method: "POST", headers: {
        "Content-Type": "application/json",
    },})
    .then(to_json)
    .then(applyPlayerTurn)
    .then(function (isWin) {
        if (!isWin){
            document.getElementById("msgBox").innerHTML = ""
            // Enable click events again
            enableAllCellClicks(true)
        }
        enableNextMoveClick(false);
    })
}
function onClickCell(x, y) { 
    
    const pawn = document.querySelector('input[name="pawn-select"]:checked').getAttribute("val");

    // Delete the error message
    document.getElementById("msgBox").innerHTML = ""

    // Disable all onClick events
    enableAllCellClicks(false)

    fetch("http://127.0.0.1:5000/", {method: "POST", body: JSON.stringify({ "x": x, "y": y, "pawn": pawn }), headers: {
        "Content-Type": "application/json",
    },})
    .then(to_json)
    .then(applyPlayerTurn)
    .then(function (isWin) {
        if (!isWin && document.getElementById("modeButton").getAttribute("mode") == CLASSIC) { botTurn() }
        else if(!isWin){
            enableNextMoveClick(true)
        }
    })
    .catch((error) => {
        document.getElementById("msgBox").innerHTML = `<p class="error msg">` + error + `</p>`
        // Enable click events again
        enableAllCellClicks(true)
    })
}

function onClickNewGame() { 
    location.reload();
}

function onClickChangeMode(current_mode) { 
    if (current_mode == CLASSIC) { 
        document.getElementById("modeButton").setAttribute("mode", ANALYSIS)
        document.getElementById("modeButton").innerHTML = `Analysis mode`
        document.getElementById("modeAnalysis").classList.remove("hidden")
        
    } else if (current_mode == ANALYSIS) {
        document.getElementById("modeButton").setAttribute("mode", CLASSIC)
        document.getElementById("modeButton").innerHTML = `Classic mode`
        document.getElementById("modeAnalysis").classList.add("hidden")
    }
}

function onClickNextMove() { 
    enableNextMoveClick(false);
    botTurn();
}
