



class Register:
    def __init__(self, *,
                 width: int,
                 full_inst_name: str):
        self.value = 0

    def read(self):
        return self.value

    def write(self, data):
        self.value = data





