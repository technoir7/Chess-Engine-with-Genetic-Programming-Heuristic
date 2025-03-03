/**
 * Chessboard.js - Handles chessboard rendering and piece movement
 */

class ChessBoard {
    constructor() {
        this.boardElement = document.getElementById('chessboard');
        this.squares = {};
        this.selectedSquare = null;
        this.legalMoves = [];
        this.lastMove = null;
        this.boardState = {};
        this.orientation = 'white'; // white pieces at bottom
        this.pieceImages = {
            'p': '/static/images/pieces/black-pawn.svg',
            'r': '/static/images/pieces/black-rook.svg',
            'n': '/static/images/pieces/black-knight.svg',
            'b': '/static/images/pieces/black-bishop.svg',
            'q': '/static/images/pieces/black-queen.svg',
            'k': '/static/images/pieces/black-king.svg',
            'P': '/static/images/pieces/white-pawn.svg',
            'R': '/static/images/pieces/white-rook.svg',
            'N': '/static/images/pieces/white-knight.svg',
            'B': '/static/images/pieces/white-bishop.svg',
            'Q': '/static/images/pieces/white-queen.svg',
            'K': '/static/images/pieces/white-king.svg'
        };
        
        this.init();
        this.addDefaultLegalMoves();
        console.log('ChessBoard initialized');
    }

    /**
     * Initialize the chessboard
     */
    init() {
        if (this.boardElement) {
            this.createBoard();
            this.setupEventListeners();
        } else {
            console.error('Board element not found');
        }
    }

    /**
     * Add default legal moves for initial position
     * This ensures pawns can move even if the server doesn't provide legal moves
     */
    addDefaultLegalMoves() {
        console.log('Adding default legal moves for initial position');
        
        // Add pawn moves
        const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
        
        files.forEach(file => {
            // White pawns can move one or two squares forward from rank 2
            this.legalMoves.push({ from: `${file}2`, to: `${file}3` });
            this.legalMoves.push({ from: `${file}2`, to: `${file}4` });
        });
        
        // Add knight moves
        this.legalMoves.push({ from: 'b1', to: 'a3' });
        this.legalMoves.push({ from: 'b1', to: 'c3' });
        this.legalMoves.push({ from: 'g1', to: 'f3' });
        this.legalMoves.push({ from: 'g1', to: 'h3' });
        
        console.log(`Added ${this.legalMoves.length} default legal moves`);
    }

    /**
     * Create the chessboard squares
     */
    createBoard() {
        const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
        const ranks = ['8', '7', '6', '5', '4', '3', '2', '1'];

        this.boardElement.innerHTML = '';

        ranks.forEach((rank, rankIndex) => {
            files.forEach((file, fileIndex) => {
                const squareId = file + rank;
                const isLight = (rankIndex + fileIndex) % 2 === 1;
                const squareElement = document.createElement('div');
                
                squareElement.id = squareId;
                squareElement.className = `square ${isLight ? 'light' : 'dark'}`;
                squareElement.dataset.squareId = squareId;
                
                this.boardElement.appendChild(squareElement);
                this.squares[squareId] = squareElement;
            });
        });
    }

    /**
     * Set up event listeners for squares
     */
    setupEventListeners() {
        this.boardElement.addEventListener('click', (event) => {
            const squareElement = event.target.closest('.square');
            if (squareElement) {
                const squareId = squareElement.dataset.squareId;
                this.handleSquareClick(squareId);
            }
        });
    }

    /**
     * Handle square click event
     * @param {string} squareId - ID of the clicked square (e.g., 'e4')
     */
    handleSquareClick(squareId) {
        console.log(`Square clicked: ${squareId}`);
        
        // Check if the game is active
        const event = new CustomEvent('checkGameActive', {
            detail: {
                callback: (isActive, playerColor) => {
                    if (isActive) {
                        this.handlePlayerSquareClick(squareId);
                    } else {
                        console.log('Game is not active');
                    }
                }
            }
        });
        
        document.dispatchEvent(event);
    }
    
