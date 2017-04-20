# standard librarieszW
import csv
import logging
import os
# installed libraries
import mpmath as mp
import pandas as pd
# local files
import file_converter
import helper_files

__author__ = 'Kyle Vitautas Lopin'

METHODS = ['eig', 'svd', 'qr']
RUN_TYPES = ['normal', 'random1', 'random2', 'random3', 'random4', 'random5', 'random6',
             'random_medium_1', 'random_medium_2', 'random_medium_3',
             'random_small_1', 'random_small_2', 'random_small_3',
             'random_smaller_1', 'random_smaller_2', 'random_smaller_3', 'wide']

A_PRIORI_HEADERS = ['voltage', 'largest element', 'smallest element', 'element difference',
                    'element ratio difference', 'condition number']

DATA_FOLDER = '/np_error_data'

def get_a_priori_data(filename, columns, data={}):
    new_data = pd.read_csv(filename)
    # print new_data.keys()
    print 'filename: ', filename
    for column in columns:
        # print new_data[column]
        if column in data:
            # if column == 'condition number':
            #     print 'has data', type(data['condition number'])
            #     print 'data in: ', data['condition number']
            #     print 'new data is: ', new_data[column]
            data[column] = data[column].append(new_data[column], ignore_index=True)
            # if column == 'condition number':
            #     print 'data in2b: ', data['condition number']
        else:
            data[column] = new_data[column]
    # print 'keys: ', data.keys()
    # print 'data:: ', data['condition number']
    # print 'len get data: ', len(data['condition number'])
    return data


def make_a_priori_file(filename, directory, cwd):
    print 'a priori filename: ', filename, directory
    data = {}
    for run_type in RUN_TYPES:
        # data[run_type] = {}
        np_file_name = '_'.join(['qr', directory, run_type, 'np'])+'.csv'
        # get the data
        print np_file_name
        file_n_path = os.path.join(cwd, directory, np_file_name)
        data = get_a_priori_data(file_n_path, A_PRIORI_HEADERS, data)
    write_file(filename, data, A_PRIORI_HEADERS)


def make_a_priori_files():
    """ Make a file saving all the a priori data for every simulation run found in the current
    working directory.
    This goes through all the numpy files and looks at the qr simulation runs and saves all the
    headers listed in A_PRIORI_HEADERS and makes a new file with just those headers in a file with
    the name {0}x{1}_np_a_priori.csv.format(num sites, num solutes)
    :return:
    """
    cwd = os.path.dirname(os.path.abspath(__file__))+DATA_FOLDER # get current working directory
    print 'cwd: ', cwd
    dirs = [x for x in os.listdir(cwd) if not x.startswith('.')]
    print 'dirs', dirs
    for directory in dirs:
        working_dir = os.path.join(cwd, directory)
        print working_dir
        a_priori_file_name = '_'.join([directory, 'np_a_priori']) + '.csv'
        make_a_priori_file(a_priori_file_name, directory, cwd)


def write_file(filename, data, ordered_keys):
    """ Take in data and write it to a file in the order of the keys given
    :param filename: string of what to call the file being made
    :param data: data to save
    :param ordered_keys: keys in the order to be added
    """
    print 'writing file'
    print 'data keys: ', data.keys()
    with open(filename, 'w') as _file:
        file_writer = csv.writer(_file)
        file_writer.writerow(ordered_keys)
        for i in range(len(data['voltage'])):  # for each row in the data save it to new row
            new_row = []
            for key in ordered_keys:
                new_row.append(data[key][i])
            # add the new row
            file_writer.writerow(new_row)
    _file.close()


if __name__ == '__main__':
    make_a_priori_files()