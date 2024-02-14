from enum import Enum

class APP_PAGE(Enum):
        MAIN = 0
        SETTING = 1

class Frequency_Selection(Enum):
        LPF_6K = 0
        LPF_12K = 1
        LPF_18K = 2
        LPF_FULL = 3

        def Frequency_list(self):
            return [self.LPF_6K,self.LPF_12K,self.LPF_18K,self.LPF_FULL] 