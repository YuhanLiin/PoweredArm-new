#include "classifier.h"

// Apply feature scaling. All 3 input arrays must be of length NUM_FEATURES
void scale_features(float features[], const float offset[], const float divisor[]);

// Returns output class with the highest probability given the scaled features
// and the weight matrix
int compute_best_class(float features[], const float weight[][CLASSIFIER_NUM_CLASSES]);

// Classify unscaled features using the 2 methods above
int classify(float features[]);
