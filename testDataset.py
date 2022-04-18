# https://www.youtube.com/watch?v=NoKvCREx36Q
import pickle
from tensorflow.keras import layers
from tensorflow import keras
import tensorflow_datasets as tfds
import pandas as pd
import tensorflow as tf
import os
from keras.models import load_model
from posixpath import split
import numpy as np
os.environ["TF_CPP_MIN_LOG_LEVEL"] = '2'

ds_train = tf.data.TextLineDataset("emotions_train.csv")
ds_test = tf.data.TextLineDataset("emotions_test.csv")

# print(ds_test.shape())
for element in ds_test:
    print(element)


def filter_train(line):
    split_line = tf.strings.split(line, ",", maxsplit=1)
    sentiment_category = split_line[1]

    return (
        True
        if sentiment_category != None
        else False
    )

# for line in ds_train.skip(1).take(5):
#     print(tf.strings.split(line, ",", maxsplit=2))


tokenizer = tfds.deprecated.text.Tokenizer()


def build_vocabulary(ds_train, threshold=10):
    """ Build a vocabulary """
    frequencies = {}
    vocabulary = set()
    vocabulary.update(["sostoken"])
    vocabulary.update(["eostoken"])

    for line in ds_train.skip(1):
        split_line = tf.strings.split(line, ",", maxsplit=2)
        review = split_line[2]
        tokenized_text = tokenizer.tokenize(review.numpy().lower())

        for word in tokenized_text:
            if word not in frequencies:
                frequencies[word] = 1
            else:
                frequencies[word] += 1

            # if we've reached the threshold
            if frequencies[word] == threshold:
                vocabulary.update(tokenized_text)

    return vocabulary


# Build vocabulary and save it to vocabulary.obj
vocabulary = build_vocabulary(ds_train)
vocab_file = open("vocabulary.obj", "wb")
pickle.dump(vocabulary, vocab_file)

# Loading the vocabulary
# vocab_file = open("vocabulary.obj", "rb")
# vocabulary = pickle.load(vocab_file)

encoder = tfds.deprecated.text.TokenTextEncoder(
    list(vocabulary), oov_token="<UNK>", lowercase=True, tokenizer=tokenizer,
)


def my_encoder(text_tensor, label):
    print(text_tensor)
    encoded_text = encoder.encode(text_tensor.numpy())
    print(encoded_text)
    return encoded_text, label


def encode_map_fn(line):
    split_line = tf.strings.split(line, ",", maxsplit=4)
    label_str = split_line[1]  # neg, pos
    review = "sostoken " + split_line[2] + " eostoken"
    label = 0

    # print("REVIEW")
    # print(review)

    if label_str == "joy":
        label = 0
    elif label_str == "sadness":
        label = 1
    elif label_str == "fear":
        label = 2
    elif label_str == "anger":
        label = 3

    (encoded_text, label) = tf.py_function(
        my_encoder, inp=[review, label], Tout=(tf.int64, tf.int32),
    )

    encoded_text.set_shape([None])
    label.set_shape([])
    # print(encoded_text)
    return encoded_text, label


AUTOTUNE = tf.data.experimental.AUTOTUNE
# ds_train = ds_train.map(encode_map_fn, num_parallel_calls=AUTOTUNE).cache()
# ds_train = ds_train.shuffle(25000)
# ds_train = ds_train.padded_batch(32, padded_shapes=([None], ()))

ds_test = ds_test.map(encode_map_fn)
# print(ds_test)

print("\nAfter encoding:")
for element in ds_test:
    print(element)

print("\nAfter Loop")
ds_test = ds_test.padded_batch(32, padded_shapes=([None], ()))

# model = keras.Sequential(
#     [
#         layers.Masking(mask_value=0),
#         layers.Embedding(input_dim=len(vocabulary) + 2, output_dim=32,),
#         layers.GlobalAveragePooling1D(),
#         layers.Dense(64, activation="relu"),
#         layers.Dense(4, activation="softmax"),
#     ]
# )

# model.compile(
#     loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
#     optimizer=keras.optimizers.Adam(3e-4, clipnorm=1),
#     metrics=["accuracy"],
# )

# model.fit(ds_train, epochs=800, verbose=2)
# model.evaluate(ds_test)

# model.save("my_model.h5")

model = load_model("my_model.h5")

print("\n\n\nMy Test:")

testStr = "sostoken  text eostoken"
ds_test = tf.convert_to_tensor(testStr, dtype=tf.string)
# ds_test = [tf.constant(testStr)]
# ds_test = np.array(ds_test)

# print(ds_test)
# func = np.vectorize(lambda x: encode_map_fn(x))
# func(ds_test)
# encode_map_fn(ds_test)
# ds_test = tf.convert_to_tensor(encoder.encode(ds_test.numpy()), tf.int64)
label = 1
(encoded_text, label) = tf.py_function(
    my_encoder, inp=[ds_test, label], Tout=(tf.int64, tf.int32),
)
print((encoded_text, tf.constant(0)))

# ds_test = ds_test.map(encode_map_fn, num_parallel_calls=AUTOTUNE).cache()
# yfit = model(encoded_text)
# print(yfit.numpy())

q = model.predict(np.array(["lovely evening", ]))

'''

'''
