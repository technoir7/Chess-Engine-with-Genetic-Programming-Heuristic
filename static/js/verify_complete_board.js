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

    const boardState = window.__currentBoardState || {};
    const expectedSquares = Object.keys(boardState);
    let missingPieces = [];
    let presentPieces = [];

    const pieceName = (type) => {
        if (type === 'n') return 'knight';
        if (type === 'r') return 'rook';
        if (type === 'b') return 'bishop';
        if (type === 'q') return 'queen';
        if (type === 'k') return 'king';
        return 'pawn';
    };

    const getSquareImage = (squareId) => {
        const square = document.getElementById(squareId);
        return square ? square.querySelector('img') : null;
    };

    if (expectedSquares.length === 0) {
        console.error('No board state available for verification');
        missingPieces.push('Current board state unavailable');
    }

    for (const squareId of expectedSquares) {
        const expectedPiece = boardState[squareId];
        const img = getSquareImage(squareId);
        const expectedImage = `/${expectedPiece.color}-${pieceName(expectedPiece.type)}.svg`;

        if (!img) {
            missingPieces.push(`${expectedPiece.color} ${expectedPiece.type} at ${squareId}`);
            continue;
        }

        if (img.src.includes(expectedImage)) {
            presentPieces.push(`${expectedPiece.color} ${expectedPiece.type} at ${squareId}`);
        } else {
            missingPieces.push(`${expectedPiece.color} ${expectedPiece.type} at ${squareId} (rendered as ${img.src.split('/').pop()})`);
        }
    }

    const renderedSquares = Array.from(document.querySelectorAll('#chessboard .square'))
        .filter(square => square.querySelector('img'))
        .map(square => square.id);

    const unexpectedSquares = renderedSquares.filter(squareId => !(squareId in boardState));
    unexpectedSquares.forEach(squareId => {
        missingPieces.push(`unexpected rendered piece at ${squareId}`);
    });
    
    // Report results
    console.log(`Board verification: ${presentPieces.length} pieces present, ${missingPieces.length} issues found`);
    
    if (missingPieces.length > 0) {
        console.error('MISSING PIECES:');
        missingPieces.forEach(piece => console.error(`- ${piece}`));
    } else {
        console.log(`SUCCESS! All ${presentPieces.length} rendered pieces match the current board state.`);
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
        notification.innerHTML = `<strong>Board Verification Failed</strong><br>Found ${missingPieces.length} mismatches.<br>Check console for details.`;
    } else {
        notification.innerHTML = `<strong>Board Verification Successful</strong><br>All ${presentPieces.length} pieces match state.`;
    }
    
    document.body.appendChild(notification);
    
    // Remove notification after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
    
    return missingPieces.length === 0;
} 
