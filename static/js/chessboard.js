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
        this.createBoard();
        this.setupEventListeners();
    }

    /**
     * Create the chessboard squares
     */
    createBoard() {
        this.boardElement.innerHTML = '';
        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const square = document.createElement('div');
                const isLight = (row + col) % 2 === 0;
                square.className = `square ${isLight ? 'light' : 'dark'}`;
                
                const file = String.fromCharCode(97 + col); // 'a' through 'h'
                const rank = 8 - row; // 8 through 1
                const squareId = `${file}${rank}`;
                
                square.id = squareId;
                square.dataset.file = file;
                square.dataset.rank = rank;
                
                this.boardElement.appendChild(square);
                this.squares[squareId] = square;
            }
        }
    }

    /**
     * Set up event listeners for squares
     */
    setupEventListeners() {
        for (const squareId in this.squares) {
            const square = this.squares[squareId];
            square.addEventListener('click', () => this.handleSquareClick(squareId));
        }
    }

    /**
     * Handle square click event
     * @param {string} squareId - ID of the clicked square (e.g., 'e4')
     */
    handleSquareClick(squareId) {
        console.log(`Square ${squareId} clicked`);
        
        // Check if we should handle this click
        const gameActiveEvent = new CustomEvent('checkGameActive', { 
            detail: { callback: (isActive, currentPlayer) => {
                if (!isActive) {
                    console.log("Game is not active, ignoring click");
                    return;
                }
                
                if (currentPlayer !== 'white') {
                    console.log("Not player's turn, ignoring click");
                    return;
                }
                
                this.handlePlayerSquareClick(squareId);
            }}
        });
        document.dispatchEvent(gameActiveEvent);
    }
    
    /**
     * Handle a valid player square click
     * @param {string} squareId - ID of the clicked square
     */
    handlePlayerSquareClick(squareId) {
        // If no piece is selected and the clicked square has a piece, select it
        if (!this.selectedSquare && this.boardState[squareId] && this.boardState[squareId].color === 'white') {
            this.selectSquare(squareId);
            return;
        }

        // If a piece is already selected
        if (this.selectedSquare) {
            // Check if the clicked square is a valid move
            const isLegalMove = this.legalMoves.some(move => {
                return move.from === this.selectedSquare && move.to === squareId;
            });

            if (isLegalMove) {
                // Make the move
                this.makeMove(this.selectedSquare, squareId);
            } else if (this.boardState[squareId] && this.boardState[squareId].color === 'white') {
                // If clicked on another own piece, select it instead
                this.deselectSquare();
                this.selectSquare(squareId);
            } else {
                // If clicked on an empty square or opponent's piece (not a legal move)
                this.deselectSquare();
            }
        }
    }

    /**
     * Select a square and highlight legal moves
     * @param {string} squareId - ID of the square to select
     */
    selectSquare(squareId) {
        this.selectedSquare = squareId;
        this.squares[squareId].classList.add('selected');
        
        // Highlight legal moves
        this.highlightLegalMoves();
    }

    /**
     * Deselect the currently selected square and clear highlights
     */
    deselectSquare() {
        if (this.selectedSquare) {
            this.squares[this.selectedSquare].classList.remove('selected');
            this.selectedSquare = null;
            
            // Remove all highlights
            for (const squareId in this.squares) {
                this.squares[squareId].classList.remove('highlight');
                this.squares[squareId].classList.remove('highlight-move');
                this.squares[squareId].classList.remove('highlight-capture');
            }
        }
    }

    /**
     * Highlight legal moves for the selected piece
     */
    highlightLegalMoves() {
        // Highlight moves that are available for the selected piece
        for (const move of this.legalMoves) {
            if (move.from === this.selectedSquare) {
                const targetSquare = this.squares[move.to];
                if (!targetSquare) continue; // Skip if square doesn't exist
                
                targetSquare.classList.add('highlight');
                
                // If it's a capture, add capture highlight
                if (this.boardState[move.to]) {
                    targetSquare.classList.add('highlight-capture');
                } else {
                    targetSquare.classList.add('highlight-move');
                }
            }
        }
    }

    /**
     * Make a move on the chessboard
     * @param {string} from - Starting square (e.g., 'e2')
     * @param {string} to - Target square (e.g., 'e4')
     */
    makeMove(from, to) {
        console.log(`Attempting to move from ${from} to ${to}`);
        
        // Validate the move
        const isLegalMove = this.legalMoves.some(move => {
            return move.from === from && move.to === to;
        });
        
        if (!isLegalMove) {
            console.error(`Move from ${from} to ${to} is not legal`);
            return false;
        }
        
        // Store the move for highlighting
        this.lastMove = { from, to };
        
        // Deselect the current square
        this.deselectSquare();
        
        // Make API call to backend
        this.sendMoveToBackend(from, to);
        
        return true;
    }
    
    /**
     * Send a move to the backend
     * @param {string} from - Starting square (e.g., 'e2')
     * @param {string} to - Target square (e.g., 'e4')
     */
    sendMoveToBackend(from, to) {
        console.log(`Sending move from ${from} to ${to} to backend`);
        
        // Trigger loading event
        const loadingEvent = new CustomEvent('showLoading', { 
            detail: { message: 'Processing move...' }
        });
        document.dispatchEvent(loadingEvent);
        
        fetch('/move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ from, to })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Move response:", data);
            
            if (data.valid) {
                // Update the board with the new state
                this.updateBoard(data.board, data.legalMoves || []);
                
                // Highlight the last move
                if (data.aiMove) {
                    this.lastMove = data.aiMove;
                    this.highlightLastMove();
                }
                
                // Handle game state
                if (data.gameState === 'ended') {
                    // Game has ended, trigger an event
                    const event = new CustomEvent('gameEnded', { 
                        detail: { 
                            winner: data.winner,
                            message: data.message
                        }
                    });
                    document.dispatchEvent(event);
                }
                
                // Trigger move completed event
                const moveEvent = new CustomEvent('moveCompleted', { 
                    detail: { 
                        valid: true,
                        player: 'white',
                        from: from,
                        to: to,
                        aiMove: data.aiMove,
                        currentPlayer: data.currentPlayer
                    }
                });
                document.dispatchEvent(moveEvent);
            } else {
                console.error("Move rejected:", data.message);
                
                // Trigger move failed event
                const moveEvent = new CustomEvent('moveFailed', { 
                    detail: { 
                        message: data.message
                    }
                });
                document.dispatchEvent(moveEvent);
                
                // Update the board to revert to valid state
                if (data.board) {
                    this.updateBoard(data.board, data.legalMoves || []);
                }
            }
            
            // Trigger hide loading event
            const hideLoadingEvent = new CustomEvent('hideLoading', {});
            document.dispatchEvent(hideLoadingEvent);
        })
        .catch(error => {
            console.error('Error sending move to backend:', error);
            
            // Trigger error event
            const errorEvent = new CustomEvent('moveError', { 
                detail: { error }
            });
            document.dispatchEvent(errorEvent);
            
            // Hide loading on error
            const hideLoadingEvent = new CustomEvent('hideLoading', {});
            document.dispatchEvent(hideLoadingEvent);
        });
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
            this.squares[this.lastMove.from].classList.add('last-move');
            this.squares[this.lastMove.to].classList.add('last-move');
        }
    }

    /**
     * Update the board with a new state
     * @param {Object} boardState - Object mapping square names to pieces
     * @param {Array} legalMoves - Array of legal moves
     */
    updateBoard(boardState, legalMoves = []) {
        console.log("Updating board with new state");
        
        // Deep copy the board state to avoid modifying the original
        const boardStateCopy = JSON.parse(JSON.stringify(boardState || {}));
        
        // Clear all pieces from the board
        for (const squareId in this.squares) {
            const square = this.squares[squareId];
            while (square.firstChild) {
                square.removeChild(square.firstChild);
            }
            
            // Ensure no text content is left in the square
            square.textContent = '';
        }
        
        // Check if the boardState is valid
        if (!boardStateCopy || typeof boardStateCopy !== 'object') {
            console.error("Invalid boardState received:", boardStateCopy);
            return;
        }

        // Validate that we have the expected number of pieces
        const pieceCount = Object.keys(boardStateCopy).length;
        if (pieceCount < 32) {
            console.warn(`Board only has ${pieceCount} pieces, which is less than the expected 32 pieces.`);
            
            // Create a special check for missing key pieces (a8 rook, h7 pawn, white pieces)
            const criticalPieces = {
                // Black back rank
                'a8': { type: 'r', color: 'black' },  // Black a-rook
                'b8': { type: 'n', color: 'black' },  // Black b-knight
                'c8': { type: 'b', color: 'black' },  // Black c-bishop
                'd8': { type: 'q', color: 'black' },  // Black d-queen
                'e8': { type: 'k', color: 'black' },  // Black e-king
                'f8': { type: 'b', color: 'black' },  // Black f-bishop
                'g8': { type: 'n', color: 'black' },  // Black g-knight
                'h8': { type: 'r', color: 'black' },  // Black h-rook
                
                // Black pawns
                'a7': { type: 'p', color: 'black' },
                'b7': { type: 'p', color: 'black' },
                'c7': { type: 'p', color: 'black' },
                'd7': { type: 'p', color: 'black' },
                'e7': { type: 'p', color: 'black' },
                'f7': { type: 'p', color: 'black' },
                'g7': { type: 'p', color: 'black' },
                'h7': { type: 'p', color: 'black' },
                
                // White back rank
                'a1': { type: 'r', color: 'white' },
                'b1': { type: 'n', color: 'white' },
                'c1': { type: 'b', color: 'white' },
                'd1': { type: 'q', color: 'white' },
                'e1': { type: 'k', color: 'white' },
                'f1': { type: 'b', color: 'white' },
                'g1': { type: 'n', color: 'white' },
                'h1': { type: 'r', color: 'white' },
                
                // White pawns
                'a2': { type: 'p', color: 'white' },
                'b2': { type: 'p', color: 'white' },
                'c2': { type: 'p', color: 'white' },
                'd2': { type: 'p', color: 'white' },
                'e2': { type: 'p', color: 'white' },
                'f2': { type: 'p', color: 'white' },
                'g2': { type: 'p', color: 'white' },
                'h2': { type: 'p', color: 'white' }
            };
            
            // Check for specific missing pieces and add them if needed
            for (const squareId in criticalPieces) {
                if (!boardStateCopy[squareId]) {
                    console.warn(`Adding missing piece at ${squareId}: ${criticalPieces[squareId].color} ${criticalPieces[squareId].type}`);
                    boardStateCopy[squareId] = criticalPieces[squareId];
                    
                    // Add code property if any existing piece has it
                    const anyPiece = Object.values(boardStateCopy)[0];
                    if (anyPiece && 'code' in anyPiece) {
                        const pieceType = criticalPieces[squareId].type;
                        boardStateCopy[squareId].code = criticalPieces[squareId].color === 'white' ? 
                            pieceType.toUpperCase() : pieceType;
                    }
                }
            }
        }

        // Update our internal boardState
        this.boardState = boardStateCopy;
        
        // Place pieces on the board
        for (const squareId in boardStateCopy) {
            const piece = boardStateCopy[squareId];
            this.placePiece(squareId, piece.type, piece.color);
        }
        
        // Update legal moves
        this.legalMoves = legalMoves || [];
        
        // Highlight the last move
        this.highlightLastMove();
        
        // If a square is selected, highlight legal moves from that square
        if (this.selectedSquare) {
            this.highlightLegalMoves();
        }
    }

    /**
     * Place a piece on the board
     * @param {string} squareId - Square ID (e.g., 'e4')
     * @param {string} pieceType - Type of piece (e.g., 'pawn', 'rook', 'knight', etc.)
     * @param {string} pieceColor - Color of the piece ('white' or 'black')
     */
    placePiece(squareId, pieceType, pieceColor) {
        console.log(`Placing ${pieceColor} ${pieceType} on ${squareId}`);
        const square = this.squares[squareId];
        if (!square) {
            console.error(`Square ${squareId} not found`);
            return;
        }
        
        // Clear any existing piece and ensure no text content
        while (square.firstChild) {
            square.removeChild(square.firstChild);
        }
        square.textContent = '';
        
        const pieceElement = document.createElement('div');
        pieceElement.className = 'piece';
        
        // Validate inputs to prevent issues
        if (!pieceType || typeof pieceType !== 'string' || pieceType.length === 0) {
            console.error(`Invalid piece type: ${pieceType}`);
            return;
        }
        
        if (!pieceColor || typeof pieceColor !== 'string' || 
            (pieceColor !== 'white' && pieceColor !== 'black')) {
            console.error(`Invalid piece color: ${pieceColor}`);
            return;
        }
        
        // Map the full piece type to its one-letter code and the correct icon name
        const pieceTypeMap = {
            'p': { code: 'p', name: 'pawn' },
            'r': { code: 'r', name: 'rook' },
            'n': { code: 'n', name: 'knight' },
            'b': { code: 'b', name: 'bishop' },
            'q': { code: 'q', name: 'queen' },
            'k': { code: 'k', name: 'king' },
            'pawn': { code: 'p', name: 'pawn' },
            'rook': { code: 'r', name: 'rook' },
            'knight': { code: 'n', name: 'knight' },
            'bishop': { code: 'b', name: 'bishop' },
            'queen': { code: 'q', name: 'queen' },
            'king': { code: 'k', name: 'king' }
        };
        
        // Get the normalized piece info
        const pieceInfo = pieceTypeMap[pieceType.toLowerCase()];
        
        if (!pieceInfo) {
            console.error(`Unknown piece type: ${pieceType}`);
            return;
        }
        
        // Get the piece code and name
        let pieceCode = pieceInfo.code;
        const pieceName = pieceInfo.name;
        
        // Uppercase for white pieces
        if (pieceColor === 'white') {
            pieceCode = pieceCode.toUpperCase();
        }
        
        console.log(`Mapped ${pieceColor} ${pieceType} to piece code ${pieceCode}, name ${pieceName}`);
        
        // Create the image path
        const imagePath = `/static/images/pieces/${pieceColor}-${pieceName}.svg`;
        
        // Create an img element for the SVG
        const imgElement = document.createElement('img');
        
        // Use the pieceImages mapping if available, fallback to constructed path
        if (this.pieceImages[pieceCode]) {
            imgElement.src = this.pieceImages[pieceCode];
        } else {
            console.warn(`No image mapping found for piece code ${pieceCode}, using calculated path instead`);
            imgElement.src = imagePath;
        }
        
        imgElement.alt = `${pieceColor} ${pieceType}`;
        imgElement.draggable = false; // Prevent default drag behavior
        
        // Append the image to the piece element, then to the square
        pieceElement.appendChild(imgElement);
        square.appendChild(pieceElement);
    }

    /**
     * Set the board orientation
     * @param {string} color - 'white' or 'black'
     */
    setOrientation(color) {
        this.orientation = color;
        
        // Implement flipping the board if needed
        if (color === 'black') {
            this.boardElement.style.transform = 'rotate(180deg)';
            document.querySelectorAll('.piece img').forEach(piece => {
                piece.style.transform = 'rotate(180deg)';
            });
        } else {
            this.boardElement.style.transform = 'none';
            document.querySelectorAll('.piece img').forEach(piece => {
                piece.style.transform = 'none';
            });
        }
    }

    /**
     * Show check highlight for the king
     * @param {string} squareId - Square ID of the king in check
     */
    showCheck(squareId) {
        if (this.squares[squareId]) {
            this.squares[squareId].classList.add('highlight-check');
        }
    }

    /**
     * Clear check highlight
     */
    clearCheck() {
        document.querySelectorAll('.highlight-check').forEach(element => {
            element.classList.remove('highlight-check');
        });
    }
} 