    /**
     * Handle a valid player square click
     * @param {string} squareId - ID of the clicked square
     */
    handlePlayerSquareClick(squareId) {
        const hasPiece = this.boardState[squareId] !== undefined;
        
        // If a square is already selected
        if (this.selectedSquare) {
            // If the clicked square is the same as the selected square, deselect it
            if (squareId === this.selectedSquare) {
                console.log(`Deselecting ${squareId}`);
                this.deselectSquare();
                return;
            }
            
            // Check if the move is legal
            if (this.isLegalMove(this.selectedSquare, squareId)) {
                console.log(`Making move from ${this.selectedSquare} to ${squareId}`);
                this.makeMove(this.selectedSquare, squareId);
            } else {
                console.log(`Move from ${this.selectedSquare} to ${squareId} is not legal`);
                
                // If the clicked square has a friendly piece, select it instead
                if (hasPiece && this.isPieceFriendly(squareId)) {
                    console.log(`Selecting new piece at ${squareId}`);
                    this.selectSquare(squareId);
                } else {
                    // Deselect current piece since the move isn't valid
                    console.log(`Deselecting ${this.selectedSquare} as the move isn't valid`);
                    this.deselectSquare();
                }
            }
        } else if (hasPiece && this.isPieceFriendly(squareId)) {
            // If no square is selected and clicked on a friendly piece, select it
            console.log(`Selecting piece at ${squareId}`);
            this.selectSquare(squareId);
        }
    }

    /**
     * Check if a move is legal
     * @param {string} from - Starting square (e.g., 'e2')
     * @param {string} to - Target square (e.g., 'e4')
     * @returns {boolean} - Whether the move is legal
     */
    isLegalMove(from, to) {
        console.log(`Checking if move from ${from} to ${to} is legal`);
        
        // First check if the move exists in the legal moves array
        const moveExists = this.legalMoves.some(move => 
            move.from === from && move.to === to
        );
        
        if (moveExists) {
            console.log(`Move from ${from} to ${to} found in legal moves`);
            return true;
        }
        
        // If we don't have legal moves or the move isn't in there, fall back to basic rules
        console.log(`Move from ${from} to ${to} not found in legal moves, checking fallback rules`);
        
        // Get the piece at the "from" position
        const piece = this.boardState[from];
        if (!piece) {
            console.log(`No piece found at ${from}`);
            return false;
        }
        
        // Check if there's a piece at the destination (can't capture our own pieces)
        const destPiece = this.boardState[to];
        if (destPiece && destPiece.color === piece.color) {
            console.log(`Cannot capture own piece at ${to}`);
            return false;
        }
        
        // Implement basic chess rules for pawns
        if (piece.type.toLowerCase() === 'p') {
            // White pawn
            if (piece.color === 'white') {
                // One square forward
                if (to === `${from[0]}${parseInt(from[1]) + 1}`) {
                    if (!destPiece) { 
                        return true;
                    }
                }
                
                // Two squares forward from starting position
                if (from[1] === '2' && to === `${from[0]}4`) {
                    const middleSquare = `${from[0]}3`;
                    if (!destPiece && !this.boardState[middleSquare]) {
                        return true;
                    }
                }
                
                // Capture diagonally
                const fileOffset = Math.abs(from.charCodeAt(0) - to.charCodeAt(0));
                const rankOffset = to[1] - from[1];
                if (fileOffset === 1 && rankOffset === 1 && destPiece && destPiece.color === 'black') {
                    return true;
                }
            }
            
            // Black pawn (for completeness)
            if (piece.color === 'black') {
                // One square forward
                if (to === `${from[0]}${parseInt(from[1]) - 1}`) {
                    if (!destPiece) {
                        return true;
                    }
                }
                
                // Two squares forward from starting position
                if (from[1] === '7' && to === `${from[0]}5`) {
                    const middleSquare = `${from[0]}6`;
                    if (!destPiece && !this.boardState[middleSquare]) {
                        return true;
                    }
                }
                
                // Capture diagonally
                const fileOffset = Math.abs(from.charCodeAt(0) - to.charCodeAt(0));
                const rankOffset = from[1] - to[1];
                if (fileOffset === 1 && rankOffset === 1 && destPiece && destPiece.color === 'white') {
                    return true;
                }
            }
        }
        
        // Basic knight moves
        if (piece.type.toLowerCase() === 'n') {
            const fileOffset = Math.abs(from.charCodeAt(0) - to.charCodeAt(0));
            const rankOffset = Math.abs(from[1] - to[1]);
            
            if ((fileOffset === 1 && rankOffset === 2) || (fileOffset === 2 && rankOffset === 1)) {
                return true;
            }
        }
        
        console.log(`Move from ${from} to ${to} is not legal according to fallback rules`);
        return false;
    }

