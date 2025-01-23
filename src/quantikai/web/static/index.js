const CLASSIC = 'classic'
const ANALYSIS = 'analysis'

function enableNextMoveClick (isAble) {
  if (isAble) {
    document.getElementById('buttonNextMove').onclick = onClickNextMove
  } else { document.getElementById('buttonNextMove').onclick = null }
}

function enableAllCellClicks (isAble) {
  const cells = document.getElementsByClassName('cell')
  for (const cell of cells) {
    if (isAble) {
      cell.onclick = function (e) { onClickCell(cell.getAttribute('x'), cell.getAttribute('y')) }
    } else {
      cell.onclick = null
    }
  }
}
function updateBoard(newMoves) {
  for (const idx in newMoves) {
    const newMove = newMoves[idx]
    const cell = document.getElementById('cell-' + newMove.x + '-' + newMove.y)
    cell.textContent = newMove.pawn
    cell.setAttribute('class', 'cell ' + newMove.color)
    // update the pawn list
    if (newMove.color === 'BLUE') {
      document.getElementById(newMove.pawn).remove()
    }
  }
}

function applyPlayerTurn(jsonResponse) {
  // update the board
  updateBoard(jsonResponse.newMoves)
  // Win or lose message
  if (jsonResponse.gameIsOver) {
    document.getElementById('msgBox').innerHTML = '<p class=\'win msg\'>' + jsonResponse.winMessage + '</p>'
  }
  return jsonResponse.gameIsOver
}

async function fetchPostRequest (path, body = null) {
  const url = 'http://127.0.0.1:5000/' + path

  const params = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  }
  if (body != null) {
    params.body = JSON.stringify(body)
  }
  return fetch(url, params).then(toJson)
}

function toJson (response) {
  if (response.ok) {
    return response.json()
  }
  return response.json().then(response => { throw new Error(response.text) })
}
function botTurn () {
  document.getElementById('msgBox').innerHTML = '<p class=\'wait msg\'>The bot is thinking...</p>'
  fetchPostRequest('bot')
    .then(applyPlayerTurn)
    .then(function (isWin) {
      if (!isWin) {
        document.getElementById('msgBox').innerHTML = ''
        // Enable click events again
        enableAllCellClicks(true)
      }
      enableNextMoveClick(false)
    })
}
function onClickCell (x, y) {
  const pawn = document.querySelector('input[name="pawn-select"]:checked').getAttribute('val')
  console.log(pawn)

  // Delete the error message
  document.getElementById('msgBox').innerHTML = ''

  // Disable all onClick events
  enableAllCellClicks(false)

  fetchPostRequest('', { x: x | null, y: y | null, pawn: pawn })
    .then(applyPlayerTurn)
    .then(function (isWin) {
      if (!isWin && document.getElementById('modeButton').getAttribute('mode') === CLASSIC) { botTurn() } else if (!isWin) {
        enableNextMoveClick(true)
      }
    })
    .catch((error) => {
      document.getElementById('msgBox').innerHTML = '<p class=\'error msg\'>' + error + '</p>'
      // Enable click events again
      enableAllCellClicks(true)
    })
}

function onClickNewGame() {
  location.reload()
}

function onClickChangeMode (currentMode) {
  if (currentMode === CLASSIC) {
    document.getElementById('modeButton').setAttribute('mode', ANALYSIS)
    document.getElementById('modeButton').innerHTML = 'Analysis mode'
    document.getElementById('modeAnalysis').classList.remove('hidden')
  } else if (currentMode === ANALYSIS) {
    document.getElementById('modeButton').setAttribute('mode', CLASSIC)
    document.getElementById('modeButton').innerHTML = 'Classic mode'
    document.getElementById('modeAnalysis').classList.add('hidden')
  }
}

function onClickNextMove () {
  enableNextMoveClick(false)
  botTurn()
}
function showBoardAnalysis () {
  fetch('http://127.0.0.1:5000/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(toJson)
}
