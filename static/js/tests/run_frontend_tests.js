/**
 * Frontend test script to verify rendering fixes and piece movement
 * Run this in the browser console to test the chessboard rendering and movement
 */

function runFrontendTests() {
    console.log('Running frontend tests for chessboard rendering and movement...');
    
    // Test 1: Verify all 32 pieces are present
    const test1 = function() {
        console.log('Test 1: Checking for all 32 pieces...');
        
        const pieces = document.querySelectorAll('.piece');
        const whitePieces = document.querySelectorAll('.piece img[src*="white"]');
        const blackPieces = document.querySelectorAll('.piece img[src*="black"]');
        
        console.log(`- Found ${pieces.length} pieces (${whitePieces.length} white, ${blackPieces.length} black)`);
        
        if (pieces.length !== 32) {
            console.error('❌ FAIL: Expected 32 pieces, found ' + pieces.length);
        } else {
            console.log('✅ PASS: Found 32 pieces total');
        }
        
        if (whitePieces.length !== 16) {
            console.error('❌ FAIL: Expected 16 white pieces, found ' + whitePieces.length);
        } else {
            console.log('✅ PASS: Found 16 white pieces');
        }
        
        if (blackPieces.length !== 16) {
            console.error('❌ FAIL: Expected 16 black pieces, found ' + blackPieces.length);
        } else {
            console.log('✅ PASS: Found 16 black pieces');
        }
    };
    
    // Test 2: Verify specific issue pieces are present (black rook at a8, black pawn at h7)
    const test2 = function() {
        console.log('Test 2: Checking for black rook at a8 and black pawn at h7...');
        
        const a8Square = document.getElementById('a8');
        const h7Square = document.getElementById('h7');
        
        if (!a8Square) {
            console.error('❌ FAIL: Square a8 not found');
            return;
        }
        
        if (!h7Square) {
            console.error('❌ FAIL: Square h7 not found');
            return;
        }
        
        const a8Piece = a8Square.querySelector('.piece img');
        const h7Piece = h7Square.querySelector('.piece img');
        
        if (!a8Piece) {
            console.error('❌ FAIL: No piece found on a8');
        } else if (!a8Piece.src.includes('black-rook')) {
            console.error(`❌ FAIL: Expected black rook on a8, found ${a8Piece.src}`);
        } else {
            console.log('✅ PASS: Black rook found on a8');
        }
        
        if (!h7Piece) {
            console.error('❌ FAIL: No piece found on h7');
        } else if (!h7Piece.src.includes('black-pawn')) {
            console.error(`❌ FAIL: Expected black pawn on h7, found ${h7Piece.src}`);
        } else {
            console.log('✅ PASS: Black pawn found on h7');
        }
    };
    
    // Test 3: Check for raw text on the board
    const test3 = function() {
        console.log('Test 3: Checking for raw "black" or "white" text on the board...');
        
        let hasRawText = false;
        
        // Check all squares for raw text
        for (let row = 1; row <= 8; row++) {
            for (let col = 0; col < 8; col++) {
                const file = String.fromCharCode(97 + col); // 'a' through 'h'
                const square = document.getElementById(`${file}${row}`);
                
                if (!square) {
                    console.error(`❌ FAIL: Square ${file}${row} not found`);
                    continue;
                }
                
                const squareText = square.textContent.trim().toLowerCase();
                
                if (squareText.includes('black') || squareText.includes('white')) {
                    console.error(`❌ FAIL: Raw text found on square ${file}${row}: "${squareText}"`);
                    hasRawText = true;
                }
            }
        }
        
        if (!hasRawText) {
            console.log('✅ PASS: No raw "black" or "white" text found on the board');
        }
    };
    
    // Test 4: Test piece selection functionality
    const test4 = function() {
        console.log('Test 4: Testing piece selection functionality...');
        
        try {
            // Check if the game is ready and has the chessboard
            const chessboard = window.chessboard;
            if (!chessboard) {
                console.error('❌ FAIL: ChessBoard instance not found on window');
                return;
            }
            
            // Clear any existing selection
            chessboard.deselectSquare();
            
            // Try to click on a white piece (e2 pawn)
            const e2Square = document.getElementById('e2');
            if (!e2Square) {
                console.error('❌ FAIL: Square e2 not found');
                return;
            }
            
            // Set up a game state event handler temporarily
            const originalEventListener = document.addEventListener;
            document.addEventListener = function(event, handler) {
                if (event === 'checkGameActive') {
                    // Immediately call the callback with active game and white's turn
                    handler.detail.callback(true, 'white');
                } else {
                    // Call the original addEventListener for other events
                    originalEventListener.call(document, event, handler);
                }
            };
            
            // Simulate click
            e2Square.click();
            
            // Restore original event listener
            document.addEventListener = originalEventListener;
            
            // Check if the piece was selected
            if (chessboard.selectedSquare !== 'e2') {
                console.error('❌ FAIL: Piece at e2 was not selected when clicked');
            } else if (!e2Square.classList.contains('selected')) {
                console.error('❌ FAIL: Square e2 does not have the "selected" class');
            } else {
                console.log('✅ PASS: Piece selection works correctly');
            }
            
            // Clean up
            chessboard.deselectSquare();
        } catch (error) {
            console.error('❌ FAIL: Error during piece selection test:', error);
        }
    };
    
    // Test 5: Test move highlighting
    const test5 = function() {
        console.log('Test 5: Testing move highlighting...');
        
        try {
            // Get the chessboard instance
            const chessboard = window.chessboard;
            if (!chessboard) {
                console.error('❌ FAIL: ChessBoard instance not found on window');
                return;
            }
            
            // Add a legal move from e2 to e4
            chessboard.legalMoves = [
                { from: 'e2', to: 'e3' },
                { from: 'e2', to: 'e4' }
            ];
            
            // Clear any existing selection
            chessboard.deselectSquare();
            
            // Set up a game state event handler temporarily
            const originalEventListener = document.addEventListener;
            document.addEventListener = function(event, handler) {
                if (event === 'checkGameActive') {
                    // Immediately call the callback with active game and white's turn
                    handler.detail.callback(true, 'white');
                } else {
                    // Call the original addEventListener for other events
                    originalEventListener.call(document, event, handler);
                }
            };
            
            // Select the e2 pawn
            const e2Square = document.getElementById('e2');
            e2Square.click();
            
            // Restore original event listener
            document.addEventListener = originalEventListener;
            
            // Check if the legal moves are highlighted
            const e3Square = document.getElementById('e3');
            const e4Square = document.getElementById('e4');
            
            if (!e3Square.classList.contains('highlight')) {
                console.error('❌ FAIL: Legal move to e3 is not highlighted');
            } else if (!e4Square.classList.contains('highlight')) {
                console.error('❌ FAIL: Legal move to e4 is not highlighted');
            } else {
                console.log('✅ PASS: Legal move highlighting works correctly');
            }
            
            // Clean up
            chessboard.deselectSquare();
        } catch (error) {
            console.error('❌ FAIL: Error during move highlighting test:', error);
        }
    };
    
    // Run all tests
    test1();
    console.log('------------');
    test2();
    console.log('------------');
    test3();
    console.log('------------');
    test4();
    console.log('------------');
    test5();
    
    console.log('Frontend tests completed!');
}

// Export for use in browser
if (typeof window !== 'undefined') {
    window.runFrontendTests = runFrontendTests;
    console.log('Frontend test script loaded. Run tests with window.runFrontendTests()');
}

// Export for testing frameworks
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { runFrontendTests };
} 