#include <stddef.h>
#include "classifier.h"
#include "predict.h"

static float classifier_weight[CLASSIFIER_NUM_FEATURES + 1][CLASSIFIER_NUM_CLASSES] =\
    CLASSIFIER_WEIGHT;

static float classifier_offset[CLASSIFIER_NUM_FEATURES] = CLASSIFIER_OFFSET;

static float classifier_divisor[CLASSIFIER_NUM_FEATURES] = CLASSIFIER_DIVISOR;


void scale_features(float features[], const float offset[], const float divisor[])
{
    // Assume all 3 params are NUM_FEATURES long
    for (size_t i = 0; i < CLASSIFIER_NUM_FEATURES; i++) {
        features[i] = (features[i] - offset[i]) / divisor[i];
    }
}

int compute_best_class(float features[], const float weight[][CLASSIFIER_NUM_CLASSES])
{
    float best_prob = 0;
    // -1 means no class has been computed yet
    int best_class = -1;

    for (size_t cls = 0; cls < CLASSIFIER_NUM_CLASSES; cls++) {
        float prob = weight[0][cls];
        for (size_t f = 1; f < CLASSIFIER_NUM_FEATURES + 1; f++) {
            prob += weight[f][cls] * features[f - 1];
        }

        if (best_class == -1 || prob > best_prob) {
            best_class = cls;
            best_prob = prob;
        }
    }

    return best_class;
}

int classify(float features[])
{
    scale_features(features, classifier_offset, classifier_divisor);
    return compute_best_class(features, classifier_weight);
}
