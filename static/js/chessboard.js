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
    }

    /**
     * Initialize the chessboard
     */
    init() {
        console.log('Initializing chessboard');
        this.createBoard();
        this.setupEventListeners();
        
        // Add default legal moves for initial position
        this.addDefaultLegalMoves();
        
        // Ensure legal moves are highlighted properly
        if (this.selectedSquare) {
            this.highlightLegalMoves();
        }
        
        console.log('Chessboard initialized');
    }

    /**
     * Add default legal moves for initial position
     * This ensures pawns can move even if the server doesn't provide legal moves
     */
    addDefaultLegalMoves() {
        console.log('Adding default legal moves for initial position');
        
        // Clear existing legal moves to avoid duplicates
        this.legalMoves = [];
        
        // Add pawn moves for white pawns (from rank 2)
        const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
        
        files.forEach(file => {
            // White pawns can move one or two squares forward from rank 2
            this.legalMoves.push({ from: `${file}2`, to: `${file}3` });
            this.legalMoves.push({ from: `${file}2`, to: `${file}4` });
            
            // Black pawns can move one or two squares forward from rank 7
            this.legalMoves.push({ from: `${file}7`, to: `${file}6` });
            this.legalMoves.push({ from: `${file}7`, to: `${file}5` });
        });
        
        // Add knight moves for both colors
        // White knights
        this.legalMoves.push({ from: 'b1', to: 'a3' });
        this.legalMoves.push({ from: 'b1', to: 'c3' });
        this.legalMoves.push({ from: 'g1', to: 'f3' });
        this.legalMoves.push({ from: 'g1', to: 'h3' });
        
        // Black knights
        this.legalMoves.push({ from: 'b8', to: 'a6' });
        this.legalMoves.push({ from: 'b8', to: 'c6' });
        this.legalMoves.push({ from: 'g8', to: 'f6' });
        this.legalMoves.push({ from: 'g8', to: 'h6' });
        
        console.log(`Added ${this.legalMoves.length} default legal moves`);
        console.log('Default moves:', this.legalMoves.map(m => `${m.from}->${m.to}`).join(', '));
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
        console.log(`Player clicked ${squareId}`);
        
        // Check if a square is already selected
        if (this.selectedSquare) {
            // If the same square is clicked again, deselect it
            if (this.selectedSquare === squareId) {
                console.log(`Deselecting ${squareId}`);
                this.deselectSquare();
                return;
            }
            
            // Check if the move is legal
            if (this.isLegalMove(this.selectedSquare, squareId)) {
                console.log(`Legal move from ${this.selectedSquare} to ${squareId}`);
                
                // Make the move
                this.makeMove(this.selectedSquare, squareId);
                
                // Reset selection
                this.deselectSquare();
            } else {
                console.log(`Deselecting ${this.selectedSquare} as the move to ${squareId} isn't valid`);
                
                // If the clicked square contains a friendly piece, select it instead
                if (this.isPieceFriendly(squareId)) {
                    console.log(`Selecting ${squareId} as it contains a friendly piece`);
                    this.selectSquare(squareId);
                } else {
                    // Otherwise just deselect the current square
                    this.deselectSquare();
                }
            }
        } 
        // No square selected, try to select this one if it contains a friendly piece
        else if (this.isPieceFriendly(squareId)) {
            console.log(`Selecting ${squareId}`);
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
        
        // First check if the move is in the list of legal moves
        for (const move of this.legalMoves) {
            if (move.from === from && move.to === to) {
                console.log(`Found move in legal moves list: ${from} to ${to}`);
                return true;
            }
        }
        
        console.log(`Move ${from} to ${to} not found in legal moves list. Checking fallback rules...`);
        
        // Fallback rules for initial pawn moves (white)
        if (this.boardState[from] && this.boardState[from].type === 'p' && 
            this.boardState[from].color === 'white') {
            
            // White pawns move up (decrease row number)
            const fromCol = from.charAt(0);
            const fromRow = parseInt(from.charAt(1));
            const toCol = to.charAt(0);
            const toRow = parseInt(to.charAt(1));
            
            // Check if it's a valid pawn move
            if (fromCol === toCol) {
                // Straight move - check if destination is empty
                if (!this.boardState[to]) {
                    // One square forward
                    if (toRow === fromRow + 1) {
                        console.log(`Valid white pawn move: ${from} to ${to} (one square forward)`);
                        return true;
                    }
                    
                    // Two squares forward from starting position
                    if (fromRow === 2 && toRow === 4 && !this.boardState[`${fromCol}3`]) {
                        console.log(`Valid white pawn move: ${from} to ${to} (two squares from start)`);
                        return true;
                    }
                }
            } 
            // Diagonal capture
            else if ((toCol === String.fromCharCode(fromCol.charCodeAt(0) - 1) || 
                     toCol === String.fromCharCode(fromCol.charCodeAt(0) + 1)) && 
                     toRow === fromRow + 1) {
                
                // Check if there's an opponent's piece to capture
                if (this.boardState[to] && this.boardState[to].color === 'black') {
                    console.log(`Valid white pawn capture: ${from} to ${to}`);
                    return true;
                }
            }
        }
        
        // Fallback rules for initial pawn moves (black)
        if (this.boardState[from] && this.boardState[from].type === 'p' && 
            this.boardState[from].color === 'black') {
            
            // Black pawns move down (increase row number)
            const fromCol = from.charAt(0);
            const fromRow = parseInt(from.charAt(1));
            const toCol = to.charAt(0);
            const toRow = parseInt(to.charAt(1));
            
            // Check if it's a valid pawn move
            if (fromCol === toCol) {
                // Straight move - check if destination is empty
                if (!this.boardState[to]) {
                    // One square forward
                    if (toRow === fromRow - 1) {
                        console.log(`Valid black pawn move: ${from} to ${to} (one square forward)`);
                        return true;
                    }
                    
                    // Two squares forward from starting position
                    if (fromRow === 7 && toRow === 5 && !this.boardState[`${fromCol}6`]) {
                        console.log(`Valid black pawn move: ${from} to ${to} (two squares from start)`);
                        return true;
                    }
                }
            } 
            // Diagonal capture
            else if ((toCol === String.fromCharCode(fromCol.charCodeAt(0) - 1) || 
                     toCol === String.fromCharCode(fromCol.charCodeAt(0) + 1)) && 
                     toRow === fromRow - 1) {
                
                // Check if there's an opponent's piece to capture
                if (this.boardState[to] && this.boardState[to].color === 'white') {
                    console.log(`Valid black pawn capture: ${from} to ${to}`);
                    return true;
                }
            }
        }
        
        // Fallback rules for knight moves
        if (this.boardState[from] && this.boardState[from].type === 'n') {
            const fromCol = from.charCodeAt(0) - 'a'.charCodeAt(0);
            const fromRow = parseInt(from.charAt(1)) - 1;
            const toCol = to.charCodeAt(0) - 'a'.charCodeAt(0);
            const toRow = parseInt(to.charAt(1)) - 1;
            
            // Knight moves in L-shape: 2 squares in one direction and 1 square in the perpendicular direction
            const colDiff = Math.abs(toCol - fromCol);
            const rowDiff = Math.abs(toRow - fromRow);
            
            if ((colDiff === 1 && rowDiff === 2) || (colDiff === 2 && rowDiff === 1)) {
                // Check if destination square doesn't contain a friendly piece
                if (!this.boardState[to] || this.boardState[to].color !== this.boardState[from].color) {
                    console.log(`Valid knight move: ${from} to ${to}`);
                    return true;
                }
            }
        }
        
        console.log(`Move ${from} to ${to} is not legal according to fallback rules`);
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
        if (!this.selectedSquare) {
            console.log('No square selected, cannot highlight legal moves');
            return;
        }
        
        console.log(`Highlighting legal moves for ${this.selectedSquare}`);
        
        // Remove any existing highlights first
        this.removeAllHighlights();
        
        let highlightCount = 0;
        
        // First try to highlight moves from the legal moves array
        this.legalMoves.forEach(move => {
            if (move.from === this.selectedSquare) {
                const squareElement = this.squares[move.to];
                if (squareElement) {
                    squareElement.classList.add('highlight');
                    
                    // If there's a piece on the target square, it's a capture
                    if (this.boardState[move.to]) {
                        squareElement.classList.add('capture');
                        console.log(`Highlighted ${move.to} as capture`);
                    } else {
                        console.log(`Highlighted ${move.to} as regular move`);
                    }
                    
                    highlightCount++;
                }
            }
        });
        
        // If no legal moves were highlighted, use fallback rules
        if (highlightCount === 0) {
            console.log(`No legal moves found in array for ${this.selectedSquare}, using fallback rules`);
            this.highlightFallbackLegalMoves();
            
            // Count highlighted squares after fallback
            const highlightedSquares = document.querySelectorAll('.square.highlight');
            console.log(`Fallback highlighting added ${highlightedSquares.length} moves`);
        } else {
            console.log(`Highlighted ${highlightCount} legal moves for ${this.selectedSquare}`);
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
        let highlightCount = 0;
        
        // Implement basic chess rules for pawns
        if (piece.type.toLowerCase() === 'p') {
            if (piece.color === 'white') {
                // One square forward
                const oneSquareForward = `${file}${rank + 1}`;
                if (this.squares[oneSquareForward] && !this.boardState[oneSquareForward]) {
                    this.squares[oneSquareForward].classList.add('highlight');
                    console.log(`Fallback: Highlighted ${oneSquareForward} for white pawn`);
                    highlightCount++;
                }
                
                // Two squares forward from starting position
                if (rank === 2) {
                    const twoSquaresForward = `${file}4`;
                    const intermediateSquare = `${file}3`;
                    if (this.squares[twoSquaresForward] && !this.boardState[intermediateSquare] && !this.boardState[twoSquaresForward]) {
                        this.squares[twoSquaresForward].classList.add('highlight');
                        console.log(`Fallback: Highlighted ${twoSquaresForward} for white pawn from starting position`);
                        highlightCount++;
                    }
                }
                
                // Captures
                const leftCapture = String.fromCharCode(file.charCodeAt(0) - 1) + (rank + 1);
                const rightCapture = String.fromCharCode(file.charCodeAt(0) + 1) + (rank + 1);
                
                if (this.squares[leftCapture] && this.boardState[leftCapture] && 
                    this.boardState[leftCapture].color === 'black') {
                    this.squares[leftCapture].classList.add('highlight', 'capture');
                    console.log(`Fallback: Highlighted ${leftCapture} for white pawn capture`);
                    highlightCount++;
                }
                
                if (this.squares[rightCapture] && this.boardState[rightCapture] && 
                    this.boardState[rightCapture].color === 'black') {
                    this.squares[rightCapture].classList.add('highlight', 'capture');
                    console.log(`Fallback: Highlighted ${rightCapture} for white pawn capture`);
                    highlightCount++;
                }
            } else {
                // Black pawns
                // One square forward
                const oneSquareForward = `${file}${rank - 1}`;
                if (this.squares[oneSquareForward] && !this.boardState[oneSquareForward]) {
                    this.squares[oneSquareForward].classList.add('highlight');
                    console.log(`Fallback: Highlighted ${oneSquareForward} for black pawn`);
                    highlightCount++;
                }
                
                // Two squares forward from starting position
                if (rank === 7) {
                    const twoSquaresForward = `${file}5`;
                    const intermediateSquare = `${file}6`;
                    if (this.squares[twoSquaresForward] && !this.boardState[intermediateSquare] && !this.boardState[twoSquaresForward]) {
                        this.squares[twoSquaresForward].classList.add('highlight');
                        console.log(`Fallback: Highlighted ${twoSquaresForward} for black pawn from starting position`);
                        highlightCount++;
                    }
                }
                
                // Captures
                const leftCapture = String.fromCharCode(file.charCodeAt(0) - 1) + (rank - 1);
                const rightCapture = String.fromCharCode(file.charCodeAt(0) + 1) + (rank - 1);
                
                if (this.squares[leftCapture] && this.boardState[leftCapture] && 
                    this.boardState[leftCapture].color === 'white') {
                    this.squares[leftCapture].classList.add('highlight', 'capture');
                    console.log(`Fallback: Highlighted ${leftCapture} for black pawn capture`);
                    highlightCount++;
                }
                
                if (this.squares[rightCapture] && this.boardState[rightCapture] && 
                    this.boardState[rightCapture].color === 'white') {
                    this.squares[rightCapture].classList.add('highlight', 'capture');
                    console.log(`Fallback: Highlighted ${rightCapture} for black pawn capture`);
                    highlightCount++;
                }
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
     * Make a move on the board
     * @param {string} from - Starting square
     * @param {string} to - Target square
     */
    makeMove(from, to) {
        console.log(`Making move from ${from} to ${to}`);
        
        // Get the moving piece
        const movingPiece = this.boardState[from];
        
        if (!movingPiece) {
            console.error(`No piece found at ${from}`);
            return;
        }
        
        // Store the original board state before making the move
        const originalBoardState = { ...this.boardState };
        
        // Create new board state (optimistic update)
        const newBoardState = { ...this.boardState };
        newBoardState[to] = { ...newBoardState[from] };
        delete newBoardState[from];
        
        // Update the UI optimistically
        this.updateBoardUI(newBoardState);
        
        // Update the last move highlight
        this.updateLastMoveHighlight(from, to);
        
        // Deselect the square
        this.deselectSquare();
        
        // Send move to backend
        this.sendMoveToBackend(from, to, movingPiece, originalBoardState);
        
        // Update the internal board state with the optimistic update
        this.boardState = newBoardState;
        
        console.log(`Move completed from ${from} to ${to}`);
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
        console.log('Updating board state');
        
        // Update board state
        this.boardState = boardState;
        
        // Update legal moves if provided, otherwise keep existing ones
        if (legalMoves && Array.isArray(legalMoves)) {
            console.log(`Setting ${legalMoves.length} legal moves`);
            this.legalMoves = legalMoves;
            
            // If no legal moves are provided, add default ones
            if (this.legalMoves.length === 0) {
                console.log('No legal moves provided, adding default legal moves');
                this.addDefaultLegalMoves();
            }
        }
        
        // Update board UI
        this.updateBoardUI(boardState);
        
        // Highlight last move if any
        if (this.lastMove) {
            this.highlightLastMove();
        }
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