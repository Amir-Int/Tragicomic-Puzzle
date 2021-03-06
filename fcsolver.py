import numpy
from GUI import Interface


class Solver:
    """
    Class Solver is the agent that attempts to do this puzzle, using the backtracking
    algorithm. This class uses maintaining arc-consistency method to propagate constraints.
    """

    def __init__(self, n):
        """
        Initialises this class
        :param n: The size of the board
        """
        self.board = None
        self.board_size = int(n)
        self.variable_queue = []
        self.variable_stack = []
        self.filled_rows = numpy.empty(self.board_size, dtype=object)
        self.filled_columns = numpy.empty(self.board_size, dtype=object)
        self.gui = Interface(self.board_size)

    def set_board(self, board):
        """
        Sets up the playing board
        :param board: The puzzle board
        """
        self.board = board.board

    def next_to_evaluate(self):
        """
        :return: Returns the next variable on the queue to be evaluated
        """
        if len(self.variable_queue) > 0:
            most_restricted = 0
            for variable in range(len(self.variable_queue)):
                if len(self.variable_queue[variable].domain) < len(self.variable_queue[most_restricted].domain):
                    most_restricted = variable
            return self.variable_queue.pop(most_restricted)
        return None

    def previously_evaluated(self):
        """
        :return: The previously (recently) evaluated variable, in case of a backtrack.
        """
        return self.variable_stack.pop(len(self.variable_stack) - 1)

    def add_to_gui(self, changed_variable):
        """
        Adds a trace of the solving procedure to the graphical interface object
        to hold track of what's been done.
        :param changed_variable: The variable that's undergone a change at the current level
        """
        board_values = []
        if changed_variable is not None:
            board_values.append(changed_variable.row)
            board_values.append(changed_variable.column)
        else:
            board_values.append(-1)
            board_values.append(-1)
        for i in self.board:
            for j in i:
                board_values.append(j.value)
                if len(j.domain) > 1:
                    board_values.append(j.domain[0])
                    board_values.append(j.domain[1])
                elif len(j.domain) > 0:
                    board_values.append(j.domain[0])
                    board_values.append(-1)
                else:
                    board_values.append(-1)
                    board_values.append(-1)
        self.gui.boards.append(board_values)

    def apply_constraint(self, variable, constraint_target):
        """
        Applies the constraints made by evaluating this variable to
        a target (typically a neighbour)
        :param variable: The recently evaluated variable
        :param constraint_target: The constraint target to which constraints are to be applied
        :return: True if this constraint is applicable; that is, after applying
        constraints the domain of the target is not empty, false otherwise.
        """
        if constraint_target.value == -1:
            if variable.value in constraint_target.domain:
                value_index = constraint_target.domain.index(variable.value)
                if len(constraint_target.domain) > 1:
                    constraint_target.domain.pop(value_index)
                    variable.constrained_variables.append(constraint_target)
                    self.add_to_gui(constraint_target)
                else:
                    return False
        return True

    def lift_constraints(self, variable):
        """
        Lift the wrongly applied constraints in case of a backtrack.
        :param variable: The last evaluated variable, from which backtracking occurs
        """
        for v in variable.constrained_variables:
            v.domain = [0, 1]
        variable.domain = [0, 1]
        variable.constrained_variables = []
        self.add_to_gui(variable)

    def propagate_horizontal_constraints(self, variable):
        """
        Applies constraints on a row
        :param variable: The recently evaluated variable
        :return: True if this constraint is applicable, false otherwise
        """
        # Checking if the variable to the left of this variable has the same value as this variable
        if variable.column > 0 and \
                self.board[variable.row, variable.column - 1].value == variable.value:
            if variable.column > 1:
                constraint_target = self.board[variable.row, variable.column - 2]
                if not self.apply_constraint(variable, constraint_target):
                    return False
            if variable.column < self.board_size - 1:
                constraint_target = self.board[variable.row, variable.column + 1]
                if not self.apply_constraint(variable, constraint_target):
                    return False

        # Checking if the variable to the right of this variable has the same value as this variable
        if variable.column < self.board_size - 1 and \
                self.board[variable.row, variable.column + 1].value == variable.value:
            if variable.column > 0:
                constraint_target = self.board[variable.row, variable.column - 1]
                if not self.apply_constraint(variable, constraint_target):
                    return False
            if variable.column < self.board_size - 2:
                constraint_target = self.board[variable.row, variable.column + 2]
                if not self.apply_constraint(variable, constraint_target):
                    return False

        # Checking if this variable encloses a variable in between itself and another identically evaluated variable
        if variable.column > 1 and \
                self.board[variable.row, variable.column - 2].value == variable.value:
            constraint_target = self.board[variable.row, variable.column - 1]
            if not self.apply_constraint(variable, constraint_target):
                return False
        if variable.column < self.board_size - 2 and \
                self.board[variable.row, variable.column + 2].value == variable.value:
            constraint_target = self.board[variable.row, variable.column + 1]
            if not self.apply_constraint(variable, constraint_target):
                return False
        return True

    def propagate_vertical_constraints(self, variable):
        """
        Applies constraints in a column
        :param variable: The recently evaluated variable
        :return: True if this constraint is applicable, false otherwise
        """
        # Checking if the variable above this variable has the same value as this variable
        if variable.row > 0 and \
                self.board[variable.row - 1, variable.column].value == variable.value:
            if variable.row > 1:
                constraint_target = self.board[variable.row - 2, variable.column]
                if not self.apply_constraint(variable, constraint_target):
                    return False
            if variable.row < self.board_size - 1:
                constraint_target = self.board[variable.row + 1, variable.column]
                if not self.apply_constraint(variable, constraint_target):
                    return False

        # Checking if the variable below this variable has the same value as this variable
        if variable.row < self.board_size - 1 and \
                self.board[variable.row + 1, variable.column].value == variable.value:
            if variable.row > 0:
                constraint_target = self.board[variable.row - 1, variable.column]
                if not self.apply_constraint(variable, constraint_target):
                    return False
            if variable.row < self.board_size - 2:
                constraint_target = self.board[variable.row + 2, variable.column]
                if not self.apply_constraint(variable, constraint_target):
                    return False

        # Checking if this variable encloses a variable in between itself and another identically evaluated variable
        if variable.row > 1 and \
                self.board[variable.row - 2, variable.column].value == variable.value:
            constraint_target = self.board[variable.row - 1, variable.column]
            if not self.apply_constraint(variable, constraint_target):
                return False
        if variable.row < self.board_size - 2 and \
                self.board[variable.row + 2, variable.column].value == variable.value:
            constraint_target = self.board[variable.row + 1, variable.column]
            if not self.apply_constraint(variable, constraint_target):
                return False
        return True

    def is_row_filled_properly(self, variable):
        """
        Checks if the variable's row is filled properly, and propagating
        corresponding constraints, as well.
        :param variable: The recently evaluated variable.
        :return: True if this row is properly arranged, false otherwise
        """
        zeros_counter = 0
        ones_counter = 0
        non_evaluated_variable = -1
        row_string = ''

        for i in range(self.board_size):
            row_string = row_string + str(self.board[variable.row, i].value)
            if self.board[variable.row, i].value == -1:
                non_evaluated_variable = i
            elif self.board[variable.row, i].value == 1:
                ones_counter += 1
            else:
                zeros_counter += 1

        if zeros_counter + ones_counter == self.board_size:
            self.filled_rows[variable.row] = row_string

        else:
            eliminating_value = -1
            if zeros_counter == self.board_size / 2:
                eliminating_value = 0
            elif ones_counter == self.board_size / 2:
                eliminating_value = 1

            if zeros_counter == self.board_size / 2 or ones_counter == self.board_size / 2:
                for i in range(self.board_size):
                    constraint_target = self.board[variable.row, i]
                    if constraint_target.value == -1:
                        value_index = -1
                        if eliminating_value in constraint_target.domain:
                            value_index = constraint_target.domain.index(eliminating_value)
                        if value_index >= 0:
                            if len(constraint_target.domain) > 1:
                                constraint_target.domain.pop(value_index)
                                variable.constrained_variables.append(constraint_target)
                            else:
                                return False

            if zeros_counter + ones_counter == self.board_size - 1:
                for row in self.filled_rows:
                    if row is not None:
                        identical = True
                        for j in range(self.board_size):
                            if j != non_evaluated_variable and int(row[j]) != self.board[variable.row, j].value:
                                identical = False
                                break
                        if identical:
                            eliminating_value = int(row[non_evaluated_variable])
                            constraint_target = self.board[variable.row, non_evaluated_variable]
                            if eliminating_value in constraint_target.domain:
                                value_index = constraint_target.domain.index(eliminating_value)
                                if len(constraint_target.domain) > 1:
                                    constraint_target.domain.pop(value_index)
                                    variable.constrained_variables.append(constraint_target)
                                else:
                                    return False

        return True

    def is_column_filled_properly(self, variable):
        """
        Checks if the variable's column is filled properly, and propagating
        corresponding constraints, as well.
        :param variable: The recently evaluated variable.
        :return: True if this column is properly arranged, false otherwise
        """
        zeros_counter = 0
        ones_counter = 0
        non_evaluated_variable = -1
        column_string = ''

        for i in range(self.board_size):
            column_string = column_string + str(self.board[i, variable.column].value)
            if self.board[i, variable.column].value == -1:
                non_evaluated_variable = i
            elif self.board[i, variable.column].value == 1:
                ones_counter += 1
            else:
                zeros_counter += 1

        if zeros_counter + ones_counter == self.board_size:
            self.filled_columns[variable.column] = column_string

        else:
            eliminating_value = -1
            if zeros_counter == self.board_size / 2:
                eliminating_value = 0
            elif ones_counter == self.board_size / 2:
                eliminating_value = 1

            if zeros_counter == self.board_size / 2 or ones_counter == self.board_size / 2:
                for i in range(self.board_size):
                    if self.board[i, variable.column].value == -1:
                        constraint_target = self.board[i, variable.column]
                        value_index = -1
                        if eliminating_value in constraint_target.domain:
                            value_index = constraint_target.domain.index(eliminating_value)
                        if value_index >= 0:
                            if len(constraint_target.domain) > 1:
                                constraint_target.domain.pop(value_index)
                                variable.constrained_variables.append(constraint_target)
                            else:
                                return False

            if zeros_counter + ones_counter == self.board_size - 1:
                for column in self.filled_columns:
                    if column is not None:
                        identical = True
                        for j in range(self.board_size):
                            if j != non_evaluated_variable and int(column[j]) != self.board[j, variable.column].value:
                                identical = False
                                break
                        if identical:
                            eliminating_value = int(column[non_evaluated_variable])
                            constraint_target = self.board[non_evaluated_variable, variable.column]
                            if eliminating_value in constraint_target.domain:
                                value_index = constraint_target.domain.index(eliminating_value)
                                if len(constraint_target.domain) > 1:
                                    constraint_target.domain.pop(value_index)
                                    variable.constrained_variables.append(constraint_target)
                                else:
                                    return False
        return True

    def propagate_constraints(self, variable):
        """
        Propagates constraints after evaluating this variable.
        :param variable: The recently evaluated variable
        :return: True if no issue is encountered, false if backtracking is required
        """
        if self.propagate_horizontal_constraints(variable) and \
                self.propagate_vertical_constraints(variable) and \
                self.is_row_filled_properly(variable) and \
                self.is_column_filled_properly(variable):
            return True
        return False

    def solve(self):
        """
        Performs the procedure of solving the puzzle holistically.
        :return: True if the puzzle is solved, false if it's an impossible puzzle
        """

        self.add_to_gui(None)

        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i, j].value != -1:
                    successful = self.propagate_constraints(self.board[i, j])
                    if not successful:
                        return False

        next_variable = self.next_to_evaluate()
        while True:
            # If the next variable's domain is non-empty:
            if len(next_variable.domain) > 0:
                # Evaluates the next variable to the first value present in its domain
                next_variable.value = next_variable.domain.pop(0)
                domain = next_variable.domain
                # If it is to change value, it first needs to lift the applied constraints:
                self.lift_constraints(next_variable)
                next_variable.domain = domain
                if self.propagate_constraints(next_variable):
                    # If constraints are propagated without any issues:
                    self.variable_stack.append(next_variable)
                    next_variable = self.next_to_evaluate()
                    if next_variable is None:
                        self.gui.root.mainloop()
                        return True
                else:
                    # If it encounters a problem propagating the constraints:
                    self.filled_rows[next_variable.row] = None
                    self.filled_columns[next_variable.column] = None
                    next_variable = next_variable
            # If the next variable's domain runs out of values:
            else:
                # Devalues the next value:
                next_variable.value = -1
                # Lifts all the constraints applied by the next variable:
                self.lift_constraints(next_variable)
                # Returns the next variable back to queue:
                queue = [next_variable]
                for c in self.variable_queue:
                    queue.append(c)
                self.variable_queue = queue
                if len(self.variable_stack) > 0:
                    self.filled_rows[next_variable.row] = None
                    self.filled_columns[next_variable.column] = None
                    next_variable = self.previously_evaluated()
                else:
                    self.gui.root.mainloop()
                    return False
