# import standard modules
import os
import time
import random
import datetime as dt

# import third party modules
import torch
import pandas as pd
from torch import nn
from torch.optim import Adam
from torchtext.data import Field, BucketIterator
from torchtext.datasets import SequenceTaggingDataset


class FoodTextDataset(object):

     def __init__(self, input_folder: str, min_word_freq: int, batch_size: int):
         self.word_field = Field(lower=True)
         self.tag_field = Field(unk_token=None)

         # create dataset using built-in parser torchtext
         self.train_dataset, self.val_dataset, self.test_dataset = SequenceTaggingDataset.splits(
             path=input_folder,
             train="train.tsv",
             validation="test.tsv",
             test="test.tsv",
             fields=(("word", self.word_field), ("tag", self.tag_field))
         )

         # convert fields to vocabulary list
         self.word_field.build_vocab(self.train_dataset.word, min_freq=min_word_freq)
         self.tag_field.build_vocab(self.train_dataset.tag)
         self.train_iter, self.val_iter, self.test_iter = data.BucketIterator.splits(
             datasets=(self.train_dataset, self.val_dataset, self.test_dataset),
             batch_size=batch_size
         )

         # prepare padding index to be ignored during model training/evaluation
         self.word_pad_idx = self.word_field.vocab.stoi[self.word_field.pad_token]
         self.tag_pad_idx = self.tag_field.vocab.stoi[self.tag_field.pad_token]

     
class FoodTextGenerator:

    CONCAT_WORDS = ["und", "ähm", "err", " ", "außerdem noch", "sowie", ","]

    def __init__(self):

        base_path = os.path.join(os.getcwd(), "datagenerator", "data_pool")
        self.products = self.read_from_data_pool(os.path.join(base_path, "products.txt"))
        self.measures = self.read_from_data_pool(os.path.join(base_path, "measures.txt"))

    @classmethod
    def read_from_data_pool(cls, path: str) -> list:
        return open(path, "r").read().split()

    def concat_word(self):
        return random.choice(self.CONCAT_WORDS)

    @classmethod
    def float_to_text(cls, num: float):
        if num == 0:
            return "null"

        units = ["", "ein", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun"]
        teens = ["zehn", "elf", "zwölf", "dreizehn", "vierzehn", "fünfzehn", "sechzehn", "siebzehn", "achtzehn", "neunzehn"]
        tens = ["zwanzig", "dreißig", "vierzig", "fünfzig", "sechzig", "siebzig", "achtzig", "neunzig"]
        scales = ["", "tausend", "million", "milliarde", "billion", "billiarde"]

        result = []
        if num < 0:
            result.append("minus")
            num = abs(num)

        whole = int(num)
        frac = int((num % 1) * 100 + 0.5)

        if frac >= 100:
            whole += 1
            frac -= 100

        scale_index = 0
        while whole > 0:
            chunk = whole % 1000
            if chunk > 0:
                if chunk >= 100:
                    result.append(units[int(chunk / 100)])
                    result.append("hundert")
                if chunk % 100 < 20:
                    result.append(teens[chunk % 100 - 10])
                else:
                    result.append(tens[int((chunk % 100) / 10) - 2])
                    result.append(units[chunk % 10])
                result.append(scales[scale_index])
            whole = int(whole / 1000)
            scale_index += 1

        if frac > 0:
            result.append("und")
            if frac % 10 > 0:
                result.append(units[frac % 10])
            if frac // 10 > 0:
                result.append(tens[frac // 10 - 2])

        return " ".join(reversed(result))

    def create_random_product_entity(self):
        return {
            "P-LOC": random.choice(self.products),
            "M-LOC": random.choice(self.measures),
            "A-LOC": self.float_to_text(round(random.uniform(0.2, 1000.5), 2))
        }

    def sentence_blueprint(self):
        return random.choice(["ich mische", "dazu kommen noch", "hinzu kommen", "", "es kommen noch rein", "dazu"])

    def generate_random_sentence(self, params):
        sentences = list()
        targets = list()
        keys = ["P-LOC", "A-LOC", "M-LOC"]
        for ix, entity in enumerate(params):
            reversed_entity = dict(zip(entity.values(), entity.keys()))
            random.shuffle(keys)
            sentence = " ".join([
                self.sentence_blueprint().lower(),
                entity[keys[0]].lower(),
                entity[keys[1]].lower(),
                entity[keys[2]].lower(),
                random.choice(self.CONCAT_WORDS).lower() if ix < len(params) else ""
            ])

            target = ['O' if x not in list(reversed_entity.keys()) else reversed_entity[x] for x in sentence.split()]
            sentences.append(sentence)
            targets += target

        sentences = " ".join(sentences)
        return sentences.split(), targets

    def generate_random_parameters(self):
        # [{product: x, amount: y, measure: z},...]
        targets = list()
        amount_entity = random.randint(1, 4)
        for _ in range(amount_entity):
            targets.append(self.create_random_product_entity())
            sentence, target = self.generate_random_sentence(targets)

        return target, sentence

    def write_data_samples_out(self, data, path_name: str = ""):
        sentences = list()
        tags = list()

        for sample in data:
            sentences.append(" ".join(x for x in sample[1]))
            tags.append(" ".join(x for x in sample[0]))

        directory = os.path.join(
            os.getcwd(),
            "datagenerator",
            "output",
            str(dt.datetime.now().date())
        )
        if not os.path.exists(directory):
            os.makedirs(directory)

        df = pd.DataFrame({"sentences": sentences, "tags": tags})
        df.to_csv(os.path.join(
            directory,
            path_name
        ), sep=";", index=False)

    def create(self, n: int = 10, write_out: bool = True):
        train_data = list()
        test_data = list()
        val_data = list()

        for _ in range(n):
            train_data.append(self.generate_random_parameters())
            val_data.append(self.generate_random_parameters())
            test_data.append(self.generate_random_parameters())

        if write_out:
            self.write_data_samples_out(train_data, path_name="train.csv")
            self.write_data_samples_out(test_data, path_name="test.csv")
            self.write_data_samples_out(val_data, path_name="val.csv")
