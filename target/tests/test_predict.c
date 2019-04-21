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
    float features[CLASSIFIER_NUM_FEATURES] = {1, 10, 88, 3, 9, 5, 11, 1};
    float offset[CLASSIFIER_NUM_FEATURES] = {3, 4, 22, 7, 0, 4, 5, 10};
    float divisor[CLASSIFIER_NUM_FEATURES] = {2, 3, 10, 9, 1, 3, 7, 9};

    float expected[CLASSIFIER_NUM_FEATURES] = {-1, 2, 6.6, -4/9., 9., 1/3., 6/7., -1};
    scale_features(features, offset, divisor);
    close_enough(expected, features, CLASSIFIER_NUM_FEATURES, 0.001);
}

int main() {
    printf("Tests start!\n");
    test_scaling();
    printf("Tests end!\n");
}
