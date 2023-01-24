import os


def load_data(file_name: str):
    with open(os.path.join(os.getcwd(), "datagenerator", "output", file_name), "r", encoding="latin-1") as f:
        data = f.readlines()
        print(data)