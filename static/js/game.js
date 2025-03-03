/**
 * Game.js - Handles game logic and communication with the backend
 */

document.addEventListener('DOMContentLoaded', () => {
    const chessboard = new ChessBoard();
    const gameStatus = document.getElementById('game-status');
    const moveHistory = document.getElementById('move-history');
    const newGameBtn = document.getElementById('new-game-btn');
    const evolveBtn = document.getElementById('evolve-btn');
    const evolveOptions = document.getElementById('evolve-options');
    const confirmEvolveBtn = document.getElementById('confirm-evolve-btn');
    const cancelEvolveBtn = document.getElementById('cancel-evolve-btn');
    const undoBtn = document.getElementById('undo-btn');
    const easyBtn = document.getElementById('easy-btn');
    const mediumBtn = document.getElementById('medium-btn');
    const hardBtn = document.getElementById('hard-btn');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingMessage = document.getElementById('loading-message');
    const notification = document.getElementById('notification');
    const notificationMessage = document.getElementById('notification-message');
    const closeNotification = document.getElementById('close-notification');

    // Game state
    let gameActive = false;
    let currentDifficulty = 'medium';
    let moveStack = [];
    let currentMoveNumber = 1;

    // Initialize game
    init();

    function init() {
        // Set up event listeners
        newGameBtn.addEventListener('click', startNewGame);
        evolveBtn.addEventListener('click', showEvolveOptions);
        confirmEvolveBtn.addEventListener('click', evolveAI);
        cancelEvolveBtn.addEventListener('click', hideEvolveOptions);
        undoBtn.addEventListener('click', undoMove);
        easyBtn.addEventListener('click', () => setDifficulty('easy'));
        mediumBtn.addEventListener('click', () => setDifficulty('medium'));
        hardBtn.addEventListener('click', () => setDifficulty('hard'));
        closeNotification.addEventListener('click', hideNotification);

        // Set up game
        startNewGame();

        // Set up chessboard event handlers
        setupChessboardEvents();
    }

    function setupChessboardEvents() {
        // When the chessboard makes a move, we need to send it to the backend
        // This is done by extending the ChessBoard.makeMove method
        const originalMakeMove = chessboard.makeMove;
        chessboard.makeMove = (from, to) => {
            if (!gameActive) return;
            
            // Call the original method
            originalMakeMove.call(chessboard, from, to);
            
            // Send the move to the backend
            sendMoveToBackend(from, to);
        };
    }

    function startNewGame() {
        showLoading('Starting new game...');
        
        // Reset game state
        gameActive = true;
        moveStack = [];
        currentMoveNumber = 1;
        moveHistory.innerHTML = '';
        
        // Make API call to initialize a new game
        fetch('/initialize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ difficulty: currentDifficulty })
        })
        .then(response => response.json())
        .then(data => {
            // Update the chessboard with the initial position
            updateBoardFromBackend(data.board);
            
            // Update game status
            updateGameStatus(data.message);
            
            // Enable/disable buttons
            updateButtonStates();
            
            hideLoading();
        })
        .catch(error => {
            console.error('Error starting new game:', error);
            showNotification('Failed to start a new game. Please try again.');
            hideLoading();
        });
    }

    function sendMoveToBackend(from, to) {
        showLoading('Processing move...');
        
        fetch('/move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ from, to })
        })
        .then(response => response.json())
        .then(data => {
            if (data.valid) {
                // Add the move to history
                addMoveToHistory(from, to, 'player');
                
                // If the game is still active and AI made a move
                if (data.gameState === 'active' && data.aiMove) {
                    // Add AI's move to history
                    addMoveToHistory(data.aiMove.from, data.aiMove.to, 'ai');
                    
                    // Highlight the AI's move
                    chessboard.lastMove = { 
                        from: data.aiMove.from, 
                        to: data.aiMove.to 
                    };
                    chessboard.highlightLastMove();
                }
                
                // Update the board with the new state
                updateBoardFromBackend(data.board);
                
                // Check game state
                if (data.gameState === 'ended') {
                    gameActive = false;
                    updateGameStatus(data.message || `Game over. ${data.winner === 'player' ? 'You won!' : 'AI won!'}`);
                }
            } else {
                // Invalid move
                showNotification(data.message || 'Invalid move!');
                
                // Update the board to revert the invalid move
                updateBoardFromBackend(data.board);
            }
            
            // Update button states
            updateButtonStates();
            
            hideLoading();
        })
        .catch(error => {
            console.error('Error sending move:', error);
            showNotification('Failed to process move. Please try again.');
            hideLoading();
        });
    }

    function updateBoardFromBackend(boardState) {
        // Convert backend board representation to frontend format
        // and update the chessboard
        chessboard.updateBoard(boardState);
        
        // Generate legal moves from the current position
        const legalMoves = generateLegalMoves(boardState);
        chessboard.legalMoves = legalMoves;
    }

    function generateLegalMoves(boardState) {
        // This is a placeholder. In a real implementation, we would
        // either get legal moves from the backend or calculate them here.
        // For now, we'll return empty array as the backend handles validation
        return [];
    }

    function setDifficulty(difficulty) {
        // Update UI
        easyBtn.classList.toggle('active', difficulty === 'easy');
        mediumBtn.classList.toggle('active', difficulty === 'medium');
        hardBtn.classList.toggle('active', difficulty === 'hard');
        
        // Update state
        currentDifficulty = difficulty;
        
        // If a game is in progress, ask if user wants to restart
        if (gameActive) {
            showNotification('Difficulty changed. Start a new game for it to take effect.');
        }
    }

    function showEvolveOptions() {
        evolveBtn.classList.add('hidden');
        evolveOptions.classList.remove('hidden');
    }

    function hideEvolveOptions() {
        evolveOptions.classList.add('hidden');
        evolveBtn.classList.remove('hidden');
    }

    function evolveAI() {
        const generations = document.getElementById('generations').value;
        
        showLoading(`Evolving AI for ${generations} generations...`);
        
        fetch('/evolve', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ generations })
        })
        .then(response => response.json())
        .then(data => {
            hideEvolveOptions();
            showNotification(data.message);
            hideLoading();
        })
        .catch(error => {
            console.error('Error evolving AI:', error);
            showNotification('Failed to evolve AI. Please try again.');
            hideLoading();
        });
    }

    function undoMove() {
        // For now, just start a new game
        // In a more complete implementation, we would track moves and allow undoing
        showNotification('Undo not implemented. Starting a new game instead.');
        startNewGame();
    }

    function addMoveToHistory(from, to, player) {
        // Create move entry
        const moveRow = document.createElement('div');
        moveRow.style.display = 'contents';
        
        if (player === 'player') {
            // Player's move (white)
            const moveNumber = document.createElement('div');
            moveNumber.textContent = `${currentMoveNumber}.`;
            moveNumber.className = 'move-number';
            
            const whiteMove = document.createElement('div');
            whiteMove.textContent = `${from}-${to}`;
            
            const blackMove = document.createElement('div');
            
            moveRow.appendChild(moveNumber);
            moveRow.appendChild(whiteMove);
            moveRow.appendChild(blackMove);
            
            moveHistory.appendChild(moveRow);
        } else {
            // AI's move (black)
            // Find the last row
            const lastRow = moveHistory.lastChild;
            if (lastRow) {
                const blackMove = lastRow.lastChild;
                blackMove.textContent = `${from}-${to}`;
                currentMoveNumber++;
            }
        }
        
        // Add to move stack for potential undo
        moveStack.push({ from, to, player });
        
        // Scroll to bottom
        moveHistory.scrollTop = moveHistory.scrollHeight;
    }

    function updateGameStatus(message) {
        gameStatus.textContent = message;
    }

    function updateButtonStates() {
        undoBtn.disabled = !gameActive || moveStack.length === 0;
    }

    function showLoading(message) {
        loadingMessage.textContent = message || 'Processing...';
        loadingOverlay.classList.remove('hidden');
    }

    function hideLoading() {
        loadingOverlay.classList.add('hidden');
    }

    function showNotification(message) {
        notificationMessage.textContent = message;
        notification.classList.remove('hidden');
        
        // Auto-hide after 5 seconds
        setTimeout(hideNotification, 5000);
    }

    function hideNotification() {
        notification.classList.add('hidden');
    }
}); 