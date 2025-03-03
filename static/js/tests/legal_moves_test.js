/**
 * Legal Moves Test - Specifically tests the functionality of legal move detection
 * and highlighting in the chess board UI.
 */

console.log('Legal Moves Test loaded');

// Store test results
const testResults = {
    passCount: 0,
    failCount: 0,
    logs: []
};

// Helper function to log test results
function logTest(message, status, details = '') {
    const result = {
        message,
        status, // 'pass', 'fail', or 'info'
        details,
        timestamp: new Date().toISOString()
    };
    
    testResults.logs.push(result);
    
    if (status === 'pass') {
        testResults.passCount++;
        console.log(`✅ PASS: ${message}`);
        if (details) console.log(`   ${details}`);
    } else if (status === 'fail') {
        testResults.failCount++;
        console.error(`❌ FAIL: ${message}`);
        if (details) console.error(`   ${details}`);
    } else {
        console.log(`ℹ️ INFO: ${message}`);
        if (details) console.log(`   ${details}`);
    }
}

// Helper function to inspect an object for debugging
function inspectObject(obj) {
    return JSON.stringify(obj, null, 2);
}

// Define the test functions
const legalMovesTests = {
    /**
     * Test 1: Check that default legal moves are added in the constructor
     */
    testDefaultLegalMovesAdded() {
        logTest('Testing if default legal moves are added during initialization', 'info');
        
        const chessboard = window.chessboard;
        
        // Check if the legal moves array has any items
        if (!chessboard.legalMoves || chessboard.legalMoves.length === 0) {
            logTest('No legal moves found in the chessboard object', 'fail',
                    'Expected legal moves to be populated, but found empty array');
            return false;
        }
        
        // Check for specific expected moves
        const e2e4Move = chessboard.legalMoves.find(move => move.from === 'e2' && move.to === 'e4');
        if (!e2e4Move) {
            logTest('e2-e4 move not found in legal moves', 'fail',
                    `Legal moves: ${inspectObject(chessboard.legalMoves)}`);
            return false;
        }
        
        logTest('Default legal moves are correctly added', 'pass',
                `Found ${chessboard.legalMoves.length} legal moves including e2-e4`);
        return true;
    },
    
    /**
     * Test 2: Test the isLegalMove function directly
     */
    testIsLegalMoveFunction() {
        logTest('Testing the isLegalMove function', 'info');
        
        const chessboard = window.chessboard;
        
        // Test a standard pawn move
        const isPawnMoveToE4Legal = chessboard.isLegalMove('e2', 'e4');
        if (!isPawnMoveToE4Legal) {
            logTest('e2-e4 should be a legal move but isLegalMove returned false', 'fail');
            return false;
        }
        
        // Test an invalid move
        const isInvalidMoveToE5Legal = chessboard.isLegalMove('e2', 'e5');
        if (isInvalidMoveToE5Legal) {
            logTest('e2-e5 should not be a legal move but isLegalMove returned true', 'fail');
            return false;
        }
        
        // Test another valid move - knight move
        const isKnightMoveLegal = chessboard.isLegalMove('g1', 'f3');
        if (!isKnightMoveLegal) {
            logTest('g1-f3 should be a legal knight move but isLegalMove returned false', 'fail');
            return false;
        }
        
        logTest('isLegalMove function is working correctly', 'pass',
                'Correctly identified legal and illegal moves');
        return true;
    },
    
    /**
     * Test 3: Test highlighting of legal moves when a piece is selected
     */
    testLegalMoveHighlighting() {
        logTest('Testing highlighting of legal moves when a piece is selected', 'info');
        
        const chessboard = window.chessboard;
        
        // Clear any existing selection
        chessboard.deselectSquare();
        
        // Manually select the e2 pawn
        chessboard.selectSquare('e2');
        
        // Check if the e4 square has the highlight class
        const e4Square = document.getElementById('e4');
        if (!e4Square.classList.contains('highlight')) {
            logTest('e4 square should be highlighted as a legal move but is not', 'fail',
                    `e4 square classes: ${e4Square.className}`);
            return false;
        }
        
        // Check if the e3 square has the highlight class (one step forward)
        const e3Square = document.getElementById('e3');
        if (!e3Square.classList.contains('highlight')) {
            logTest('e3 square should be highlighted as a legal move but is not', 'fail',
                    `e3 square classes: ${e3Square.className}`);
            return false;
        }
        
        logTest('Legal moves are correctly highlighted when a piece is selected', 'pass',
                'Found highlight classes on e3 and e4 squares');
        
        // Clean up
        chessboard.deselectSquare();
        return true;
    },
    
    /**
     * Test 4: Test piece movement through simulated clicks
     */
    testPieceMovement() {
        logTest('Testing piece movement through simulated clicks', 'info');
        
        const chessboard = window.chessboard;
        
        // Store the original fetch function
        const originalFetch = window.fetch;
        
        // Create a mock fetch function
        window.fetch = function(url, options) {
            logTest(`Mock fetch called with url: ${url}`, 'info');
            
            // Create a response for the move
            const responseData = {
                valid: true,
                board: {
                    // Include a simplified board state with the moved piece
                    'e4': { type: 'p', color: 'white', code: 'P' }
                },
                legalMoves: []
            };
            
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve(responseData)
            });
        };
        
        // Set up a custom event listener for checkGameActive
        const originalAddEventListener = document.addEventListener;
        document.addEventListener = function(event, handler) {
            if (event === 'checkGameActive') {
                // Immediately call the callback
                setTimeout(() => {
                    handler.detail.callback(true, 'white');
                }, 0);
            } else {
                // Use the original for other events
                originalAddEventListener.call(document, event, handler);
            }
        };
        
        try {
            // Clear any existing selection
            chessboard.deselectSquare();
            
            // Get the e2 square and click it
            const e2Square = document.getElementById('e2');
            e2Square.click();
            
            // Check if e2 is selected
            if (chessboard.selectedSquare !== 'e2') {
                logTest('e2 square should be selected after clicking it', 'fail');
                return false;
            }
            
            logTest('Successfully selected the e2 pawn', 'pass');
            
            // Now click on e4 to move there
            const e4Square = document.getElementById('e4');
            e4Square.click();
            
            // Set a timeout to check the result after the async move completes
            setTimeout(() => {
                try {
                    // Check if the piece is now at e4 in the UI
                    const pieceAtE4 = e4Square.querySelector('.piece');
                    
                    if (!pieceAtE4) {
                        logTest('No piece found at e4 after attempted move', 'fail');
                    } else {
                        // Check if it's a white pawn
                        const imgAtE4 = pieceAtE4.querySelector('img');
                        if (imgAtE4 && imgAtE4.src.includes('white-pawn')) {
                            logTest('Successfully moved pawn from e2 to e4', 'pass');
                        } else {
                            logTest('Piece at e4 is not a white pawn', 'fail',
                                    `Found: ${imgAtE4 ? imgAtE4.src : 'no image'}`);
                        }
                    }
                    
                    // Restore original functions
                    window.fetch = originalFetch;
                    document.addEventListener = originalAddEventListener;
                    
                    // Print final results
                    printTestSummary();
                } catch (error) {
                    logTest('Error checking move result', 'fail', error.toString());
                    
                    // Restore original functions even if there's an error
                    window.fetch = originalFetch;
                    document.addEventListener = originalAddEventListener;
                }
            }, 50);
            
            return true;
        } catch (error) {
            logTest('Error during piece movement test', 'fail', error.toString());
            
            // Restore original functions
            window.fetch = originalFetch;
            document.addEventListener = originalAddEventListener;
            return false;
        }
    },
    
    /**
     * Test 5: Test internal representation of board state after move
     */
    testBoardStateAfterMove() {
        logTest('Testing internal board state after move', 'info');
        
        const chessboard = window.chessboard;
        
        // Make a direct move using makeMove
        const originalPiece = chessboard.boardState['e2'];
        
        // We'll use updateBoardUI to simulate a move without API calls
        const newBoardState = {...chessboard.boardState};
        
        // Only proceed if e2 has a piece
        if (!originalPiece) {
            logTest('No piece found at e2 in the board state', 'fail');
            return false;
        }
        
        // Move the piece in our temp state
        newBoardState['e4'] = newBoardState['e2'];
        delete newBoardState['e2'];
        
        // Update the UI
        chessboard.updateBoardUI(newBoardState);
        
        // Check if the piece visually moved
        const e4Square = document.getElementById('e4');
        const pieceAtE4 = e4Square.querySelector('.piece');
        
        if (!pieceAtE4) {
            logTest('No piece found at e4 after updateBoardUI', 'fail');
            return false;
        }
        
        // Check the image
        const imgAtE4 = pieceAtE4.querySelector('img');
        if (!imgAtE4 || !imgAtE4.src.includes('white-pawn')) {
            logTest('Image at e4 is not a white pawn', 'fail',
                    `Found: ${imgAtE4 ? imgAtE4.src : 'no image'}`);
            return false;
        }
        
        logTest('Board state successfully updated with piece moved from e2 to e4', 'pass');
        return true;
    }
};

