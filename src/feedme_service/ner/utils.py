import torch
import zahlwort2num as w2n
from spellchecker import SpellChecker

tag_to_ix = {"P-LOC": 0, "M-LOC": 1, "A-LOC": 2, "O": 3}  # Assign each tag with a unique index
ix_to_tag = dict(zip(list(tag_to_ix.values()), list(tag_to_ix.keys())))


def extract_index_sequences(ix_list: list):
    sequence_map = {0: list()}
    current_sequence = 0

    for ix in range(len(ix_list)):
        try:
            if ix_list[ix] + 1 == ix_list[ix + 1]:
                sequence_map[current_sequence].append(ix_list[ix])
            else:
                sequence_map[current_sequence].append(ix_list[ix])
                current_sequence += 1
                sequence_map[current_sequence] = list()

        except IndexError:
            sequence_map[current_sequence].append(ix_list[ix])

    return sequence_map


def replace_string_numbers_with_numbers(word_list: list, replace_index_map: dict):
    length = len(word_list)
    diff = 0
    for i, (replace_word, ix) in enumerate(replace_index_map.items()):
        ix = [n + diff for n in ix]

        start = word_list[:min(ix)]
        end = word_list[max(ix) + 1:]

        word_list = start + [replace_word] + end
        diff = len(word_list) - length
        length = len(word_list)

    return word_list


def convert_text_to_number(text: str) -> str:
    word_split = text.lower().split(" ")
    number_split = list()
    number_word = list()

    for ix, word in enumerate(word_split):
        try:
            if word == "komma":
                number_split.append(".")
            elif word == "und":
                continue
            else:
                number_split.append(str(w2n.convert(word)))
            number_word.append(ix)

        except KeyError:
            continue

    new_word_split = extract_index_sequences(number_word)
    replace_map = {}

    start = 0
    for key, values in new_word_split.items():
        concated_number = "".join(str(x) for x in number_split[start:start + len(values)])
        replace_map[concated_number] = values
        start += len(values)

    return " ".join(replace_string_numbers_with_numbers(word_split, replace_map))


def prepare_sequence(seq, to_ix):
    idxs = [to_ix[w] for w in seq]
    return torch.tensor(idxs, dtype=torch.long)


def correct_spelling(text: str):
    spell = SpellChecker(language='de')
    try:
        corrected_text = spell.correction(text)
        return corrected_text
    except Exception as e:
        print("could not correct", text, e)
        return text