# standard libraries
import csv
import os
# installed libraries
import mpmath as mp
# local files
import file_converter
import helper_files

__author__ = 'Kyle Vitautas Lopin'

METHODS = ['eig', 'svd', 'qr']
RUN_TYPES = ['normal', 'random1', 'random2', 'random3', 'random4', 'random5', 'random6',
             'random_medium_1', 'random_medium_2', 'random_medium_3',
             'random_small_1', 'random_small_2', 'random_small_3',
             'random_smaller_1', 'random_smaller_2', 'random_smaller_3', 'wide']


def convert_all_files(data_folder):
    """ Convert all files in the current working directory + data_folder and goes through all the directories and
    converts all files that can be converted
    """
    print 'convert all files: ', data_folder
    cwd = os.path.dirname(os.path.abspath(__file__))  # get current working directory
    _path = cwd + data_folder
    file_converter.convert_files_in_path(_path)

def get_best_np_filenames(start_of_file, working_dir):
    """ Giving the start of set of simulations file names get the best mpmath run and the np run
    :param start_of_file: start of the files, i.e. "qr_2x6_random1"
    :param working_dir: working directory
    :return: 2 file names, mpmath and then numpy
    """
    files = [x for x in os.listdir(working_dir) if x.startswith(start_of_file)]
    for _file in files:
        if 'np' in _file:
            np_file = _file
        elif 'mp' in _file:
            mp_file = _file
    return mp_file, np_file

def calc_solute_n_barrier_errors(data1, data2, num_sites, num_solutes):
    solutes = ['solute_'+str(i+1) for i in range(num_solutes)]
    errors = {'voltage': data1['voltage']}
    for solute in solutes:
        for barrier in range(num_sites+1):
            key = solute+' transport over barrier '+str(barrier)
            data1_array = data1[key]
            data2_array = data2[key]
            error_array = []
            for data_pt in data1_array-data2_array:
                error_array.append(abs(data_pt))
                # print 'error', error_array[-1]
            errors[key] = error_array
    return errors

def calc_solute_n_barrier_errors_rel(data1_best, data2, num_sites, num_solutes):
    solutes = ['solute_'+str(i+1) for i in range(num_solutes)]
    errors = {'voltage': data1_best['voltage']}
    for solute in solutes:
        for barrier in range(num_sites+1):
            key = solute+' transport over barrier '+str(barrier)
            data1_array = data1_best[key]
            data2_array = data2[key]
            error_array = []
            # get the relative solute transport rate
            norm = mp.norm(data1_best[key], 1) / 26.
            # norm = 1
            # print 'data 1: ', data1_array
            # print 'data 2: ', data2_array
            print len(data1_array), len(data2_array)
            for data_pt in data1_array-data2_array:
                error_array.append(abs(data_pt)/norm)
                # print 'error', error_array[-1]
            errors[key] = error_array
    return errors

def get_best_filename(start_of_file, working_dir):
    print 'start of file: ', start_of_file
    best_file = [x for x in os.listdir(working_dir) if x.startswith(start_of_file) and 'mp' in x]
    print best_file
    return best_file[0]

def errors_for_set(cwd, directory, simulation_type):
    """ Calculate the error for each solute and each barrier for a numpy simulation of
    an eyring rate model given the methods used
    :param directory:
    :param simulation_type:
    :return: array of errors
    """
    mp.mp.dps = 100
    start_best_filename = '_'.join(['qr', directory, simulation_type])
    best_file = get_best_filename(start_best_filename, os.path.join(cwd, directory))
    best_data = helper_files.mp_read_csv(os.path.join(cwd, directory, best_file))
    print 'best data file: ', best_file
    num_sites, num_solutes = [int(x) for x in directory.split('x')]
    all_errors = {}
    all_errors_rel = {}
    for method in METHODS:
        np_filename = '_'.join([method, directory, simulation_type, 'np']) + '.csv'
        np_file = os.path.join(cwd, directory, np_filename)
        np_data = helper_files.mp_read_csv(np_file)
        # print 'nums', num_solutes, num_sites
        # print np_filename
        error = calc_solute_n_barrier_errors(best_data, np_data, num_sites, num_solutes)
        # print sorted(error.keys())
        all_errors[method] = error

        errors_rel = calc_solute_n_barrier_errors_rel(best_data, np_data, num_sites, num_solutes)
        all_errors_rel[method] = errors_rel
    return all_errors, all_errors_rel

def make_np_error_files():
    """ Make a csv file with the errors of each solutes transport errors over each barrier
    Stack the errors for the eig, svd, and qr methods on top of each other
    :return:
    """
    print 'check'
    convert_all_files('/np_error_data')
    cwd = os.path.dirname(os.path.abspath(__file__))+'/np_error_data' # get current working directory
    print 'cwd: ', cwd
    dirs = [x for x in os.listdir(cwd) if not x.startswith('.')]
    print 'dirs', dirs
    for directory in dirs:
        working_dir = os.path.join(cwd, directory)
        print 'work dir', working_dir
        full_set_errors = {}
        full_set_errors_rel = {}
        for _run_type in RUN_TYPES:
            full_set_errors[_run_type], full_set_errors_rel[_run_type] = errors_for_set(cwd, directory, _run_type)
            run_type_list = sorted(full_set_errors.keys())
            print 'hello: ', sorted(full_set_errors.keys())
            # for key in full_set_errors.keys():
            #     print 'checker: ', full_set_errors[key].keys()
        for method in METHODS:
            error_file_name_rel = '_'.join([method, directory, 'np_transport_errors_rel']) + '.csv'
            error_file_name = '_'.join([method, directory, 'np_transport_errors']) + '.csv'
            print 'error_file_name', error_file_name
            make_method_error_file(method, error_file_name, full_set_errors)
            make_method_error_file(method, error_file_name_rel, full_set_errors_rel)

def make_method_error_file(method, filename, data):
    print 'filename: ', filename, method
    print 'keys: ', data.keys()
    ordered_keys = sorted(data['wide']['qr'].keys())

    ordered_keys.insert(0, 'voltage')
    ordered_keys.pop()
    print 'ordered keys: ', ordered_keys
    with open(filename, 'w') as _file:
        file_writer = csv.writer(_file)
        # put first row of the np_errors file to be which solute and barrier each error is for
        file_writer.writerow(ordered_keys)

        for run_key in sorted(data.keys()):  # go through each type of run, wide, random etc
            print data[run_key].keys()
            print 'data to get is : ', data[run_key][method].keys()
            print 'keyyy: ', run_key, ordered_keys
            # make a row of data and add it
            data_to_add = data[run_key][method]
            for i in range(len(data_to_add['voltage'])):  # for each row in the data save it to new row
                new_row = []
                for solute_key in ordered_keys:
                    new_row.append(data_to_add[solute_key][i])
                # add the new row
                file_writer.writerow(new_row)
    _file.close()


            # print 'check: ', data[run_key][method]['voltage']


            # for i in range(len(data[run_key][method]['voltage'])):
                # print 'i = ', i, data[run_key][method]['voltage'][i], run_key, method



make_np_error_files()