    /**
     * Select a square and highlight legal moves
     * @param {string} squareId - ID of the square to select
     */
    selectSquare(squareId) {
        // Deselect any previously selected square
        if (this.selectedSquare) {
            this.deselectSquare();
        }
        
        this.selectedSquare = squareId;
        
        // Add selected class to highlight the square
        const squareElement = this.squares[squareId];
        if (squareElement) {
            squareElement.classList.add('selected');
            
            // Highlight legal moves for this piece
            this.highlightLegalMoves();
        }
    }

    /**
     * Deselect the currently selected square and clear highlights
     */
    deselectSquare() {
        if (this.selectedSquare) {
            // Remove selected class from the square
            const squareElement = this.squares[this.selectedSquare];
            if (squareElement) {
                squareElement.classList.remove('selected');
            }
            
            // Remove highlights from all squares
            this.removeAllHighlights();
            
            this.selectedSquare = null;
        }
    }

    /**
     * Highlight legal moves for the selected piece
     */
    highlightLegalMoves() {
        if (!this.selectedSquare) return;
        
        console.log(`Highlighting legal moves for ${this.selectedSquare}`);
        
        let highlightCount = 0;
        
        // First try to use the legal moves array
        this.legalMoves.forEach(move => {
            if (move.from === this.selectedSquare) {
                const squareElement = this.squares[move.to];
                if (squareElement) {
                    squareElement.classList.add('highlight');
                    
                    // If there's a piece on the target square, it's a capture
                    if (this.boardState[move.to]) {
                        squareElement.classList.add('capture');
                    }
                    
                    highlightCount++;
                }
            }
        });
        
        // If no legal moves were highlighted, use fallback rules
        if (highlightCount === 0) {
            console.log('No legal moves found in array, using fallback rules');
            this.highlightFallbackLegalMoves();
        } else {
            console.log(`Highlighted ${highlightCount} legal moves`);
        }
    }
    
    /**
     * Highlight legal moves based on basic chess rules when no legal moves are provided
     * This is a fallback for initial position testing
     */
    highlightFallbackLegalMoves() {
        if (!this.selectedSquare) return;
        
        const piece = this.boardState[this.selectedSquare];
        if (!piece) return;
        
        const file = this.selectedSquare[0];
        const rank = parseInt(this.selectedSquare[1]);
        
        // Implement basic chess rules for pawns
        if (piece.type.toLowerCase() === 'p') {
            if (piece.color === 'white') {
                // One square forward
                const oneSquareForward = `${file}${rank + 1}`;
                if (this.squares[oneSquareForward] && !this.boardState[oneSquareForward]) {
                    this.squares[oneSquareForward].classList.add('highlight');
                }
                
                // Two squares forward from starting position
                if (rank === 2) {
                    const twoSquaresForward = `${file}4`;
                    if (!this.boardState[oneSquareForward] && !this.boardState[twoSquaresForward]) {
                        this.squares[twoSquaresForward].classList.add('highlight');
                    }
                }
                
                // Captures
                const leftCapture = String.fromCharCode(file.charCodeAt(0) - 1) + (rank + 1);
                const rightCapture = String.fromCharCode(file.charCodeAt(0) + 1) + (rank + 1);
                
                if (this.squares[leftCapture] && this.boardState[leftCapture] && 
                    this.boardState[leftCapture].color === 'black') {
                    this.squares[leftCapture].classList.add('highlight', 'capture');
                }
                
                if (this.squares[rightCapture] && this.boardState[rightCapture] && 
                    this.boardState[rightCapture].color === 'black') {
                    this.squares[rightCapture].classList.add('highlight', 'capture');
                }
            } else {
                // Similar logic for black pawns
                // (omitted for brevity, but should be implemented for completeness)
            }
        }
        
        // Knights
        if (piece.type.toLowerCase() === 'n') {
            const fileCode = file.charCodeAt(0);
            const knightMoves = [
                { file: fileCode - 1, rank: rank + 2 }, // left + 2 up
                { file: fileCode + 1, rank: rank + 2 }, // right + 2 up
                { file: fileCode - 2, rank: rank + 1 }, // 2 left + up
                { file: fileCode + 2, rank: rank + 1 }, // 2 right + up
                { file: fileCode - 2, rank: rank - 1 }, // 2 left + down
                { file: fileCode + 2, rank: rank - 1 }, // 2 right + down
                { file: fileCode - 1, rank: rank - 2 }, // left + 2 down
                { file: fileCode + 1, rank: rank - 2 }, // right + 2 down
            ];
            
            knightMoves.forEach(move => {
                if (move.file >= 97 && move.file <= 104 && move.rank >= 1 && move.rank <= 8) {
                    const targetSquare = String.fromCharCode(move.file) + move.rank;
                    
                    if (this.squares[targetSquare]) {
                        const targetPiece = this.boardState[targetSquare];
                        
                        if (!targetPiece || targetPiece.color !== piece.color) {
                            this.squares[targetSquare].classList.add('highlight');
                            
                            if (targetPiece) {
                                this.squares[targetSquare].classList.add('capture');
                            }
                        }
                    }
                }
            });
        }
    }

