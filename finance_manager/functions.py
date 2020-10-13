class periods:
    """
    Iterator for periods

    Exists for brevity/clarity in actual code
    """

    def __init__(self):
        pass

    def __iter__(self):
        self.a = 1
        return self

    def __next__(self):
        if self.a <= 12:
            x = self.a
            self.a += 1
            return x
        else:
            raise StopIteration
