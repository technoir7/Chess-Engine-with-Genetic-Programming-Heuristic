/**
 * Simple test suite for the ChessBoard component
 * 
 * Run this test by opening test.html in a browser
 */

// Mock DOM elements
document.body.innerHTML = `
  <div id="chessboard"></div>
  <div id="test-results"></div>
`;

// Test results container
const testResults = document.getElementById('test-results');

/**
 * Simple test runner
 */
function runTests() {
  const tests = [
    testBoardCreation,
    testPiecePlacement,
    testSquareSelection,
    testMoveHighlighting,
    testOrientationChange
  ];
  
  let passed = 0;
  let failed = 0;
  
  tests.forEach(test => {
    try {
      // Reset the board for each test
      document.getElementById('chessboard').innerHTML = '';
      
      // Run the test
      test();
      passed++;
      logResult(`✅ ${test.name} passed`);
    } catch (error) {
      failed++;
      logResult(`❌ ${test.name} failed: ${error.message}`);
      console.error(error);
    }
  });
  
  logResult(`\nTest Summary: ${passed} passed, ${failed} failed`);
}

/**
 * Log test results to the page
 */
function logResult(message) {
  const resultElement = document.createElement('div');
  resultElement.textContent = message;
  testResults.appendChild(resultElement);
}

/**
 * Assert that a condition is true
 */
function assert(condition, message) {
  if (!condition) {
    throw new Error(message || "Assertion failed");
  }
}

/**
 * Test that the chessboard is created correctly
 */
function testBoardCreation() {
  const chessboard = new ChessBoard();
  
  // Check that 64 squares were created
  const squares = document.querySelectorAll('.square');
  assert(squares.length === 64, "Should create 64 squares");
  
  // Check that there are alternating light and dark squares
  let lightSquares = document.querySelectorAll('.square.light');
  let darkSquares = document.querySelectorAll('.square.dark');
  assert(lightSquares.length === 32, "Should have 32 light squares");
  assert(darkSquares.length === 32, "Should have 32 dark squares");
  
  // Check that the squares have the correct IDs
  assert(document.getElementById('a1'), "Should have square a1");
  assert(document.getElementById('h8'), "Should have square h8");
}

/**
 * Test that pieces are placed correctly on the board
 */
function testPiecePlacement() {
  const chessboard = new ChessBoard();
  
  // Create a sample board state with a few pieces
  const sampleBoard = {
    'e4': { type: 'p', color: 'white' },
    'e5': { type: 'p', color: 'black' },
    'a1': { type: 'r', color: 'white' },
    'h8': { type: 'r', color: 'black' }
  };
  
  // Update the board with the sample state
  chessboard.updateBoard(sampleBoard);
  
  // Check that the pieces were placed
  const e4Square = document.getElementById('e4');
  const e5Square = document.getElementById('e5');
  const a1Square = document.getElementById('a1');
  const h8Square = document.getElementById('h8');
  
  assert(e4Square.querySelector('.piece img'), "E4 should have a piece");
  assert(e5Square.querySelector('.piece img'), "E5 should have a piece");
  assert(a1Square.querySelector('.piece img'), "A1 should have a piece");
  assert(h8Square.querySelector('.piece img'), "H8 should have a piece");
  
  // Check the image sources to verify correct pieces
  const e4Img = e4Square.querySelector('.piece img');
  const a1Img = a1Square.querySelector('.piece img');
  
  assert(e4Img.src.includes('white-pawn.svg'), "E4 should have a white pawn");
  assert(a1Img.src.includes('white-rook.svg'), "A1 should have a white rook");
}

/**
 * Test square selection
 */
function testSquareSelection() {
  const chessboard = new ChessBoard();
  
  // Create a sample board state with a piece
  const sampleBoard = {
    'e2': { type: 'p', color: 'white' }
  };
  
  // Update the board with the sample state
  chessboard.updateBoard(sampleBoard);
  
  // Select the e2 square
  chessboard.selectSquare('e2');
  
  // Check that the square is selected
  const e2Square = document.getElementById('e2');
  assert(e2Square.classList.contains('selected'), "E2 should be selected");
  
  // Deselect the square
  chessboard.deselectSquare();
  
  // Check that the square is no longer selected
  assert(!e2Square.classList.contains('selected'), "E2 should no longer be selected");
}

/**
 * Test move highlighting
 */
function testMoveHighlighting() {
  const chessboard = new ChessBoard();
  
  // Create a sample board state with a piece
  const sampleBoard = {
    'e2': { type: 'p', color: 'white' }
  };
  
  // Create sample legal moves
  const legalMoves = [
    { from: 'e2', to: 'e3' },
    { from: 'e2', to: 'e4' }
  ];
  
  // Update the board with the sample state and legal moves
  chessboard.updateBoard(sampleBoard, legalMoves);
  
  // Select the e2 square to trigger highlighting
  chessboard.selectSquare('e2');
  
  // Check that the legal move squares are highlighted
  const e3Square = document.getElementById('e3');
  const e4Square = document.getElementById('e4');
  
  assert(e3Square.classList.contains('highlight'), "E3 should be highlighted");
  assert(e4Square.classList.contains('highlight'), "E4 should be highlighted");
}

/**
 * Test board orientation change
 */
function testOrientationChange() {
  const chessboard = new ChessBoard();
  
  // Check default orientation
  assert(chessboard.orientation === 'white', "Default orientation should be white");
  
  // Change orientation to black
  chessboard.setOrientation('black');
  
  // Check that orientation was changed
  assert(chessboard.orientation === 'black', "Orientation should be changed to black");
  assert(
    document.getElementById('chessboard').style.transform === 'rotate(180deg)',
    "Board should be rotated 180 degrees"
  );
  
  // Change orientation back to white
  chessboard.setOrientation('white');
  
  // Check that orientation was changed back
  assert(chessboard.orientation === 'white', "Orientation should be changed back to white");
  assert(
    document.getElementById('chessboard').style.transform === 'none',
    "Board should have no rotation"
  );
}

// Run the tests when the script is loaded
window.addEventListener('load', runTests); 