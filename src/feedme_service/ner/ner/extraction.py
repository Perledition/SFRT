# import standard modules
import numexpr

# import third party modules
import pandas as pd


# https://openfoodfacts.github.io/openfoodfacts-python/Usage/

class IngredientsExtractor:

    def __init__(self, ix_to_tag):
        self.ix_to_tag = ix_to_tag

    @staticmethod
    def map_measures_to_concrete_numbers(amount, measure):
        mapping = {"teelöffel": {"gramm", 15}, "brise": {"gramm", 2}}
        return mapping[measure], amount

    @classmethod
    def text_to_int(cls, text: str):
        try:
            return int(numexpr.evaluate(text.replace(" ", "")))
        except:
            return text

    def extract(self, sentence, prediction):
        arg_max_convert = prediction.numpy().astype(int)

        tags = [self.ix_to_tag[x] for x in arg_max_convert]
        data = {"P-LOC": list(), "A-LOC": list(), "M-LOC": list() }

        for ix, tag in enumerate(tags):
            if tag != "O":
                data[tag].append(sentence[ix])

        int_amount = list()
        for txt_amount in data.get("A-LOC", list(0 for _ in range(len(data.get("P-LOC"))))):
            int_amount.append(self.text_to_int(txt_amount))
        
        data["A-LOC"] = int_amount        

        return pd.DataFrame(data).rename(columns={"P-LOC": "Produkt", "A-LOC": "Menge", "M-LOC": "Maßeinheit"})