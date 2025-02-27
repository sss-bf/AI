from datetime import datetime

class CurrentDateTime:
    def __str__(self):
        return datetime.now().strftime("%Y%m%d-%H%M%S")
    
    def __repr__(self):
        return self.__str__()
