#include "classifier.h"

static float classifier_weight[CLASSIFIER_NUM_FEATURES + 1][CLASSIFIER_NUM_CLASSES] =\
    CLASSIFIER_WEIGHT;

static float classifier_offset[CLASSIFIER_NUM_FEATURES] = CLASSIFIER_OFFSET;

static float classifier_divisor[CLASSIFIER_NUM_FEATURES] = CLASSIFIER_DIVISOR;
