/**
 * Frontend test script to verify rendering fixes
 * Run this in the browser console to test the chessboard rendering
 */

function runFrontendTests() {
    console.log('Running frontend tests for chessboard rendering...');
    
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
    
    // Run all tests
    test1();
    test2();
    test3();
    
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