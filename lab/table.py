"""
Class containing classes for printing tables
"""

# SPDX-FileCopyrightText: 2020 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from typing import List


class Table:
    """
    Manages and draws a table to the standard output
    """

    __columns: List[List[str]] = []

    def add_column(self, column: List[str]) -> None:
        """
        Add a column to the table.
        The column needs to be a list of strings
        """
        self.__columns.append(column)

    def add_row(self, row: List[str]) -> None:
        """
        Add a row to the table.
        The row needs to be a list of strings.
        """
        columns_len: int = Table.__columns_max_len(self.__columns)

        while len(row) > len(self.__columns):
            self.__columns.append([])

        for i, item in enumerate(row, 0):
            for column in self.__columns:
                while len(column) < columns_len:
                    column.append("")

            self.__columns[i].append(item)

    @staticmethod
    def __column_max_width(column: List[str]) -> int:
        lens: List[int] = []
        for string in column:
            lens.append(len(string))

        return max(lens)

    @staticmethod
    def __columns_max_len(columns: List[List[str]]) -> int:
        lens: List[int] = []
        for column in columns:
            lens.append(len(column))

        try:
            return max(lens)
        except ValueError:  # Happens if table is completely empty
            return 0

    def print(self) -> None:
        """
        print the table to the terminal
        """
        # Calculate width for each column
        column_widths: List[int] = []
        for col in self.__columns:
            column_widths.append(self.__column_max_width(col))

        # Build table
        for grid_y in range(0, Table.__columns_max_len(self.__columns)):
            textbuffer: str = ""

            for grid_x in range(0, len(self.__columns)):
                column: List[str] = self.__columns[grid_x]

                try:
                    textbuffer += column[grid_y]
                    textbuffer += (column_widths[grid_x] - len(column[grid_y]) + 2) * " "
                except IndexError:
                    textbuffer += (column_widths[grid_x] + 2) * " "

            print(textbuffer)
