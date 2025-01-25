const CLASSIC = 'classic'
const ANALYSIS = 'analysis'

function enableNextMoveClick(isAble) {
  if (isAble) {
    document.getElementById('buttonNextMove').onclick = onClickNextMove
  } else { document.getElementById('buttonNextMove').onclick = null }
}

function enableAllCellClicks(isAble) {
  const cells = document.getElementsByClassName('cell')
  for (const cell of cells) {
    if (isAble) {
      cell.onclick = function (e) { onClickCell(cell.getAttribute('x'), cell.getAttribute('y')) }
    } else {
      cell.onclick = null
    }
  }
}
function waitForBotMsg() {
  document.getElementById('msgBox').innerHTML = '<p class=\'wait msg\'>The bot is thinking...</p>'
}
function errorMsg(error) {
  document.getElementById('msgBox').innerHTML = '<p class=\'error msg\'>' + error + '</p>'
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

async function fetchPostRequest(path, body = null) {
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

function toJson(response) {
  if (response.ok) {
    return response.json()
  }
  return response.json().then(response => { throw new Error(response.text) })
}
function botTurn() {
  waitForBotMsg()
  fetchPostRequest('bot')
    .then(applyPlayerTurn)
    .then(function (isWin) {
      if (!isWin) {
        document.getElementById('msgBox').innerHTML = ''
        // Enable click events again
        enableAllCellClicks(true)
      }
      enableNextMoveClick(false)
    }).catch((error) => { errorMsg(error) })
}
function onClickCell(x, y) {
  const hasCheckedPawn = document.querySelector('input[name="pawn-select"]:checked') !== null
  if (!hasCheckedPawn) {
    throw new Error('Please select a pawn.')
  }
  const pawn = document.querySelector('input[name="pawn-select"]:checked').getAttribute('val')

  // Delete the error message
  document.getElementById('msgBox').innerHTML = ''

  // Disable all onClick events
  enableAllCellClicks(false)

  fetchPostRequest('', { x: x | null, y: y | null, pawn })
    .then(applyPlayerTurn)
    .then(function (isWin) {
      if (!isWin && !document.getElementById('modeButtonAnalysis').getAttribute('disabled')) { botTurn() } else if (!isWin) {
        enableNextMoveClick(true)
      }
    })
    .catch((error) => {
      errorMsg(error)
      // Enable click events again
      enableAllCellClicks(true)
    })
}

function onClickNewGame() {
  location.reload()
}

function onClickChangeMode(currentMode) {
  if (currentMode === CLASSIC) {
    document.getElementById('modeButtonClassic').setAttribute('disabled', '')
    document.getElementById('modeButtonAnalysis').removeAttribute('disabled')
    document.getElementById('modeAnalysis').classList.add('hidden')
  } else if (currentMode === ANALYSIS) {
    document.getElementById('modeButtonAnalysis').setAttribute('disabled', '')
    document.getElementById('modeButtonClassic').removeAttribute('disabled')
    document.getElementById('modeAnalysis').classList.remove('hidden')
  }
}

function onClickNextMove() {
  enableNextMoveClick(false)
  botTurn()
}
function showBoardAnalysis() {
  waitForBotMsg()
  const depth = document.getElementById('boardAnalysisDepth').value
  fetchPostRequest('analysis', { depth }).then(
    function (response) {
      let responseDisplay = '<p>Board analysis: score for each possible bot move, starting with the best one.</p><ol>'
      for (const item of response) {
        responseDisplay += '<li>' + JSON.stringify([[item[0].x, item[0].y, item[0].pawn, item[0].color], item[1]]) + '</li>'
      }
      responseDisplay += '</ol>'
      document.getElementById('board-analysis').innerHTML = responseDisplay
      document.getElementById('msgBox').innerHTML = ''
    }
  ).catch((error) => { errorMsg(error) })
}
function showGamePrediction() {
  waitForBotMsg()
  fetchPostRequest('gameprediction').then(
    function (response) {
      let responseDisplay = '<p>Game prediction: which moves will be played up to the end</p><ol>'
      for (const item of response) {
        responseDisplay += '<li>' + JSON.stringify([[item[0].parent_move.x, item[0].parent_move.y, item[0].parent_move.pawn, item[0].parent_move.color], item[1]]) + '</li>'
      }
      responseDisplay += '</ol>'
      document.getElementById('game-prediction').innerHTML = responseDisplay
      document.getElementById('msgBox').innerHTML = ''
    }
  ).catch((error) => { errorMsg(error) })
}
