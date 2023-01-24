import torch

tag_to_ix = {"P-LOC": 0, "M-LOC": 1, "A-LOC": 2, "O": 3}  # Assign each tag with a unique index
ix_to_tag = dict(zip(list(tag_to_ix.values()), list(tag_to_ix.keys())))

def prepare_sequence(seq, to_ix):
    idxs = [to_ix[w] for w in seq]
    return torch.tensor(idxs, dtype=torch.long)