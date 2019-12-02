# -*- coding: utf-8 -*-

"""
@author: zhangmeng
@file: deep_feature_config.py
@time: 2019/12/10 17:17
"""

import tensorflow as tf

FEATURE_INFOS = [
    ["account_age", int, 0],
    ["alignment_day", str, None],
    ["alignment_day_of_week", str, None],
    ["alignment_hour", str, None],
    ["alignment_month", str, None],
    ["alignment_year", str, None],
    ["all_call_num", int, 0],
    ["avgerage_waiting_time_of_dialogue", float, 0],
    ["consult_type", str, None],
    ["contain_education_or_promotion_key_word_in_dialogue", str, None],
    ["contain_price_key_word_in_dialogue", str, None],
    ["create_user", str, None],
    ["delta_days_from_entryDate", int, 0],
    ["delta_time_of_create_time_and_operator_time", float, 0],
    ["dialogue_start_at", str, None],
    ["duration_of_dialogue", float, 0],
    ["educationalBackground", str, None],
    ["first_proj_id", str, None],
    ["gender", str, None],
    ["graduateSchool", str, None],
    ["major", str, None],
    ["marriageState", str, None],
    ["message_opp_distribution_num", int, 0],
    ["message_opp_distribution_saturation", float, 0],
    ["message_opp_limit_num", int, 0],
    ["nationalEdu", str, None],
    ["number_of_dialogue", int, 0],
    ["number_of_student_dialogue", int, 0],
    ["online_opp_distribution_num", int, 0],
    ["online_opp_distribution_saturation", float, 0],
    ["online_opp_limit_num", int, 0],
    ["opp_completed_rate", float, 0],
    ["opp_following_num", int, 0],
    ["opp_today_following_num", int, 0],
    ["oppor_source", str, None],
    ["pastNday_advertiser_applied_ratio", float, 0],
    ["pastNday_advertiser_distribution_num", int, 0],
    ["pastNday_advertiser_order_num", int, 0],
    ["pastNday_applied_ratio_on_siteId", float, 0],
    ["pastNday_distribution_num_on_siteId", int, 0],
    ["pastNday_order_num_on_siteId", int, 0],
    ["past_n_days_acc_alignment_num", int, 0],
    ["past_n_days_acc_order_amount", int, 0],
    ["past_n_days_acc_order_avg_amount", int, 0],
    ["past_n_days_acc_order_num", int, 0],
    ["past_n_days_acc_order_rate", float, 0],
    ["posLevel", str, None],
    ["promotion_type", str, None],
    ["quantum_id", str, None],
    ["race", str, None],
    ["recycle_opp_distribution_num", int, 0],
    ["recycle_opp_distribution_saturation", float, 0],
    ["recycle_opp_limit_num", int, 0],
    ["residenceType", str, None],
    ["site_source", str, None],
    ["student_cellphone_midnum", str, None],
    ["student_dialogue_fenci", str, None],
    ["timedelta_from", str, None],
    ["today_unfollowed_num", int, 0],
    ["twice_consult", str, None],
    ["valid_call_num", int, 0],
]


def parse_feature_config():
    feature_name_list = []
    feature_dtype_list = []
    feature_default_list = []
    feature_keras_input_dict = {}
    for arr in FEATURE_INFOS:
        f_name, dtype, default = arr

        feature_name_list.append(f_name)
        feature_dtype_list.append(dtype)
        if dtype == str:
            feature_keras_input_dict[f_name] = tf.keras.Input(name=f_name, shape=(1,), dtype=tf.string)
            feature_default_list.append(str(default))
        elif dtype == int:
            feature_keras_input_dict[f_name] = tf.keras.Input(name=f_name, shape=(1,), dtype=tf.int64)
            feature_default_list.append(int(default))
        elif dtype == float:
            feature_keras_input_dict[f_name] = tf.keras.Input(name=f_name, shape=(1,), dtype=tf.float32)
            feature_default_list.append(float(default))
    return feature_name_list, feature_dtype_list, feature_default_list, feature_keras_input_dict


FEATURE_NAMES, FEATURE_DTYPES, FEATURE_DEFAULTS, FEATURE_KERAS_INPUT_DICT = parse_feature_config()

if __name__ == '__main__':
    for i in [FEATURE_NAMES, FEATURE_DTYPES, FEATURE_DEFAULTS, FEATURE_KERAS_INPUT_DICT]:
        print(i)
