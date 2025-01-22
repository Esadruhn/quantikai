function enableAllCellClicks(is_able) { 
    cells = document.getElementsByClassName("cell")
    if (is_able) { 
        for (let cell of cells) { 
            cell.onclick = function(e){onClickCell(cell.getAttribute("x"), cell.getAttribute("y"))}
        }
    }
    else { 
        for (let cell of cells) { 
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
function onClickCell(x, y) { 
    
    const pawn = document.querySelector('input[name="pawn-select"]:checked').getAttribute("val");

    // Delete the error message
    document.getElementById("msgBox").innerHTML = ""

    // Disable all onClick events
    enableAllCellClicks(false)

    fetch("http://127.0.0.1:5000/", {method: "POST", body: JSON.stringify({ "x": x, "y": y, "pawn": pawn }), headers: {
        "Content-Type": "application/json",
    },})
    .then(function (response) {
        if (response.ok) {
            return response.json();
        }
        return response.json().then(response => {throw new Error(response.text)})
    })
    .then(applyPlayerTurn)
    .then(function (isWin) { 
        if (!isWin) { 
            document.getElementById("msgBox").innerHTML = `<p class="wait msg">The bot is thinking...</p>`
            fetch("http://127.0.0.1:5000/bot", {method: "POST", body: JSON.stringify({ "x": x, "y": y, "pawn": pawn }), headers: {
                "Content-Type": "application/json",
            },})
            .then(function (response) {
                if (response.ok) {
                    return response.json();
                    }
                    return response.json().then(response => {throw new Error(response.text)})
            })
            .then(applyPlayerTurn)
            .then(function (isWin) {
                if (!isWin){
                    document.getElementById("msgBox").innerHTML = ""
                    // Enable click events again
                    enableAllCellClicks(true)
                }
            })
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
