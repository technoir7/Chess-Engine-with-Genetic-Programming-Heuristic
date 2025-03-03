/**
 * Script to run piece movement tests in the browser
 */

function runPieceMovementTests() {
    console.log('Running chess piece movement tests...');
    
    // Test 1: Verify piece selection works
    const test1 = function() {
        console.log('Test 1: Testing piece selection...');
        
        try {
            // Clear any existing selection
            const chessboard = window.chessboard;
            chessboard.deselectSquare();
            
            // Click on the e2 pawn
            const e2Square = chessboard.squares['e2'];
            e2Square.click();
            
            // Check if the square is selected
            if (chessboard.selectedSquare !== 'e2') {
                console.error('❌ FAIL: Piece at e2 was not selected when clicked');
                return false;
            }
            
            if (!e2Square.classList.contains('selected')) {
                console.error('❌ FAIL: Square e2 does not have the "selected" class');
                return false;
            }
            
            // Check if legal moves are highlighted
            const e3Square = chessboard.squares['e3'];
            const e4Square = chessboard.squares['e4'];
            
            if (!e3Square.classList.contains('highlight') || !e4Square.classList.contains('highlight')) {
                console.error('❌ FAIL: Legal moves are not highlighted properly');
                return false;
            }
            
            console.log('✅ PASS: Piece selection working correctly');
            return true;
        } catch (error) {
            console.error('❌ FAIL: Error during piece selection test:', error);
            return false;
        }
    };
    
    // Test 2: Verify piece movement
    const test2 = function() {
        console.log('Test 2: Testing piece movement...');
        
        try {
            // Mock the fetch API for testing
            const originalFetch = window.fetch;
            
            // Create a success response for a move from e2 to e4
            const mockResponse = {
                valid: true,
                board: {
                    // Simplified board state with just the moved pawn
                    'e4': { type: 'p', color: 'white', code: 'P' }
                },
                legalMoves: [],
                currentPlayer: 'black'
            };
            
            // Replace fetch with a mock
            window.fetch = function(url, options) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(mockResponse)
                });
            };
            
            // Get reference to chessboard
            const chessboard = window.chessboard;
            
            // Clear any existing selection
            chessboard.deselectSquare();
            
            // Click on the e2 pawn to select it
            const e2Square = chessboard.squares['e2'];
            e2Square.click();
            
            // Click on e4 to move there
            const e4Square = chessboard.squares['e4'];
            e4Square.click();
            
            // Wait a bit for the async operations to complete
            setTimeout(() => {
                try {
                    // Check if the piece is now at e4
                    const pieceAtE4 = e4Square.querySelector('.piece');
                    
                    if (!pieceAtE4) {
                        console.error('❌ FAIL: No piece found at e4 after movement');
                    } else {
                        // Verify it's a white pawn
                        const imgElement = pieceAtE4.querySelector('img');
                        if (!imgElement || !imgElement.src.includes('white-p')) {
                            console.error('❌ FAIL: Wrong piece found at e4 after movement');
                        } else {
                            console.log('✅ PASS: Piece movement is working correctly');
                        }
                    }
                    
                    // Restore original fetch
                    window.fetch = originalFetch;
                } catch (error) {
                    console.error('❌ FAIL: Error checking piece movement result:', error);
                    // Restore original fetch
                    window.fetch = originalFetch;
                }
            }, 100);
            
            return true;
        } catch (error) {
            console.error('❌ FAIL: Error during piece movement test:', error);
            return false;
        }
    };
    
    // Test 3: Verify piece deselection
    const test3 = function() {
        console.log('Test 3: Testing piece deselection...');
        
        try {
            // Get reference to chessboard
            const chessboard = window.chessboard;
            
            // Clear any existing selection
            chessboard.deselectSquare();
            
            // Click on the e2 pawn to select it
            const e2Square = chessboard.squares['e2'];
            e2Square.click();
            
            // Verify it's selected
            if (chessboard.selectedSquare !== 'e2') {
                console.error('❌ FAIL: Piece at e2 was not selected');
                return false;
            }
            
            // Click on an empty square (e3) to deselect
            const e3Square = chessboard.squares['e3'];
            e3Square.click();
            
            // Verify nothing is selected
            if (chessboard.selectedSquare !== null) {
                console.error('❌ FAIL: Piece was not deselected');
                return false;
            }
            
            console.log('✅ PASS: Piece deselection working correctly');
            return true;
        } catch (error) {
            console.error('❌ FAIL: Error during piece deselection test:', error);
            return false;
        }
    };
    
    // Test 4: Verify changing selection between pieces
    const test4 = function() {
        console.log('Test 4: Testing changing selection between pieces...');
        
        try {
            // Get reference to chessboard
            const chessboard = window.chessboard;
            
            // Clear any existing selection
            chessboard.deselectSquare();
            
            // Click on the e2 pawn to select it
            const e2Square = chessboard.squares['e2'];
            e2Square.click();
            
            // Click on the d2 pawn to change selection
            const d2Square = chessboard.squares['d2'];
            d2Square.click();
            
            // Verify d2 is now selected instead of e2
            if (chessboard.selectedSquare !== 'd2') {
                console.error('❌ FAIL: Selection did not change to d2');
                return false;
            }
            
            if (e2Square.classList.contains('selected')) {
                console.error('❌ FAIL: e2 is still showing as selected');
                return false;
            }
            
            if (!d2Square.classList.contains('selected')) {
                console.error('❌ FAIL: d2 is not showing as selected');
                return false;
            }
            
            console.log('✅ PASS: Changing selection between pieces works correctly');
            return true;
        } catch (error) {
            console.error('❌ FAIL: Error during changing selection test:', error);
            return false;
        }
    };
    
    // Run all tests
    const test1Result = test1();
    console.log('------------');
    
    // Only continue if test1 passes
    if (test1Result) {
        const test3Result = test3();
        console.log('------------');
        
        const test4Result = test4();
        console.log('------------');
        
        // Run the movement test last as it modifies the board
        test2();
    }
    
    console.log('Movement tests completed!');
}

// Make the function available globally
if (typeof window !== 'undefined') {
    window.runPieceMovementTests = runPieceMovementTests;
    console.log('Piece movement test script loaded. Run tests with window.runPieceMovementTests()');
}

// Export for testing frameworks
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { runPieceMovementTests };
} 