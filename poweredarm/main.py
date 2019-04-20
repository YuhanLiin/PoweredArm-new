# Entry point script
import sys
import glob
from functools import reduce
from poweredarm.train_classifier import (train_linear_classifier,
                                         evaluate_linear_classifier)

def glob_args(start):
    return reduce(lambda a, b: a + b, [glob.glob(f) for f in sys.argv[start:]], [])

def print_results(acc, recalls):
    print('Classifier predicted with accuracy of: {}'.format(acc * 100))
    print('')
    for cls, recall in enumerate(recalls):
        print('Class {} has recall of: {}'.format(cls, recall))

if __name__ == '__main__':
    command = sys.argv[1]

    if command == 'train':
        data_files = glob_args(2)
        if len(data_files) == 0:
            print("No data files detected for the 'train' option")
            sys.exit(1)

        acc, recalls = train_linear_classifier(data_files, True, True)
        print_results(acc, recalls)

    elif command == 'evaluate':
        classifer_file = glob.glob(sys.argv[2])[0]
        data_files = glob_args(3)
        if len(data_files) == 0:
            print("No data files detected for the 'evaluate' option")
            sys.exit(1)

        acc, recalls = evaluate_linear_classifier(classifer_file, data_files)
        print_results(acc, recalls)

    elif command == 'help':
        print('Usage: python -m poweredarm.main [command] [..args]')
        print('')

        print('COMMAND train')
        print('Usage: train [..data_files]')
        print('Trains a classifier using the supplied CSV data files and saves it.')
        print('')

        print('COMMAND evaluate')
        print('Usage: train classifier_file [..data_files]')
        print('Loads a classifier from an existing file and evaluates ' +
              'how accurately it predicts the supplied CSV dataset.')
        print('')

        print('COMMAND help')
        print('Show this help message')
        print('')

    else:
        print(f"Invalid command '{command}'. Use command 'help' to show all commands")
        sys.exit(1)
