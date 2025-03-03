/**
 * Test Runner for Chess Engine
 * Runs all tests and reports results
 */

// Define the tests to run
const TestSuite = {
    // Track results
    results: {
        total: 0,
        passed: 0,
        failed: 0
    },
    
    // Store test cases
    testCases: {},
    
    /**
     * Register a test case
     * @param {string} name - Test name
     * @param {Function} testFn - Test function
     */
    registerTest(name, testFn) {
        this.testCases[name] = testFn;
        console.log(`Registered test: ${name}`);
    },
    
    /**
     * Assert that a condition is true
     * @param {boolean} condition - The condition to test
     * @param {string} message - Description of the test
     * @returns {boolean} - Whether the assertion passed
     */
    assert(condition, message) {
        this.results.total++;
        
        if (condition) {
            this.results.passed++;
            console.log(`✅ PASS: ${message}`);
            return true;
        } else {
            this.results.failed++;
            console.error(`❌ FAIL: ${message}`);
            return false;
        }
    },
    
    /**
     * Run all registered tests
     */
    async runAll() {
        console.log('=== STARTING TEST SUITE ===');
        
        // Reset results
        this.results = {
            total: 0,
            passed: 0, 
            failed: 0
        };
        
        // Run each test
        for (const [name, testFn] of Object.entries(this.testCases)) {
            console.log(`\n▶️ Running test: ${name}`);
            
            try {
                const result = testFn.call(this);
                
                // Handle async tests
                if (result instanceof Promise) {
                    await result;
                }
            } catch (error) {
                console.error(`❌ Test "${name}" failed with error:`, error);
                this.results.failed++;
            }
        }
        
        // Print summary
        this.printSummary();
    },
    
    /**
     * Print test results summary
     */
    printSummary() {
        console.log('\n=== TEST SUMMARY ===');
        console.log(`Total tests: ${this.results.total}`);
        console.log(`Passed: ${this.results.passed}`);
        console.log(`Failed: ${this.results.failed}`);
        
        if (this.results.failed === 0) {
            console.log('✅ ALL TESTS PASSED');
        } else {
            console.error(`❌ ${this.results.failed} TESTS FAILED`);
        }
    }
};

// ===== Chessboard Tests =====

// Test legal move detection
TestSuite.registerTest('Legal Move Detection', function() {
    const chessboard = window.chessboard;
    
    // Ensure chessboard exists
    if (!this.assert(chessboard, 'Chessboard should exist')) {
        return;
    }
    
    // Test that legal moves are initialized
    this.assert(
        chessboard.legalMoves && chessboard.legalMoves.length > 0,
        'Legal moves should be initialized'
    );
    
    // Test e2-e4 is a legal move
    const e2e4Move = chessboard.legalMoves.find(move => 
        move.from === 'e2' && move.to === 'e4'
    );
    this.assert(e2e4Move, 'e2-e4 should be in the legal moves list');
    
    // Test the isLegalMove function
    this.assert(
        chessboard.isLegalMove('e2', 'e4'),
        'isLegalMove should return true for e2-e4'
    );
    
    this.assert(
        !chessboard.isLegalMove('e2', 'e5'),
        'isLegalMove should return false for e2-e5'
    );
    
    this.assert(
        chessboard.isLegalMove('g1', 'f3'),
        'isLegalMove should return true for knight move g1-f3'
    );
});

// Test piece selection and highlighting
TestSuite.registerTest('Piece Selection and Highlighting', function() {
    const chessboard = window.chessboard;
    
    // Ensure chessboard exists
    if (!this.assert(chessboard, 'Chessboard should exist')) {
        return;
    }
    
    // Clear any existing selection
    chessboard.deselectSquare();
    
    // Select e2 pawn
    chessboard.selectSquare('e2');
    this.assert(
        chessboard.selectedSquare === 'e2',
        'Selecting e2 should set selectedSquare property'
    );
    
    // Check if e2 has selected class
    const e2Square = document.getElementById('e2');
    this.assert(
        e2Square.classList.contains('selected'),
        'Selected square should have "selected" class'
    );
    
    // Check if legal moves are highlighted
    const e4Square = document.getElementById('e4');
    this.assert(
        e4Square.classList.contains('highlight'),
        'Legal moves should be highlighted (e4)'
    );
    
    const e3Square = document.getElementById('e3');
    this.assert(
        e3Square.classList.contains('highlight'),
        'Legal moves should be highlighted (e3)'
    );
    
    // Deselect and verify highlights are removed
    chessboard.deselectSquare();
    this.assert(
        !e2Square.classList.contains('selected'),
        'Deselected square should not have "selected" class'
    );
    
    this.assert(
        !e4Square.classList.contains('highlight'),
        'Highlights should be removed after deselection'
    );
});

