/**
 * Board Verification Script
 * This script verifies that all 32 chess pieces are present on the board initialization
 * It will report any missing pieces in the console
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add a button to trigger the verification
    const verifyButton = document.createElement('button');
    verifyButton.textContent = 'Verify Complete Board';
    verifyButton.style.position = 'fixed';
    verifyButton.style.bottom = '10px';
    verifyButton.style.right = '10px';
    verifyButton.style.zIndex = '1000';
    verifyButton.className = 'button';
    document.body.appendChild(verifyButton);
    
    verifyButton.addEventListener('click', verifyCompleteBoard);
    
    // Also verify when game initializes
    document.addEventListener('gameInitialized', verifyCompleteBoard);
});

function verifyCompleteBoard() {
    console.log('Verifying board completeness...');
    
    // Critical pieces that should be on a complete board
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
    
    // Check each square on the board
    let missingPieces = [];
    let presentPieces = [];
    
    // Function to check if a DOM element has a piece image
    const hasPieceImage = (square) => {
        return square && 
               square.querySelector('img') !== null && 
               square.querySelector('img').src.includes('/pieces/');
    };
    
    // Check each critical square
    for (const squareId in criticalPieces) {
        const square = document.getElementById(squareId);
        if (!square) {
            console.error(`Square ${squareId} not found in DOM`);
            continue;
        }
        
        const expectedPiece = criticalPieces[squareId];
        
        // Check if the square has a piece
        if (hasPieceImage(square)) {
            const img = square.querySelector('img');
            const imgSrc = img.src;
            
            // Verify it's the right piece type and color
            const correctType = imgSrc.includes(`/${expectedPiece.color}-${expectedPiece.type === 'n' ? 'knight' : 
                                                expectedPiece.type === 'r' ? 'rook' : 
                                                expectedPiece.type === 'b' ? 'bishop' : 
                                                expectedPiece.type === 'q' ? 'queen' : 
                                                expectedPiece.type === 'k' ? 'king' : 'pawn'}.svg`);
            
            if (correctType) {
                presentPieces.push(`${expectedPiece.color} ${expectedPiece.type} at ${squareId}`);
            } else {
                missingPieces.push(`${expectedPiece.color} ${expectedPiece.type} at ${squareId} (wrong piece type/color)`);
            }
        } else {
            missingPieces.push(`${expectedPiece.color} ${expectedPiece.type} at ${squareId}`);
        }
    }
    
    // Report results
    console.log(`Board verification: ${presentPieces.length} pieces present, ${missingPieces.length} pieces missing`);
    
    if (missingPieces.length > 0) {
        console.error('MISSING PIECES:');
        missingPieces.forEach(piece => console.error(`- ${piece}`));
    } else {
        console.log('SUCCESS! All 32 pieces are present and correctly positioned.');
    }
    
    // Create a notification on the page
    const notification = document.createElement('div');
    notification.style.position = 'fixed';
    notification.style.top = '10px';
    notification.style.right = '10px';
    notification.style.padding = '10px';
    notification.style.backgroundColor = missingPieces.length > 0 ? '#ffcccc' : '#ccffcc';
    notification.style.border = '1px solid ' + (missingPieces.length > 0 ? '#ff0000' : '#00ff00');
    notification.style.borderRadius = '5px';
    notification.style.zIndex = '1000';
    notification.style.maxWidth = '300px';
    
    if (missingPieces.length > 0) {
        notification.innerHTML = `<strong>Board Verification Failed</strong><br>Missing ${missingPieces.length} pieces.<br>Check console for details.`;
    } else {
        notification.innerHTML = `<strong>Board Verification Successful</strong><br>All 32 pieces present.`;
    }
    
    document.body.appendChild(notification);
    
    // Remove notification after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
    
    return missingPieces.length === 0;
} 