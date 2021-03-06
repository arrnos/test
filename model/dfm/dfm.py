#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@version: python3.7
@author: zhangmeng
@file: dfm.py
@time: 2019/12/06
"""


class DFM(object):

    def __init__(self, keras_input_dict, embedding_size, interaction_columns, liner_columns, dnn_reg=0.01,
                 liner_reg=0.01,
                 dnn_units=(128, 64), drop_ratio=0.5, use_liner=True, use_fm=True, use_dnn=True, seed=1024):

        self.keras_input_dict = keras_input_dict
        self.embedding_size = embedding_size
        self.interaction_columns = interaction_columns
        self.liner_columns = liner_columns
        self.dnn_reg = dnn_reg
        self.liner_reg = liner_reg
        self.dnn_units = dnn_units
        self.drop_ratio = drop_ratio
        self.use_liner = use_liner
        self.use_fm = use_fm
        self.use_dnn = use_dnn
        self.seed = seed
        self.reshaped_emb = self.get_reshaped_emb()

    def get_reshaped_emb(self):
        # flatten shape(batch_size, column_num * embedding_size)
        flatten_emb = tf.keras.layers.DenseFeatures(self.interaction_columns)(self.keras_input_dict)
        interaction_column_num = len(self.interaction_columns)
        reshaped_emb = tf.reshape(flatten_emb, (-1, interaction_column_num, self.embedding_size), "reshape_embedding")
        return reshaped_emb

    def fm_logit(self):
        # sum-square-part
        summed_val = tf.reduce_sum(self.reshaped_emb, 1)
        summed_square_val = tf.square(summed_val)

        # squre-sum-part
        squared_val = tf.square(self.reshaped_emb)
        squared_sum_val = tf.reduce_sum(squared_val, 1)

        # fm-logit
        logit = tf.reduce_sum(0.5 * tf.subtract(summed_square_val, squared_sum_val), -1)
        return logit

    def liner_logit(self):
        input = tf.keras.layers.DenseFeatures(self.liner_columns)(self.keras_input_dict)
        logit = tf.keras.layers.Dense(1, kernel_regularizer=tf.keras.regularizers.l2(self.liner_reg),
                                      use_bias=False, )(input)

        return logit

    def dnn_logit(self):
        output = tf.keras.layers.Flatten()(self.reshaped_emb)
        for unit in self.dnn_units:
            output = tf.keras.layers.Dense(unit, kernel_initializer=tf.keras.initializers.glorot_normal(seed=self.seed),
                                           kernel_regularizer=tf.keras.regularizers.l2(self.dnn_reg),
                                           use_bias=True,
                                           bias_regularizer=tf.keras.regularizers.l2(self.dnn_reg),
                                           bias_initializer='zeros')(output)
            if self.drop_ratio:
                output = tf.keras.layers.Dropout(self.drop_ratio)(output)

        logit = tf.keras.layers.Dense(1, kernel_regularizer=tf.keras.regularizers.l2(self.dnn_reg),
                                      use_bias=False)(output)

        return logit

    def build(self):
        logit_ls = []
        if self.use_dnn:
            dnn_logits = self.dnn_logit()
            logit_ls.append(dnn_logits)
        if self.use_fm:
            fm_logits = self.fm_logit()
            logit_ls.append(fm_logits)
        if self.use_liner:
            liner_logits = self.liner_logit()
            logit_ls.append(liner_logits)

        assert logit_ls
        if len(logit_ls) > 1:
            output = tf.keras.layers.add(logit_ls)
        else:
            output = logit_ls[0]

        pred = tf.keras.layers.Dense(1, activation="sigmoid")(output)

        model = tf.keras.Model(self.keras_input_dict, outputs=pred)

        return model


def train_and_test():
    train_dataset = read_csv_2_dataset(args.train_data_path, min_max_value_path, shuffle_size=10000,
                                       batch_size=args.batch_size)
    valid_dataset = read_csv_2_dataset(args.valid_data_path, min_max_value_path, batch_size=1024)
    test_dataset = read_csv_2_dataset(args.test_data_path, min_max_value_path, batch_size=1024)

    model = DFM(FEATURE_KERAS_INPUT_DICT, args.embedding_size, InteractionColumns, LinerColumns, dnn_reg=args.dnn_reg,
                liner_reg=args.liner_reg,
                dnn_units=eval(args.dnn_layers), drop_ratio=args.drop_out,
                use_liner=args.use_liner, use_fm=args.use_fm, use_dnn=args.use_dnn)
    model = model.build()
    model.summary()

    model.compile(optimizer=tf.keras.optimizers.Adam(args.learning_rate),
                  loss=tf.keras.losses.BinaryCrossentropy(),
                  metrics=[tf.keras.metrics.AUC()])
    early_stop = tf.keras.callbacks.EarlyStopping(monitor='val_auc', patience=4, mode="max")
    reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=1, min_lr=0)

    history = model.fit(train_dataset, epochs=args.epochs, callbacks=[early_stop, reduce_lr],
                        validation_data=valid_dataset,
                        class_weight={0: 1., 1: 50.})
    print("【history】")
    print(history.history)

    # print("\n【evaluate】\n")
    # print(model.evaluate(test_dataset))

    # tf.keras.models.save_model(model, "dfm_model")


if __name__ == '__main__':
    from config.file_path_config import *
    from config.feature_column_config import *
    from util.dataset_read_util import read_csv_2_dataset
    import argparse
    import time

    parser = argparse.ArgumentParser()
    parser.add_argument("-batch_size", type=int, default=512)
    parser.add_argument("-epochs", type=int, default=4)
    parser.add_argument("-drop_out", type=float, default=0.5)
    parser.add_argument("-embedding_size", type=int, default=SPARSE_EMBEDDING_SIZE)
    parser.add_argument("-learning_rate", type=float, default=0.001)
    parser.add_argument("-dnn_layers", type=str, default="128,64")
    parser.add_argument("-dnn_reg", type=float, default=0.005)
    parser.add_argument("-liner_reg", type=float, default=0.005)

    parser.add_argument("-train_data_path", type=str, default=train_csv_file)
    parser.add_argument("-valid_data_path", type=str, default=test_csv_file)
    parser.add_argument("-test_data_path", type=str, default=test_csv_file)

    parser.add_argument("-gpu_idx", type=str, default="0")

    parser.add_argument("-use_fm", type=bool, default=True)
    parser.add_argument("-use_liner", type=bool, default=True)
    parser.add_argument("-use_dnn", type=bool, default=True)

    args = parser.parse_args()
    print("\nArgument:", args, "\n")

    # 设置gup使用
    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu_idx
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            tf.config.experimental.set_virtual_device_configuration(
                gpus[0],
                [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=5120)])
            logical_gpus = tf.config.experimental.list_logical_devices('GPU')
            print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
        except RuntimeError as e:
            # Virtual devices must be set before GPUs have been initialized
            print(e)

    assert SPARSE_EMBEDDING_SIZE == BUCKTE_EMBEDDING_SIZE
    time1 = time.time()
    train_and_test()
    time2 = time.time()
    print("总耗时：%.2f min" % ((time2 - time1) / 60))
