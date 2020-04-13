from typing import List

class Table:
    __columns: List[List[str]] = []

    """
    Add a column to the table.
    The column needs to be a list of strings
    """
    def add_column(self, column: List[str]):
        self.__columns.append(column)

    """
    Add a row to the table.
    The row needs to be a list of strings.
    """
    def add_row(self, row: List[str]):
        columns_len: int = Table.__columns_max_len(self.__columns)

        while (len(row) > len(self.__columns)):
            self.__columns.append([])

        for i in range(0, len(row)):
            for column in self.__columns:
                while (len(column) < columns_len):
                    column.append("")

            self.__columns[i].append(row[i])

    @staticmethod
    def __column_max_width(column: List[str]) -> int:
        lens: List[int] = []
        for string in column:
            lens.append(len(string))

        return max(lens)

    @staticmethod
    def __columns_max_len(columns: [List[List[str]]]) -> int:
        lens: List[int] = []
        for column in columns:
            lens.append(len(column))

        try:
            return max(lens)
        except ValueError: # Happens if table is completely empty
            return 0

    def print(self):
        #print(self.__columns)

        for y in range(0, Table.__columns_max_len(self.__columns)):
            textbuffer: str = ""
            for column in self.__columns:
                #print(column)
                width = self.__column_max_width(column) # Inefficient
                try:
                    textbuffer += column[y]
                    textbuffer += (width - len(column[y]) + 2) * " "
                except IndexError:
                    textbuffer += (width + 2) * " "

            print(textbuffer)
