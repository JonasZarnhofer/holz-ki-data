class LimitValueError(Exception):
    def __init__(self, limit):
        self.limit = limit
        super().__init__(f"Limit value '{limit}' is not a positive integer.")


class ValueNotFound(Exception):
    def __init__(self, value, table):
        self.value = value
        self.table = table
        super().__init__(f"Value '{value}' not found in table '{table}'.")


class NonExistantColumn(Exception):
    def __init__(self, column):
        self.column = column
        super().__init__(f"Column {column} does not exist in the table.")


class InvalidSortOption(Exception):
    def __init__(self, sort_option):
        self.sort_option = sort_option
        super().__init__(
            f"Sort option '{sort_option}' is invalid. It must be either 'asc' or 'desc'."
        )


class ResourceNotFound(Exception):
    def __init__(self, resource, id):
        self.resource = resource
        super().__init__(f"Resource '{resource}' with id '{id}' could not be found.")
