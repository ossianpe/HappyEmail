class FrequentVariables:
    def __init__(self):
        word_of_day = ""
        self.files = []
        lenght_of_database_table = 0
    def set_wod(self, wod):
        self.word_of_day = wod
    def get_wod(self):
        return self.word_of_day
    def append_files(self, fil):
        self.files.append(fil)
    def get_files(self):
        return self.files
    def set_length_of_database_table(self, lodt):
        temp_lodt_str = ""
        temp_lodt_str = str(lodt).replace("(", "").replace(",", "").replace(")", "")
        self.length_of_database_table = int(temp_lodt_str)
    def get_length_of_database_table(self):
        return self.length_of_database_table
