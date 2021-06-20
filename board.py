from variable import Variable
import numpy


class Board:

    def __init__(self, n, solver):
        self.board = numpy.empty((n, n), dtype=object)
        for i in range(n):
            p = input().split()
            for j in range(n):
                if p[j] == '-':
                    self.board[i, j] = Variable(-1, i, j)
                    solver.variable_queue.append(self.board[i, j])
                else:
                    self.board[i, j] = Variable(int(p[j]), i, j)
