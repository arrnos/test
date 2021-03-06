#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@version: python3.7
@author: zhangmeng
@file: cate_values_util.py
@time: 2019/12/02
"""

import pickle
from codecs import open

import numpy as np

from config.deep_feature_config import *
from config.file_path_config import *


def dump_min_max_values_2_file(csv_file, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    rs_dict = {}
    for f in CONTINUOUS_FEATURE_ALL_LIST:
        rs_dict[f] = [np.inf, -np.inf, 0, 0, 0]

    with open(csv_file, "r", "utf-8") as fin:
        for i, line in enumerate(fin):
            arr = line.strip().split(",")
            features = dict(zip(FEATURE_NAMES, arr))
            for f in CONTINUOUS_FEATURE_ALL_LIST:
                # 每种特征，统计其每种特征值的出现的最小值和最大值
                f_value = features[f]
                if not f_value:
                    continue
                f_value = float(f_value)
                rs_dict[f][0] = min(rs_dict[f][0], f_value)
                rs_dict[f][1] = max(rs_dict[f][1], f_value)
                rs_dict[f][3] += f_value
                rs_dict[f][4] += 1

            if i > 0 and i % 5000 == 0:
                print("line:", i)
    # 求均值
    for k in rs_dict.keys():
        min_, max_, mean_, sum_, cnt_ = rs_dict[k]
        mean_ = sum_ / cnt_ if cnt_ else 0
        rs_dict[k][2] = mean_

    pickle.dump(rs_dict, open(out_path, "wb"))

    print(rs_dict)

    print("min max value dict dump completed!", out_path)


def fix_min_max_value_dict_from_file(min_max_value_save_path):
    assert os.path.exists(min_max_value_save_path)
    save_dict = pickle.load(open(min_max_value_save_path, "rb"))
    fixed_dict = {}
    for key, (min_value, max_value, mean_value, sum_value, cnt_value) in save_dict.items():
        if "opp_distribution_saturation" in key:  # 最大值设置为1
            fixed_dict[key] = (min_value, 1.0, mean_value, sum_value, cnt_value)
        else:
            fixed_dict[key] = (min_value, max_value, mean_value, sum_value, cnt_value)
    pickle.dump(fixed_dict, open(min_max_value_save_path, "wb"))

    print(fixed_dict)
    print("min max value dict fix completed!", min_max_value_save_path)


def load_min_max_value_dict_from_file(min_max_value_save_path):
    assert os.path.exists(min_max_value_save_path)
    save_dict = pickle.load(open(min_max_value_save_path, "rb"))
    min_max_dict = {}
    for key, (min_value, max_value, mean_value, _, _) in save_dict.items():
        min_max_dict[key] = (min_value, max_value)
    return min_max_dict


def prepare_log_min_max_dict(min_max_dict):
    log_config_dict = {}
    for feature, (min_value, max_value) in min_max_dict.items():
        log_config_dict[feature] = (np.log1p(min_value), np.log1p(max_value))
    return log_config_dict


if __name__ == '__main__':
    dump_min_max_values_2_file(train_csv_file, min_max_value_path)
    fix_min_max_value_dict_from_file(min_max_value_path)

    print(load_min_max_value_dict_from_file(min_max_value_path))
