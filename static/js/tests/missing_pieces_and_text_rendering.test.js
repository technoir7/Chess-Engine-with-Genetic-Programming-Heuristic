/**
 * Tests specifically for missing pieces and erroneous text rendering issues
 */

describe('ChessBoard Rendering Issues', () => {
    let chessboard;
    
    // Setup before each test
    beforeEach(() => {
        // Create a mock board element
        document.body.innerHTML = '<div id="chessboard"></div>';
        
        // Initialize the chessboard
        chessboard = new ChessBoard();
    });
    
    // Clean up after each test
    afterEach(() => {
        document.body.innerHTML = '';
        chessboard = null;
    });
    
    test('should render black rook on a8 and black pawn on h7 correctly', () => {
        // Create a board state with specific pieces that are reported missing
        const boardState = {
            'a8': { type: 'r', color: 'black' },
            'h7': { type: 'p', color: 'black' }
        };
        
        // Update board with these pieces
        chessboard.updateBoard(boardState);
        
        // Check black rook at a8
        const rookSquare = chessboard.squares['a8'];
        const rookPiece = rookSquare.querySelector('.piece');
        expect(rookPiece).not.toBeNull();
        
        const rookImg = rookPiece.querySelector('img');
        expect(rookImg).not.toBeNull();
        expect(rookImg.src).toContain('/static/images/pieces/black-rook.svg');
        expect(rookImg.alt).toBe('black r');
        
        // Check black pawn at h7
        const pawnSquare = chessboard.squares['h7'];
        const pawnPiece = pawnSquare.querySelector('.piece');
        expect(pawnPiece).not.toBeNull();
        
        const pawnImg = pawnPiece.querySelector('img');
        expect(pawnImg).not.toBeNull();
        expect(pawnImg.src).toContain('/static/images/pieces/black-pawn.svg');
        expect(pawnImg.alt).toBe('black p');
        
        // Ensure no "black" text is visible on the squares
        expect(rookSquare.textContent.trim()).not.toContain('black');
        expect(pawnSquare.textContent.trim()).not.toContain('black');
    });
    
    test('should render all white pieces correctly', () => {
        // Create a board state with all white pieces
        const whitePositions = {
            'a1': { type: 'r', color: 'white' },
            'b1': { type: 'n', color: 'white' },
            'c1': { type: 'b', color: 'white' },
            'd1': { type: 'q', color: 'white' },
            'e1': { type: 'k', color: 'white' },
            'f1': { type: 'b', color: 'white' },
            'g1': { type: 'n', color: 'white' },
            'h1': { type: 'r', color: 'white' },
            'a2': { type: 'p', color: 'white' },
            'b2': { type: 'p', color: 'white' },
            'c2': { type: 'p', color: 'white' },
            'd2': { type: 'p', color: 'white' },
            'e2': { type: 'p', color: 'white' },
            'f2': { type: 'p', color: 'white' },
            'g2': { type: 'p', color: 'white' },
            'h2': { type: 'p', color: 'white' }
        };
        
        // Update board with white pieces
        chessboard.updateBoard(whitePositions);
        
        // Check that all white pieces are correctly rendered
        for (const [square, piece] of Object.entries(whitePositions)) {
            const squareElement = chessboard.squares[square];
            const pieceElement = squareElement.querySelector('.piece');
            
            expect(pieceElement).not.toBeNull();
            
            const imgElement = pieceElement.querySelector('img');
            expect(imgElement).not.toBeNull();
            expect(imgElement.src).toContain(`/static/images/pieces/white-${piece.type}.svg`);
            expect(imgElement.alt).toBe(`white ${piece.type}`);
            
            // Ensure no "white" text is visible on the square
            expect(squareElement.textContent.trim()).not.toContain('white');
        }
    });
    
    test('should not display raw text on board squares', () => {
        // Create a complete board state with all 32 pieces
        const fullBoardState = {
            // White pieces
            'a1': { type: 'r', color: 'white' },
            'b1': { type: 'n', color: 'white' },
            'c1': { type: 'b', color: 'white' },
            'd1': { type: 'q', color: 'white' },
            'e1': { type: 'k', color: 'white' },
            'f1': { type: 'b', color: 'white' },
            'g1': { type: 'n', color: 'white' },
            'h1': { type: 'r', color: 'white' },
            'a2': { type: 'p', color: 'white' },
            'b2': { type: 'p', color: 'white' },
            'c2': { type: 'p', color: 'white' },
            'd2': { type: 'p', color: 'white' },
            'e2': { type: 'p', color: 'white' },
            'f2': { type: 'p', color: 'white' },
            'g2': { type: 'p', color: 'white' },
            'h2': { type: 'p', color: 'white' },
            
            // Black pieces
            'a8': { type: 'r', color: 'black' },
            'b8': { type: 'n', color: 'black' },
            'c8': { type: 'b', color: 'black' },
            'd8': { type: 'q', color: 'black' },
            'e8': { type: 'k', color: 'black' },
            'f8': { type: 'b', color: 'black' },
            'g8': { type: 'n', color: 'black' },
            'h8': { type: 'r', color: 'black' },
            'a7': { type: 'p', color: 'black' },
            'b7': { type: 'p', color: 'black' },
            'c7': { type: 'p', color: 'black' },
            'd7': { type: 'p', color: 'black' },
            'e7': { type: 'p', color: 'black' },
            'f7': { type: 'p', color: 'black' },
            'g7': { type: 'p', color: 'black' },
            'h7': { type: 'p', color: 'black' }
        };
        
        // Update the board
        chessboard.updateBoard(fullBoardState);
        
        // Check no raw "black" or "white" text appears on any square
        for (const squareId in chessboard.squares) {
            const squareElement = chessboard.squares[squareId];
            const squareText = squareElement.textContent.trim().toLowerCase();
            
            expect(squareText).not.toContain('black');
            expect(squareText).not.toContain('white');
        }
    });
}); 