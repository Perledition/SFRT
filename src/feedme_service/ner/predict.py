import os
import json
import torch
import pandas as pd

# import project related modules
from feedme_service.settings import ner_model, word_to_ix
from feedme_service.ner.ner.extraction import IngredientsExtractor
from feedme_service.ner.utils import tag_to_ix, ix_to_tag, prepare_sequence


def predict(sentence: str):

    try:
        with torch.no_grad():
            inputs = prepare_sequence(sentence.replace("vier", "4").split(" "), word_to_ix)
            tag_scores = ner_model.forward(inputs)

            # The sentence is "the dog ate the apple". i,j corresponds to score for tag j
            # for word i. The predicated tag is the maximum scoring tag.
            # Here, we can see the predicted sequence below is 0 1 2 0 1
            # since 0 is index of the maximum value of row 1,
            # 1 is the index of maximum value of row 2, etc.
            # Which is DET NOUN VERB DET NOUN, the correct sequence!

            arg_max = torch.argmax(tag_scores, dim=1)
            ie = IngredientsExtractor(ix_to_tag)
            return ie.extract(sentence.split(" "), arg_max)

    except KeyError as e:
        print("KeyError: ", e)
        return pd.DataFrame({"output": [str(e)]})
