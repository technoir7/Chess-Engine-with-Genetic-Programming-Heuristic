/**
 * Tests for chess piece movement in the web UI
 */

describe('Chess Piece Movement', () => {
    let chessboard;
    let originalFetch;
    
    // Mock fetch API for testing
    function setupFetchMock(responseData) {
        window.fetch = jest.fn().mockImplementation(() => {
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve(responseData)
            });
        });
    }
    
    // Setup before each test
    beforeEach(() => {
        // Save original fetch
        originalFetch = window.fetch;
        
        // Create the required HTML structure
        document.body.innerHTML = `
            <div id="chessboard"></div>
            <div id="game-status"></div>
            <div id="move-history"></div>
            <div id="loading-overlay"></div>
            <div id="loading-message"></div>
            <div id="notification"></div>
        `;
        
        // Initialize the chessboard
        chessboard = new ChessBoard();
        
        // Set up an initial board state with all pieces in starting positions
        const initialBoardState = {
            // White pieces
            'a1': { type: 'r', color: 'white', code: 'R' },
            'b1': { type: 'n', color: 'white', code: 'N' },
            'c1': { type: 'b', color: 'white', code: 'B' },
            'd1': { type: 'q', color: 'white', code: 'Q' },
            'e1': { type: 'k', color: 'white', code: 'K' },
            'f1': { type: 'b', color: 'white', code: 'B' },
            'g1': { type: 'n', color: 'white', code: 'N' },
            'h1': { type: 'r', color: 'white', code: 'R' },
            'a2': { type: 'p', color: 'white', code: 'P' },
            'b2': { type: 'p', color: 'white', code: 'P' },
            'c2': { type: 'p', color: 'white', code: 'P' },
            'd2': { type: 'p', color: 'white', code: 'P' },
            'e2': { type: 'p', color: 'white', code: 'P' },
            'f2': { type: 'p', color: 'white', code: 'P' },
            'g2': { type: 'p', color: 'white', code: 'P' },
            'h2': { type: 'p', color: 'white', code: 'P' },
            
            // Black pieces
            'a8': { type: 'r', color: 'black', code: 'r' },
            'b8': { type: 'n', color: 'black', code: 'n' },
            'c8': { type: 'b', color: 'black', code: 'b' },
            'd8': { type: 'q', color: 'black', code: 'q' },
            'e8': { type: 'k', color: 'black', code: 'k' },
            'f8': { type: 'b', color: 'black', code: 'b' },
            'g8': { type: 'n', color: 'black', code: 'n' },
            'h8': { type: 'r', color: 'black', code: 'r' },
            'a7': { type: 'p', color: 'black', code: 'p' },
            'b7': { type: 'p', color: 'black', code: 'p' },
            'c7': { type: 'p', color: 'black', code: 'p' },
            'd7': { type: 'p', color: 'black', code: 'p' },
            'e7': { type: 'p', color: 'black', code: 'p' },
            'f7': { type: 'p', color: 'black', code: 'p' },
            'g7': { type: 'p', color: 'black', code: 'p' },
            'h7': { type: 'p', color: 'black', code: 'p' }
        };
        
        // Initial legal moves for white (pawn and knight moves)
        const initialLegalMoves = [
            { from: 'a2', to: 'a3' },
            { from: 'a2', to: 'a4' },
            { from: 'b2', to: 'b3' },
            { from: 'b2', to: 'b4' },
            { from: 'c2', to: 'c3' },
            { from: 'c2', to: 'c4' },
            { from: 'd2', to: 'd3' },
            { from: 'd2', to: 'd4' },
            { from: 'e2', to: 'e3' },
            { from: 'e2', to: 'e4' },
            { from: 'f2', to: 'f3' },
            { from: 'f2', to: 'f4' },
            { from: 'g2', to: 'g3' },
            { from: 'g2', to: 'g4' },
            { from: 'h2', to: 'h3' },
            { from: 'h2', to: 'h4' },
            { from: 'b1', to: 'a3' },
            { from: 'b1', to: 'c3' },
            { from: 'g1', to: 'f3' },
            { from: 'g1', to: 'h3' }
        ];
        
        // Initialize the board
        chessboard.updateBoard(initialBoardState, initialLegalMoves);
        
        // Setup game active event handler
        document.addEventListener('checkGameActive', (event) => {
            if (event.detail && typeof event.detail.callback === 'function') {
                event.detail.callback(true, 'white');
            }
        });
    });
    
    // Clean up after each test
    afterEach(() => {
        document.body.innerHTML = '';
        chessboard = null;
        window.fetch = originalFetch;
        
        // Remove all event listeners
        const oldElement = document;
        const newElement = oldElement.cloneNode(true);
        oldElement.parentNode.replaceChild(newElement, oldElement);
    });
    
    // Test: User can select a piece
    test('should select a piece when clicked', () => {
        // Click on the e2 pawn
        const e2Square = chessboard.squares['e2'];
        e2Square.click();
        
        // Should have selected the square
        expect(chessboard.selectedSquare).toBe('e2');
        expect(e2Square.classList.contains('selected')).toBe(true);
        
        // Should have highlighted legal moves
        const e3Square = chessboard.squares['e3'];
        const e4Square = chessboard.squares['e4'];
        
        expect(e3Square.classList.contains('highlight')).toBe(true);
        expect(e4Square.classList.contains('highlight')).toBe(true);
    });
    
    // Test: User can move a piece to a legal square
    test('should move a piece to a legal square when clicked', async () => {
        // Mock the fetch response for a successful move
        const moveResponseData = {
            valid: true,
            board: {
                // Updated board state after e2-e4 move
                'a1': { type: 'r', color: 'white', code: 'R' },
                'b1': { type: 'n', color: 'white', code: 'N' },
                'c1': { type: 'b', color: 'white', code: 'B' },
                'd1': { type: 'q', color: 'white', code: 'Q' },
                'e1': { type: 'k', color: 'white', code: 'K' },
                'f1': { type: 'b', color: 'white', code: 'B' },
                'g1': { type: 'n', color: 'white', code: 'N' },
                'h1': { type: 'r', color: 'white', code: 'R' },
                'a2': { type: 'p', color: 'white', code: 'P' },
                'b2': { type: 'p', color: 'white', code: 'P' },
                'c2': { type: 'p', color: 'white', code: 'P' },
                'd2': { type: 'p', color: 'white', code: 'P' },
                'e4': { type: 'p', color: 'white', code: 'P' }, // Pawn moved from e2 to e4
                'f2': { type: 'p', color: 'white', code: 'P' },
                'g2': { type: 'p', color: 'white', code: 'P' },
                'h2': { type: 'p', color: 'white', code: 'P' },
                
                // Black pieces (unchanged)
                'a8': { type: 'r', color: 'black', code: 'r' },
                'b8': { type: 'n', color: 'black', code: 'n' },
                'c8': { type: 'b', color: 'black', code: 'b' },
                'd8': { type: 'q', color: 'black', code: 'q' },
                'e8': { type: 'k', color: 'black', code: 'k' },
                'f8': { type: 'b', color: 'black', code: 'b' },
                'g8': { type: 'n', color: 'black', code: 'n' },
                'h8': { type: 'r', color: 'black', code: 'r' },
                'a7': { type: 'p', color: 'black', code: 'p' },
                'b7': { type: 'p', color: 'black', code: 'p' },
                'c7': { type: 'p', color: 'black', code: 'p' },
                'd7': { type: 'p', color: 'black', code: 'p' },
                'e7': { type: 'p', color: 'black', code: 'p' },
                'f7': { type: 'p', color: 'black', code: 'p' },
                'g7': { type: 'p', color: 'black', code: 'p' },
                'h7': { type: 'p', color: 'black', code: 'p' }
            },
            legalMoves: [], // Empty for simplicity in this test
            aiMove: { from: 'e7', to: 'e5' }, // AI's response move
            currentPlayer: 'white'
        };
        
        setupFetchMock(moveResponseData);
        
        // Click on the e2 pawn to select it
        const e2Square = chessboard.squares['e2'];
        e2Square.click();
        
        // Verify it's selected
        expect(chessboard.selectedSquare).toBe('e2');
        
        // Click on e4 to move there
        const e4Square = chessboard.squares['e4'];
        e4Square.click();
        
        // Wait for the asynchronous fetch to complete
        await new Promise(resolve => setTimeout(resolve, 0));
        
        // Verify fetch was called with the right parameters
        expect(window.fetch).toHaveBeenCalledWith('/move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ from: 'e2', to: 'e4' })
        });
        
        // Check that the board was updated correctly
        expect(chessboard.boardState['e4']).toBeDefined();
        expect(chessboard.boardState['e2']).toBeUndefined();
        expect(chessboard.boardState['e4'].type).toBe('p');
        expect(chessboard.boardState['e4'].color).toBe('white');
        
        // Check that the piece is visually on e4
        const pieceOnE4 = e4Square.querySelector('.piece');
        expect(pieceOnE4).not.toBeNull();
        
        // Check that there's no piece on e2
        const pieceOnE2 = e2Square.querySelector('.piece');
        expect(pieceOnE2).toBeNull();
        
        // Verify last move is set and highlighted
        expect(chessboard.lastMove).toEqual({ from: 'e7', to: 'e5' });
    });
    
    // Test: Cannot move a piece to an illegal square
    test('should not move a piece to an illegal square', async () => {
        // Select the e2 pawn
        const e2Square = chessboard.squares['e2'];
        e2Square.click();
        
        // Attempt to move to e5, which is not a legal move
        const e5Square = chessboard.squares['e5'];
        e5Square.click();
        
        // Verify the pawn wasn't moved (no fetch call should be made)
        expect(window.fetch).not.toHaveBeenCalled();
        
        // Ensure e2 still has the pawn
        expect(chessboard.boardState['e2']).toBeDefined();
        expect(chessboard.boardState['e2'].type).toBe('p');
        expect(chessboard.boardState['e2'].color).toBe('white');
    });
    
    // Test: User can select another piece after deselecting
    test('should allow selecting another piece after deselecting', () => {
        // Click on the e2 pawn to select it
        const e2Square = chessboard.squares['e2'];
        e2Square.click();
        
        // Verify it's selected
        expect(chessboard.selectedSquare).toBe('e2');
        
        // Click on an empty square to deselect
        const e5Square = chessboard.squares['e5'];
        e5Square.click();
        
        // Verify no square is selected
        expect(chessboard.selectedSquare).toBeNull();
        
        // Now click on the d2 pawn
        const d2Square = chessboard.squares['d2'];
        d2Square.click();
        
        // Verify d2 is now selected
        expect(chessboard.selectedSquare).toBe('d2');
    });
    
    // Test: User can select another own piece to change selection
    test('should change selection when clicking another own piece', () => {
        // Click on the e2 pawn to select it
        const e2Square = chessboard.squares['e2'];
        e2Square.click();
        
        // Verify it's selected
        expect(chessboard.selectedSquare).toBe('e2');
        
        // Click on another white piece (d2 pawn)
        const d2Square = chessboard.squares['d2'];
        d2Square.click();
        
        // Verify d2 is now selected instead of e2
        expect(chessboard.selectedSquare).toBe('d2');
        expect(e2Square.classList.contains('selected')).toBe(false);
        expect(d2Square.classList.contains('selected')).toBe(true);
    });
}); 