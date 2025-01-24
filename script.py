import timeit

from quantikai.game import Board, Pawns, Colors, Move

if __name__ == "__main__":
    # 1.9-2
    # board = Board(
    #     board=[
    #         [(Pawns.A, Colors.BLUE), None, None, None],
    #         [None, None, (Pawns.B, Colors.BLUE), None],
    #         [None, (Pawns.C, Colors.BLUE), None, None],
    #         [None, None, None, (Pawns.D, Colors.BLUE)],
    #     ]
    # )
    # print("_check_move_is_valid")
    # print(
    #     timeit.timeit(
    #         lambda: board._check_move_is_valid(Move(2, 2, Pawns.D, Colors.BLUE))
    #     )
    # )
    # # 1.4-1.6
    board = Board(
        board=[
            [(Pawns.A, Colors.BLUE), None, None, None],
            [None, None, (Pawns.B, Colors.BLUE), None],
            [None, (Pawns.C, Colors.BLUE), None, None],
            [None, None, None, (Pawns.D, Colors.BLUE)],
        ]
    )
    print("_check_move_is_win")
    print(timeit.timeit(lambda: board._move_is_a_win(2, 2), number=1000000))
    # get_possible_moves - optimize=False - 1 pawn
    # 59.88025159500103
    # get_possible_moves - optimize=False - 2 pawns
    # 56.686884267001005
    # get_possible_moves - optimize=False - 3 pawns
    # 52.76525373199547

    # #### after opti
    # get_possible_moves - optimize=False - 1 pawn
    # 62.09644343499531
    # get_possible_moves - optimize=False - 2 pawns
    # 54.56482182000036
    # get_possible_moves - optimize=False - 3 pawns
    # 49.24243845699675

    # board = Board(
    #     board=[
    #         [None, None, None, None],
    #         [None, None, (Pawns.B, Colors.BLUE), None],
    #         [None, None, None, None],
    #         [None, None, None, None],
    #     ]
    # )

    # print("get_possible_moves - optimize=False - 1 pawn")
    # print(
    #     timeit.timeit(
    #         lambda: board.get_possible_moves([Pawns.A, Pawns.B, Pawns.C, Pawns.D], Colors.RED)
    #     )
    # )
    # board = Board(
    #     board=[
    #         [None, None, None, None],
    #         [None, None, (Pawns.B, Colors.BLUE), None],
    #         [None, None, None, None],
    #         [(Pawns.D, Colors.BLUE), None, None, None],
    #     ]
    # )
    # print("get_possible_moves - optimize=False - 2 pawns")
    # print(
    #     timeit.timeit(
    #         lambda: board.get_possible_moves([Pawns.A, Pawns.B, Pawns.C, Pawns.D], Colors.RED)
    #     )
    # )
    # board = Board(
    #     board=[
    #         [None, (Pawns.C, Colors.BLUE), None, None],
    #         [None, None, (Pawns.B, Colors.BLUE), None],
    #         [None, None, None, None],
    #         [(Pawns.D, Colors.BLUE), None, None, None],
    #     ]
    # )
    # print("get_possible_moves - optimize=False - 3 pawns")
    # print(
    #     timeit.timeit(
    #         lambda: board.get_possible_moves([Pawns.A, Pawns.B, Pawns.C, Pawns.D], Colors.RED)
    #     )
    # )
    # # 28.47s
    # print("get_possible_moves - optimize=True")
    # print(
    #     timeit.timeit(
    #         lambda: board.get_possible_moves(
    #             [Pawns.A, Pawns.B, Pawns.C, Pawns.D], Colors.RED, optimize=True
    #         )
    #     )
    # )