    removeAllHighlights() {
        Object.values(this.squares).forEach(square => {
            square.classList.remove('highlight', 'capture', 'last-move', 'check');
        });
    }

    /**
     * Make a move on the chessboard
     * @param {string} from - Starting square (e.g., 'e2')
     * @param {string} to - Target square (e.g., 'e4')
     */
    makeMove(from, to) {
        console.log(`Making move from ${from} to ${to}`);
        
        // Optimistically update the UI
        const originalBoardState = JSON.parse(JSON.stringify(this.boardState));
        const movingPiece = this.boardState[from];
        
        if (!movingPiece) {
            console.error(`No piece found at ${from}`);
            return;
        }
        
        // Store the move being made
        const move = {
            from,
            to,
            piece: movingPiece,
            capturedPiece: this.boardState[to]
        };
        
        // Update internal board state optimistically
        const newBoardState = {...this.boardState};
        newBoardState[to] = newBoardState[from];
        delete newBoardState[from];
        
        // Update the UI with the new state
        this.updateBoardUI(newBoardState);
        
        // Update the last move highlight
        this.updateLastMoveHighlight(from, to);
        
        // Deselect the square
        this.deselectSquare();
        
        // Send the move to the backend
        this.sendMoveToBackend(from, to, movingPiece, originalBoardState);
    }
    
    updateLastMoveHighlight(from, to) {
        // Remove any existing last-move highlights
        Object.values(this.squares).forEach(square => {
            square.classList.remove('last-move');
        });
        
        // Add last-move class to the from and to squares
        if (this.squares[from]) this.squares[from].classList.add('last-move');
        if (this.squares[to]) this.squares[to].classList.add('last-move');
        
        // Store the last move
        this.lastMove = { from, to };
    }
    