// Function to run all tests
function runLegalMovesTests() {
    logTest('Starting legal moves tests...', 'info');
    
    // Reset the chessboard
    resetChessboard();
    
    // Run the tests
    legalMovesTests.testDefaultLegalMovesAdded();
    legalMovesTests.testIsLegalMoveFunction();
    legalMovesTests.testLegalMoveHighlighting();
    legalMovesTests.testBoardStateAfterMove();
    
    // Run the movement test last as it's async
    legalMovesTests.testPieceMovement();
}

// Reset chessboard to initial state
function resetChessboard() {
    const chessboard = window.chessboard;
    
    // Set up initial board state with legal moves for testing
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
    
    // Make sure chessboard is initialized before updating
    if (chessboard) {
        chessboard.updateBoard(initialBoardState);
    }
}

// Print test summary
function printTestSummary() {
    const total = testResults.passCount + testResults.failCount;
    console.log('');
    console.log('=== TEST SUMMARY ===');
    console.log(`Total tests: ${total}`);
    console.log(`Passed: ${testResults.passCount}`);
    console.log(`Failed: ${testResults.failCount}`);
    
    if (testResults.failCount === 0) {
        console.log('✅ ALL TESTS PASSED');
    } else {
        console.error(`❌ ${testResults.failCount} TESTS FAILED`);
    }
}

// Make functions available in the global scope
window.runLegalMovesTests = runLegalMovesTests;
window.resetChessboard = resetChessboard; 