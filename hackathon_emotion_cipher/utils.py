# utils.py
import numpy as np
from sklearn.decomposition import PCA

# For a quick hack: sign of PCA projected vector -> binary signature
def embedding_to_signature(embedding, bits=128, pca=None):
    # embedding: 1D numpy array
    if pca is None:
        pca = PCA(n_components=min(bits, embedding.shape[0]))
        # caller should fit PCA on many examples in production. For demo we do identity.
        try:
            reduced = pca.fit_transform(embedding.reshape(1, -1))[0]
        except Exception:
            # fallback: pad/truncate
            arr = embedding
            if len(arr) < bits:
                arr = np.pad(arr, (0, bits-len(arr)))
            reduced = arr[:bits]
    else:
        reduced = pca.transform(embedding.reshape(1, -1))[0]
    # binarize by sign -> 0/1
    bits_arr = (reduced > 0).astype(int)
    # convert to hex string
    bstr = ''.join(str(x) for x in bits_arr.tolist())
    h = hex(int(bstr, 2))[2:]
    return h  # hex signature
