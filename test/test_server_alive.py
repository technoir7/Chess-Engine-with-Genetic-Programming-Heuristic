#!/usr/bin/env python
"""
Test suite that verifies the key API endpoints of the chess engine using the
Flask test client rather than a live network server.

The original version of this file sent real HTTP requests to localhost:5001.
That approach requires the server to be running externally, which makes the
tests unreliable in CI and on developer machines.  The rewritten version uses
Flask's built-in test client so the tests are self-contained and always run.
"""

import json
import time
import unittest

from app import app


class TestServerAlive(unittest.TestCase):
    """Test that key API endpoints respond correctly via the Flask test client."""

    def setUp(self):
        """Initialise the Flask test client before each test."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_01_server_running(self):
        """GET / should return the main HTML page with HTTP 200."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200,
                         "GET / should return HTTP 200")

    def test_02_initialize_endpoint(self):
        """POST /initialize should return a valid game state."""
        response = self.client.post(
            '/initialize',
            data=json.dumps({'difficulty': 'easy'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200,
                         "/initialize should return HTTP 200")
        data = response.get_json()
        self.assertIn('currentPlayer', data,
                      "Initialize response should contain 'currentPlayer'")
        self.assertEqual(data['currentPlayer'], 'white',
                         "Game always starts with white to move")

    def test_03_move_endpoint(self):
        """POST /move with a legal pawn move should return HTTP 200 and valid=True."""
        # Initialise first so global state is set up.
        self.client.post(
            '/initialize',
            data=json.dumps({'difficulty': 'easy'}),
            content_type='application/json',
        )

        response = self.client.post(
            '/move',
            data=json.dumps({'from': 'e2', 'to': 'e4'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200,
                         "POST /move should return HTTP 200 for a legal move")
        data = response.get_json()
        self.assertIn('board', data, "Move response should contain 'board'")
        self.assertTrue(data.get('valid', False),
                        "A legal pawn move should be reported as valid")

    def test_04_start_new_game(self):
        """A second /initialize call resets the game cleanly."""
        response = self.client.post(
            '/initialize',
            data=json.dumps({'difficulty': 'easy'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200,
                         "Second /initialize call should return HTTP 200")
        data = response.get_json()
        self.assertIn('board', data, "New-game response should contain 'board'")
        self.assertEqual(data.get('gameState'), 'active',
                         "Game state should be 'active' after initialization")

    def test_05_server_response_time(self):
        """GET / and POST /initialize should both respond quickly."""
        endpoints = []

        start = time.time()
        self.client.get('/')
        endpoints.append(('GET /', time.time() - start))

        start = time.time()
        self.client.post(
            '/initialize',
            data=json.dumps({'difficulty': 'easy'}),
            content_type='application/json',
        )
        endpoints.append(('POST /initialize', time.time() - start))

        for name, elapsed in endpoints:
            # In-process requests should complete in well under 5 seconds
            # (the /initialize sets up a minimax searcher but doesn't search).
            self.assertLess(elapsed, 5.0,
                            f"{name} took {elapsed:.3f}s — expected < 5 s")


def main():
    unittest.main()


if __name__ == '__main__':
    main()
