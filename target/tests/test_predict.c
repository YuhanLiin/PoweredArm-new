#include <stdio.h>
#include <math.h>
#include "classifier.h"
#include "predict.h"

void _close_enough(
    const float arr1[],
    const float arr2[],
    size_t size,
    float tol,
    int line)
{
    for (size_t i = 0; i < size; i++) {
        float a = arr1[i];
        float b = arr2[i];
        float diff = fabs(a - b);

        if (diff > tol || -diff < -tol) {
            printf("arr1[%zd]=%f not close enough to arr2[%zd]=%f on line %d!\n",
                   i, a, i, b, line);
        }
    }
}

#define close_enough(arr1, arr2, size, tol)\
    _close_enough(arr1, arr2, size, tol, __LINE__)

static void test_scaling()
{
    float features[CLASSIFIER_NUM_FEATURES] = {1, 10, 88, 3};
    float offset[CLASSIFIER_NUM_FEATURES] = {3, 4, 22, 7};
    float divisor[CLASSIFIER_NUM_FEATURES] = {2, 3, 10, 9};

    float expected[CLASSIFIER_NUM_FEATURES] = {-1, 2, 6.6, -4/9.};
    scale_features(features, offset, divisor);
    close_enough(expected, features, CLASSIFIER_NUM_FEATURES, 0.001);
}

static void test_compute_best_class()
{
    float weight[CLASSIFIER_NUM_FEATURES + 1][CLASSIFIER_NUM_CLASSES] = {
        {400, 0},
        {20, 4},
        {2, 4},
        {1, 5},
        {4, 4}
    };

    float features1[] = {0, 0, -1, 0};
    float features2[] = {-20, 17, 12, 1};
    float features3[] = {0, 10, 10, 7000};
    float features4[] = {1, 0, 105, 3};
    float expected_results[] = {0, 1, 0, 1};

    float results[] = {
        compute_best_class(features1, weight),
        compute_best_class(features2, weight),
        compute_best_class(features3, weight),
        compute_best_class(features4, weight),
    };

    close_enough(results, expected_results, sizeof(results)/sizeof(float), 0.00001);
}

int main() {
    printf("Tests start!\n");
    test_scaling();
    test_compute_best_class();
    printf("Tests end!\n");
}