// Test piece movement
TestSuite.registerTest('Piece Movement', function() {
    const chessboard = window.chessboard;
    
    // Ensure chessboard exists
    if (!this.assert(chessboard, 'Chessboard should exist')) {
        return;
    }
    
    // Store the original fetch for restoration
    const originalFetch = window.fetch;
    let moveCompleted = false;
    
    // Create a mock fetch
    window.fetch = function(url, options) {
        console.log(`Mock fetch called with url: ${url}`);
        
        // Return a mock response
        const responseData = {
            valid: true,
            board: {
                'e4': { type: 'p', color: 'white', code: 'P' },
                // Include enough of the board to avoid warnings
                'a1': { type: 'r', color: 'white', code: 'R' },
                'h1': { type: 'r', color: 'white', code: 'R' }
            },
            legalMoves: []
        };
        
        moveCompleted = true;
        
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
            originalAddEventListener.call(document, event, handler);
        }
    };
    
    // Define a cleanup function
    const cleanup = () => {
        window.fetch = originalFetch;
        document.addEventListener = originalAddEventListener;
    };
    
    try {
        // Reset the board to initial state
        const initialBoardState = {
            // Add white pieces in starting position
            'e2': { type: 'p', color: 'white', code: 'P' }
        };
        
        chessboard.updateBoard(initialBoardState);
        chessboard.deselectSquare();
        
        // Test the move process
        // 1. Select a piece
        chessboard.handleSquareClick('e2');
        this.assert(
            chessboard.selectedSquare === 'e2',
            'Should select the piece at e2'
        );
        
        // 2. Move the piece
        chessboard.handleSquareClick('e4');
        
        // 3. Check if the move was made (optimistic UI)
        // Since the move is async, we'll check the board after a delay
        return new Promise(resolve => {
            setTimeout(() => {
                try {
                    const pieceAtE4 = document.getElementById('e4').querySelector('.piece');
                    this.assert(
                        pieceAtE4 !== null,
                        'After move, piece should be present at e4'
                    );
                    
                    this.assert(
                        moveCompleted,
                        'Move request should have been sent to the backend'
                    );
                } catch (error) {
                    console.error('Error in async test:', error);
                    this.results.failed++;
                } finally {
                    cleanup();
                    resolve();
                }
            }, 100);
        });
    } catch (error) {
        cleanup();
        throw error;
    }
});

// Test fallback legal moves
TestSuite.registerTest('Fallback Legal Moves', function() {
    const chessboard = window.chessboard;
    
    // Ensure chessboard exists
    if (!this.assert(chessboard, 'Chessboard should exist')) {
        return;
    }
    
    // Clear legal moves to test fallback functionality
    const originalLegalMoves = [...chessboard.legalMoves];
    chessboard.legalMoves = [];
    
    // Select e2 pawn
    chessboard.deselectSquare();
    chessboard.selectSquare('e2');
    
    // Check if fallback legal moves were applied
    const e4Square = document.getElementById('e4');
    this.assert(
        e4Square.classList.contains('highlight'),
        'Fallback legal moves should highlight e4'
    );
    
    const e3Square = document.getElementById('e3');
    this.assert(
        e3Square.classList.contains('highlight'),
        'Fallback legal moves should highlight e3'
    );
    
    // Restore original legal moves
    chessboard.legalMoves = originalLegalMoves;
    chessboard.deselectSquare();
});

// ===== Initialize and run tests =====
document.addEventListener('DOMContentLoaded', function() {
    const runTestsButton = document.getElementById('run-tests-button');
    if (runTestsButton) {
        runTestsButton.addEventListener('click', function() {
            // Clear any previous test output
            const testOutput = document.getElementById('test-output');
            if (testOutput) {
                testOutput.innerHTML = '';
            }
            
            // Run tests
            TestSuite.runAll();
        });
    }
    
    // Auto-run tests if autorun parameter is present
    if (window.location.search.includes('autorun')) {
        setTimeout(() => {
            TestSuite.runAll();
        }, 500);
    }
});

// Make TestSuite available globally
window.TestSuite = TestSuite; 