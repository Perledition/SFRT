# import standard modules

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

    def extract(self, sentence, prediction):
        arg_max_convert = prediction.numpy().astype(int)

        tags = [self.ix_to_tag[x] for x in arg_max_convert]
        data = {"P-LOC": list(), "A-LOC": list(), "M-LOC": list() }

        for ix, tag in enumerate(tags):
            if tag != "O":
                data[tag].append(sentence[ix])

        return pd.DataFrame(data).rename(columns={"P-LOC": "Produkt", "A-LOC": "Menge", "M-LOC": "Maßeinheit"})