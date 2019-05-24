# Entry point script
import os
import sys
from functools import reduce
from poweredarm.classifier import LinearClassifier
from poweredarm.data_processing import collect_from_serial
from poweredarm.train_classifier import (train_linear_classifier,
                                         evaluate_linear_classifier)
from poweredarm.util import Gesture, dated_name

def print_results(acc, recalls):
    print('Classifier predicted with accuracy of: {}'.format(acc * 100))
    print('')
    for cls, recall in enumerate(recalls):
        print('Class {} has recall of: {}'.format(cls, recall * 100))

def print_help(retcode):
    print('Usage: python -m poweredarm.main [command] [..args]')
    print('')

    print('COMMAND train')
    print('Usage: train [..data_files]')
    print('Trains a classifier using the supplied CSV data files and saves it.')
    print('')

    print('COMMAND evaluate')
    print('Usage: evaluate classifier_file [..data_files]')
    print('Loads a classifier from an existing file and evaluates ' +
          'how accurately it predicts the supplied CSV dataset.')
    print('')

    print('COMMAND header')
    print('Usage: header classifer_file')
    print('Loads a classifier from an existing file and generates ' +
          'a C header file from its parameters.')
    print('')

    print('COMMAND collect')
    print('Usage: collect [rest|open|grip|key]')
    print('Collects training EMG data for a specific gesture from the ESP32. ' +
          'Monitors serial port for 15s, collecting all received EMG data into' +
          'a CSV file for later use.')
    print('')

    print('COMMAND help')
    print('Show this help message')
    print('')
    sys.exit(retcode)

if __name__ == '__main__':
    try:
        command = sys.argv[1]
    except IndexError:
        print_help(1)

    if command == 'train':
        data_files = sys.argv[2:]
        if len(data_files) == 0:
            print("No data files detected for the 'train' option")
            sys.exit(1)

        acc, recalls = train_linear_classifier(data_files, True, True)
        print_results(acc, recalls)

    elif command == 'evaluate':
        classifier_file = sys.argv[2]
        data_files = sys.argv[3:]
        if len(data_files) == 0:
            print("No data files detected for the 'evaluate' option")
            sys.exit(1)

        acc, recalls = evaluate_linear_classifier(classifier_file, data_files)
        print_results(acc, recalls)

    elif command == 'header':
        classifier_file = sys.argv[2]
        classifier = LinearClassifier.load(classifier_file)

        header = os.path.join('out', 'classifier.h')
        if not os.path.exists('out'):
            os.mkdir('out')
        classifier.to_header(classifier_file, header)
        print('Generate header {} using classifier {}'.format(header, classifier_file))

    elif command == 'collect':
        # Needs to be one of the names in the Gesture enum
        gesture = sys.argv[2]
        label = Gesture[gesture].value
        collect_from_serial('data/dataset/{}.csv'.format(dated_name(gesture)), label)

    elif command == 'help':
        print_help(0)

    else:
        print(f"Invalid command '{command}'. Use command 'help' to show all commands")
        sys.exit(1)