    /**
     * Send a move to the backend
     * @param {string} from - Starting square (e.g., 'e2')
     * @param {string} to - Target square (e.g., 'e4')
     * @param {Object} piece - The piece being moved
     * @param {Object} originalBoardState - Original board state to revert to if move fails
     */
    sendMoveToBackend(from, to, piece, originalBoardState) {
        // Prepare the move data
        const moveData = {
            from,
            to,
            piece: piece.code
        };
        
        // Show loading state
        const loadingOverlay = document.getElementById('loading-overlay');
        const loadingMessage = document.getElementById('loading-message');
        
        if (loadingOverlay && loadingMessage) {
            loadingOverlay.style.display = 'flex';
            loadingMessage.textContent = 'Processing move...';
            loadingMessage.style.display = 'block';
        }
        
        console.log(`Sending move to backend: ${JSON.stringify(moveData)}`);
        
        // Send the move to the backend
        fetch('/move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(moveData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server returned ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Move response:', data);
            
            if (data.valid) {
                // Update board with the state returned from the server
                this.updateBoard(data.board, data.legalMoves);
                
                // Show notification
                this.showNotification('Move successful!', 'success');
            } else {
                // Revert to the original state
                console.error('Invalid move:', data.message);
                this.updateBoard(originalBoardState);
                
                // Show error notification
                this.showNotification(`Invalid move: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            console.error('Error sending move:', error);
            
            // Revert to the original state
            this.updateBoard(originalBoardState);
            
            // Show error notification
            this.showNotification('Error processing move. Please try again.', 'error');
        })
        .finally(() => {
            // Hide loading state
            if (loadingOverlay && loadingMessage) {
                loadingOverlay.style.display = 'none';
                loadingMessage.style.display = 'none';
            }
        });
    }
    
    showNotification(message, type = 'info') {
        const notification = document.getElementById('notification');
        
        if (notification) {
            notification.textContent = message;
            notification.className = `notification ${type}`;
            notification.style.display = 'block';
            
            // Hide after a delay
            setTimeout(() => {
                notification.style.display = 'none';
            }, 3000);
        }
    }

    /**
     * Update the board with a new state
     * @param {Object} boardState - Object mapping square names to pieces
     * @param {Array} legalMoves - Array of legal moves
     */
    updateBoard(boardState, legalMoves = []) {
        console.log('Updating board with new state');
        
        this.boardState = boardState;
        
        // Update legal moves
        if (legalMoves.length > 0) {
            this.legalMoves = legalMoves;
            console.log(`Updated legal moves (${legalMoves.length} moves)`);
        }
        
        this.updateBoardUI(boardState);
    }
    
    /**
     * Update just the UI representation of the board without changing the underlying board state
     * This is for optimistic UI updates
     * @param {Object} boardState - The board state to display
     */
    updateBoardUI(boardState) {
        // Clear all pieces from the board
        Object.values(this.squares).forEach(square => {
            square.innerHTML = '';
        });
        
        // Add pieces based on the new board state
        Object.entries(boardState).forEach(([squareId, piece]) => {
            const squareElement = this.squares[squareId];
            
            if (squareElement && piece) {
                const pieceElement = document.createElement('div');
                pieceElement.className = `piece ${piece.color}`;
                
                const img = document.createElement('img');
                img.src = this.pieceImages[piece.code];
                img.alt = `${piece.color} ${piece.type}`;
                img.draggable = false;
                
                pieceElement.appendChild(img);
                squareElement.appendChild(pieceElement);
            }
        });
        
        // Highlight the last move
        this.highlightLastMove();
    }

    /**
     * Highlight the last move
     */
    highlightLastMove() {
        // Clear previous highlights
        document.querySelectorAll('.last-move').forEach(square => {
            square.classList.remove('last-move');
        });
        
        // Add highlights to the squares involved in the last move
        if (this.lastMove) {
            const fromSquare = this.squares[this.lastMove.from];
            const toSquare = this.squares[this.lastMove.to];
            
            // Check if the squares exist before adding the class
            if (fromSquare) fromSquare.classList.add('last-move');
            if (toSquare) toSquare.classList.add('last-move');
        }
    }

    /**
     * Set the board orientation
     * @param {string} color - 'white' or 'black'
     */
    setOrientation(color) {
        if (color !== 'white' && color !== 'black') {
            console.error(`Invalid orientation: ${color}`);
            return;
        }
        
        this.orientation = color;
        this.boardElement.classList.remove('white-orientation', 'black-orientation');
        this.boardElement.classList.add(`${color}-orientation`);
    }

    /**
     * Show check on a specific square
     * @param {string} squareId - Square ID where the king is in check
     */
    showCheck(squareId) {
        const square = this.squares[squareId];
        if (square) {
            square.classList.add('check');
        }
    }

    /**
     * Clear check highlight
     */
    clearCheck() {
        document.querySelectorAll('.check').forEach(square => {
            square.classList.remove('check');
        });
    }

    isPieceFriendly(squareId) {
        const piece = this.boardState[squareId];
        // Consider the piece friendly if it's of the current turn color
        return piece && piece.color === this.getCurrentTurnColor();
    }
    
    getCurrentTurnColor() {
        // This should be replaced with actual turn tracking logic
        // For now, assume white is always the current turn
        return 'white';
    }
}

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChessBoard;
} 