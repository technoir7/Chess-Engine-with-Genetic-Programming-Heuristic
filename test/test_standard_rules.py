import json
import unittest

import app as app_module
from app import app, square_to_coord
from chess_logic_by_thomasahle import Position, initial


class DummySearcher:
    def search(self, pos, secs):
        return None, 0


def make_board(pieces):
    board = list(initial)

    for idx, char in enumerate(board):
        if char not in (' ', '\n'):
            board[idx] = '.'

    for square, piece in pieces.items():
        board[square_to_coord(square)] = piece

    return ''.join(board)


class StandardRulesTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        app_module.move_history = []
        app_module.current_player = 'white'

    def tearDown(self):
        self.app_context.pop()

    def test_en_passant_available_and_applied(self):
        board = make_board({
            'e1': 'K',
            'e8': 'k',
            'e5': 'P',
            'd5': 'p',
        })
        app_module.current_position = Position(
            board, 0, (False, False), (False, False), square_to_coord('d6'), 0
        )
        app_module.reset_rule_tracking()
        app_module.heuristic = object()
        app_module.searcher = DummySearcher()

        response = self.client.post(
            '/move',
            data=json.dumps({'from': 'e5', 'to': 'd6'}),
            content_type='application/json',
        )

        data = response.get_json()
        self.assertTrue(data['valid'])
        self.assertIn('d6', data['board'])
        self.assertNotIn('d5', data['board'])
        self.assertEqual(data['board']['d6']['color'], 'white')

    def test_castling_kingside_is_legal(self):
        board = make_board({
            'e1': 'K',
            'h1': 'R',
            'e8': 'k',
        })
        app_module.current_position = Position(
            board, 0, (False, True), (False, False), 0, 0
        )
        app_module.reset_rule_tracking()
        app_module.heuristic = object()
        app_module.searcher = DummySearcher()

        response = self.client.post(
            '/move',
            data=json.dumps({'from': 'e1', 'to': 'g1'}),
            content_type='application/json',
        )

        data = response.get_json()
        self.assertTrue(data['valid'])
        self.assertEqual(data['board']['g1']['type'], 'k')
        self.assertEqual(data['board']['f1']['type'], 'r')
        self.assertNotIn('h1', data['board'])

    def test_player_promotion_choice_is_applied(self):
        board = make_board({
            'e1': 'K',
            'e8': 'k',
            'a7': 'P',
        })
        app_module.current_position = Position(
            board, 0, (False, False), (False, False), 0, 0
        )
        app_module.reset_rule_tracking()
        app_module.heuristic = object()
        app_module.searcher = DummySearcher()

        response = self.client.post(
            '/move',
            data=json.dumps({'from': 'a7', 'to': 'a8', 'promotion': 'n'}),
            content_type='application/json',
        )

        data = response.get_json()
        self.assertTrue(data['valid'])
        self.assertEqual(data['board']['a8']['type'], 'n')
        self.assertEqual(data['board']['a8']['color'], 'white')

    def test_insufficient_material_draw_status(self):
        board = make_board({
            'e1': 'K',
            'e8': 'k',
        })
        position = Position(board, 0, (False, False), (False, False), 0, 0)
        app_module.position_history_counts = {app_module.get_position_hash(position): 1}
        app_module.halfmove_clock = 0

        status = app_module.get_game_status(position, 'white')
        self.assertTrue(status['game_over'])
        self.assertEqual(status['draw_reason'], 'insufficient material')

    def test_threefold_repetition_draw_status(self):
        position = Position(initial, 0, (True, True), (True, True), 0, 0)
        app_module.position_history_counts = {app_module.get_position_hash(position): 3}
        app_module.halfmove_clock = 0

        status = app_module.get_game_status(position, 'white')
        self.assertTrue(status['game_over'])
        self.assertEqual(status['draw_reason'], 'threefold repetition')

    def test_fifty_move_rule_draw_status(self):
        position = Position(initial, 0, (True, True), (True, True), 0, 0)
        app_module.position_history_counts = {app_module.get_position_hash(position): 1}
        app_module.halfmove_clock = 100

        status = app_module.get_game_status(position, 'white')
        self.assertTrue(status['game_over'])
        self.assertEqual(status['draw_reason'], 'fifty-move rule')

    def test_stalemate_draw_status(self):
        # King trapped with no legal moves and not in check
        board = make_board({
            'a8': 'k',
            'b6': 'Q',
            'c6': 'K',
        })
        position = Position(board, 0, (False, False), (False, False), 0, 0)
        # Rotate so it's black's turn (black king is stalemated)
        position = position.rotate()
        app_module.position_history_counts = {app_module.get_position_hash(position): 1}
        app_module.halfmove_clock = 0

        status = app_module.get_game_status(position, 'black')
        self.assertTrue(status['game_over'])
        self.assertEqual(status['draw_reason'], 'stalemate')

    def test_move_response_includes_required_fields(self):
        board = make_board({
            'e1': 'K',
            'e8': 'k',
            'e2': 'P',
        })
        app_module.current_position = Position(board, 0, (False, False), (False, False), 0, 0)
        app_module.reset_rule_tracking()
        app_module.heuristic = object()
        app_module.searcher = DummySearcher()
        app_module.current_player = 'white'

        response = self.client.post(
            '/move',
            data=json.dumps({'from': 'e2', 'to': 'e4'}),
            content_type='application/json',
        )

        data = response.get_json()
        for field in ('valid', 'board', 'legalMoves', 'game_over', 'result', 'in_check', 'draw_reason', 'currentPlayer'):
            self.assertIn(field, data, f"Response missing field: {field}")

    def test_illegal_move_rejected_with_valid_false(self):
        board = make_board({
            'e1': 'K',
            'e8': 'k',
            'e2': 'P',
        })
        app_module.current_position = Position(board, 0, (False, False), (False, False), 0, 0)
        app_module.reset_rule_tracking()
        app_module.heuristic = object()
        app_module.searcher = DummySearcher()
        app_module.current_player = 'white'

        response = self.client.post(
            '/move',
            data=json.dumps({'from': 'e2', 'to': 'e5'}),  # Illegal: pawn can't jump two from e2 to e5
            content_type='application/json',
        )

        data = response.get_json()
        self.assertFalse(data.get('valid'), "Illegal move should be rejected")

    def test_not_your_turn_rejected(self):
        board = make_board({
            'e1': 'K',
            'e8': 'k',
            'e2': 'P',
        })
        app_module.current_position = Position(board, 0, (False, False), (False, False), 0, 0)
        app_module.reset_rule_tracking()
        app_module.heuristic = object()
        app_module.searcher = DummySearcher()
        app_module.current_player = 'black'  # It's AI's turn, not player's

        response = self.client.post(
            '/move',
            data=json.dumps({'from': 'e2', 'to': 'e4'}),
            content_type='application/json',
        )

        data = response.get_json()
        self.assertFalse(data.get('valid'), "Move should be rejected when it's not the player's turn")

    def test_checkmate_status(self):
        # Queen + rook checkmate: white king at a1, black rook at h1 (check along
        # rank 1), black queen at b3 (covers a2 via diagonal, b1 via b-file, b2
        # via b-file), black king at e8. All escape squares blocked.
        board = make_board({
            'a1': 'K',
            'h1': 'r',
            'b3': 'q',
            'e8': 'k',
        })
        position = Position(board, 0, (False, False), (False, False), 0, 0)
        app_module.position_history_counts = {app_module.get_position_hash(position): 1}
        app_module.halfmove_clock = 0

        status = app_module.get_game_status(position, 'white')
        self.assertTrue(status['game_over'])
        self.assertTrue(status['in_check'])
        self.assertIsNone(status['draw_reason'])
        self.assertIn('Checkmate', status['result'])

    def test_in_check_field_true_when_in_check(self):
        # White king in check from black rook
        board = make_board({
            'e1': 'K',
            'e8': 'r',
            'a8': 'k',
        })
        position = Position(board, 0, (False, False), (False, False), 0, 0)
        app_module.position_history_counts = {app_module.get_position_hash(position): 1}
        app_module.halfmove_clock = 0

        status = app_module.get_game_status(position, 'white')
        self.assertTrue(status['in_check'])
        self.assertFalse(status['game_over'])  # King can escape

    def test_initialize_response_includes_current_player(self):
        response = self.client.post(
            '/initialize',
            data=json.dumps({'difficulty': 'easy'}),
            content_type='application/json',
        )
        data = response.get_json()
        self.assertIn('currentPlayer', data)
        self.assertEqual(data['currentPlayer'], 'white')


if __name__ == '__main__':
    unittest.main()
