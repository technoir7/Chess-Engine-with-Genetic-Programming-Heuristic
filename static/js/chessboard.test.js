/**
 * Tests for chessboard.js
 */

describe('ChessBoard', () => {
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
    
    test('board should be created with 64 squares', () => {
        expect(Object.keys(chessboard.squares).length).toBe(64);
    });
    
    test('should place white pieces correctly', () => {
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
        
        // Verify each white piece is placed correctly
        for (const [square, piece] of Object.entries(whitePositions)) {
            const squareElement = chessboard.squares[square];
            
            // Check that piece exists
            expect(squareElement.querySelector('.piece')).not.toBeNull();
            
            // Check image src uses correct path
            const imgElement = squareElement.querySelector('.piece img');
            expect(imgElement).not.toBeNull();
            
            // Check image path uses uppercase for white pieces
            const upperPieceType = piece.type.toUpperCase();
            expect(imgElement.src).toContain(`/static/images/pieces/white-${piece.type}.svg`);
            
            // Check alt text
            expect(imgElement.alt).toBe(`${piece.color} ${piece.type}`);
        }
    });
    
    test('should place black pieces correctly', () => {
        const blackPositions = {
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
        
        // Update board with black pieces
        chessboard.updateBoard(blackPositions);
        
        // Verify each black piece is placed correctly
        for (const [square, piece] of Object.entries(blackPositions)) {
            const squareElement = chessboard.squares[square];
            
            // Check that piece exists
            expect(squareElement.querySelector('.piece')).not.toBeNull();
            
            // Check image src uses correct path
            const imgElement = squareElement.querySelector('.piece img');
            expect(imgElement).not.toBeNull();
            
            // Check image path
            expect(imgElement.src).toContain(`/static/images/pieces/black-${piece.type}.svg`);
            
            // Check alt text
            expect(imgElement.alt).toBe(`${piece.color} ${piece.type}`);
        }
    });
    
    test('should handle incorrect piece data', () => {
        // Mock console.error
        const originalConsoleError = console.error;
        const mockConsoleError = jest.fn();
        console.error = mockConsoleError;
        
        // Try to update board with invalid data
        chessboard.updateBoard({
            'a1': null,
            'b1': { type: null, color: 'white' },
            'c1': { type: 'b', color: null },
            'd1': { type: 'q', color: 'white' } // Only this one is valid
        });
        
        // Verify console.error was called for invalid pieces
        expect(mockConsoleError).toHaveBeenCalledTimes(3);
        
        // Verify valid piece was placed
        const squareElement = chessboard.squares['d1'];
        expect(squareElement.querySelector('.piece')).not.toBeNull();
        
        // Restore console.error
        console.error = originalConsoleError;
    });
    
    test('should update the entire board correctly', () => {
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
        
        // Count the number of pieces placed on the board
        const piecesOnBoard = document.querySelectorAll('.piece').length;
        expect(piecesOnBoard).toBe(32);
        
        // Verify white pieces count
        const whitePieces = document.querySelectorAll('.piece img[src*="white"]').length;
        expect(whitePieces).toBe(16);
        
        // Verify black pieces count
        const blackPieces = document.querySelectorAll('.piece img[src*="black"]').length;
        expect(blackPieces).toBe(16);
    });
}); 