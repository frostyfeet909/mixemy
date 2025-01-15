from abc import ABC


class Base(ABC):
    a_: int

    def __init__(self) -> None:
        self.a = self.a_

    def p(self) -> None:
        print(self.a)


class Child(Base, ABC):
    pass


class SuperChild(Child):
    pass


a = SuperChild()
a.p()
