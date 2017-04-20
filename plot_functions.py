""" Functions to plot different sets of data from an Eyring rate model
Most data should be stored in csv files
"""

# standard libraries

# installed libraris
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.sandbox.regression.predstd import wls_prediction_std

from bs4 import BeautifulSoup


__author__ = 'Kyle Vitautas Lopin'

METHODS = ['eig', 'svd', 'qr']
COLOR_MAP = ['b', 'cyan', 'r', 'g']
SIZE_MAP = [0, 20, 0, 0]
SIZE_MAP = [4, 40, 4]

def plot_error_versus_x(num_sites, num_solutes, column_name):
    print num_sites, num_solutes

    # get the a priori data
    a_priori_filename = '{0}x{1}_np_a_priori.csv'.format(num_sites, num_solutes)
    print a_priori_filename
    a_priori_data = pd.read_csv(a_priori_filename)
    print a_priori_data.keys()
    axes = []
    for method in METHODS:
        # get the errors for each method used
        # 1. get filename
        errors_filename = method + '_{0}x{1}_np_transport_errors_rel.csv'.format(num_sites, num_solutes)
        print errors_filename
        # 2. get the data
        error_data = pd.read_csv(errors_filename)
        error_data[error_data<10**-30] = np.nan
        print error_data.keys()
        fig = plt.figure()
        axes.append(fig.add_subplot(111))
        axes[-1].set_title(method)
        axes[-1].set_xscale('log')
        axes[-1].grid(True)

        axes[-1].set_yscale('log')
        axes[-1].set_ylim([10**-20, 10**14])
        for key in error_data.keys():
            if key != 'voltage':
                print len(a_priori_data[column_name]), len(error_data[key])
                # print a_priori_data[column_name]
                # print error_data[key]
                # print 'key: ', key, key[-1]
                # print COLOR_MAP[int(key[-1])]

                axes[-1].scatter(a_priori_data[column_name], error_data[key], color=COLOR_MAP[int(key[-1])],
                                 s=SIZE_MAP[int(key[-1])])


    # plt.legend()
    plt.show()

def plot_fitted_lines(num_sites, num_solutes, column_name, log=False):
    a_priori_filename = '{0}x{1}_np_a_priori.csv'.format(num_sites, num_solutes)
    print a_priori_filename
    a_priori_data = pd.read_csv(a_priori_filename)
    print a_priori_data.keys()
    axes = []
    errors_struct = {}
    x_data = {}

    for i in range(num_sites+1):
        x_data[i] = []
    for method in METHODS:
        errors_struct[method] = {}
        for i in range(num_sites+1):
            errors_struct[method][i] = []
        errors_filename = method + '_{0}x{1}_np_transport_errors_rel.csv'.format(num_sites, num_solutes)
        # 2. get the data
        error_data = pd.read_csv(errors_filename)
        ordered_keys = sorted(error_data.keys())
        for key in ordered_keys:  # make the data structure
            if key != 'voltage':
                errors_struct[method][int(key[-1])].extend(error_data[key])
                if method == 'eig':
                    x_data[int(key[-1])].extend(a_priori_data[column_name])
        # fit the data
        a = 1
        print method
        for i in range(num_sites+1):
            x = np.array(x_data[i])
            x_fit = np.column_stack((x_data[i], np.ones(len(x_data[i]))))
            y = errors_struct[method][i]
            y_log = np.log10(y)
            x_log = np.log10(x)
            x_fit_log = np.column_stack((x_log, np.ones(len(x))))
            fig = plt.figure()
            axes.append(fig.add_subplot(111))
            axes[-1].set_title('{0} over barrier {1}'.format(method, i))
            if not log:
                axes[-1].set_xscale('log')
                axes[-1].set_yscale('log')
                axes[-1].set_ylim([10 ** -20, 10 ** 14])
            axes[-1].grid(True)

            if log:
                axes[-1].scatter(x_log, y_log, color='b', s=5)
                model = sm.OLS(y_log, x_fit_log)
            else:
                axes[-1].scatter(x, y, color='b', s=5)
                model = sm.OLS(y, x_fit)
            results = model.fit()
            print 'Fit for {0} over barrier {1}'.format(method, i)
            print results.summary()
            if log:
                fitted_values = sm.OLS(y_log, x_fit_log).fit()
                axes[-1].plot(x_log, fitted_values.fittedvalues, 'r')
            else:
                fitted_values = sm.OLS(y, x_fit).fit()
                axes[-1].plot(x, fitted_values.fittedvalues, 'r')

            prdstd, iv_l, iv_u = wls_prediction_std(fitted_values)
            if log:
                axes[-1].plot(x_log, iv_u, 'r--')
            else:
                axes[-1].plot(x, iv_u, 'r--')

            # fit the data with numpy to compare
            if log:
                m, c = np.linalg.lstsq(x_fit_log, y_log)[0]
                x = x_log
            else:
                m, c = np.linalg.lstsq(x_fit, y)[0]
            print m, c
            axes[-1].plot(x, m*x+c, 'k')

    print errors_struct
    print x_data
    plt.show()



def calc_sse(num_sites, num_solutes):
    barriers = range(num_sites+1)
    error_keys = [(x, y) for x in METHODS for y in barriers]
    all_errors = {}
    for error_key in error_keys:
        all_errors[error_key] = pd.Series()
    for method in METHODS:

        error_filename = method + '_{0}x{1}_np_transport_errors_rel.csv'.format(num_sites, num_solutes)
        error_data = pd.read_csv(error_filename)
        for key in error_data.keys():
            if key != 'voltage':
                all_errors[(method, int(key[-1]))] = all_errors[(method, int(key[-1]))].append(error_data[key])

    all_errors = pd.DataFrame(all_errors)
    all_errors_squared = all_errors**2
    print 'all: ', all_errors
    print 'squared: ', all_errors_squared
    fig, ax = plt.subplots()
    fig1, ax1 = plt.subplots()
    all_errors.boxplot(ax=ax)
    ax.set_yscale('log')
    ax.set_title('errors')
    all_errors_squared.boxplot(ax=ax1)
    ax1.set_yscale('log')
    ax1.set_title('errors squared')
    print 'mean ', all_errors.mean()
    print 'max ', all_errors.max()
    print 'mean ', all_errors_squared.mean()
    print 'max ', all_errors_squared.max()
    plt.show()


def get_errors_n_column(num_sites, num_solutes, column_name, error_type='Relative'):
    """ Get the numerical errors stored in the xxx_np_transport_errors.cvs file and the a priori data
    and export them
    :param num_sites: int - number of binding sites in model to analyze
    :param num_solutes: int - number of solutes in model to analyze
    :param column_name: string - header from a_priori file of the type of a priori data to get
    :param error_type: 'Relative' or 'Normal', which error type to return
    :return: tranport error dict with keys of the different method and values of dicts with keys
    of the barrior number and values of the errors for all the simulation runs,
    list of a priori data that is the same length as the lists in the transport error dicts
    """
    a_priori_filename = '{0}x{1}_np_a_priori.csv'.format(num_sites, num_solutes)
    a_priori_data = pd.read_csv(a_priori_filename)
    # a_priori_column_data = a_priori_data[column_name]
    a_priori_column_data = []
    errors_struct = {}
    for method in METHODS:
        errors_struct[method] = {}
        for i in range(num_sites+1):
            errors_struct[method][i] = []
        if error_type == 'Relative':
            errors_filename = method + '_{0}x{1}_np_transport_errors_rel.csv'.format(num_sites, num_solutes)
        elif error_type == 'Normal':
            errors_filename = method + '_{0}x{1}_np_transport_errors.csv'.format(num_sites, num_solutes)
        else:
            raise NotImplementedError
        # 2. get the data
        error_data = pd.read_csv(errors_filename)
        ordered_keys = sorted(error_data.keys())
        for key in ordered_keys:  # make the data structure
            if key != 'voltage':
                errors_struct[method][int(key[-1])].extend(error_data[key])
                if method == 'eig' and key[-1] == '0':  # add this the correct amount of times
                    a_priori_column_data.extend(a_priori_data[column_name])
    return errors_struct, a_priori_column_data


def plot_error_versus_x_compare(num_sites, num_solutes, column_name, barriers, methods):
    """ Plot on a single graph all the data for the number of sites 
    and solutes given for the barrier and methods given
    :param num_sites: int - number of binding sites in model to analyze
    :param num_solutes: int - number of solutes in model to analyze
    :param column_name: string - header from a_priori file of the type of a priori data to get
    :param barriers: list of barriers to put in the plot
    :param methods: list of methods to put in the plot
    """
    errors, column = get_errors_n_column(num_sites, num_solutes, column_name)
    print errors
    print column
    print len(errors['svd'][0]), len(column)
    fig = plt.figure()
    axis = fig.add_subplot(111)
    for barrier in barriers:
        for i, method in enumerate(methods):
            axis.scatter(column, errors[method][barrier],
                         label="{0} over barrier {1}".format(method, barrier), s=5,
                         color=COLOR_MAP[i])
    axis.set_ylim([10 ** -20, 10 ** 14])
    axis.set_xscale('log')
    axis.set_yscale('log')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    A_PRIORI_HEADERS = ['voltage', 'largest element', 'smallest element', 'element difference',
                        'element ratio difference', 'condition number']
    # plot_error_versus_x(2, 6, 'condition number')
    # calc_sse(2, 4)
    plot_fitted_lines(2, 6, 'condition number', log=True)
    # plot_error_versus_x_compare()
    # get_errors_n_column(2, 6, 'element ratio difference')
    # plot_error_versus_x_compare(2, 6, 'element ratio difference', [1], ['eig', 'svd', 'qr'])
    pass


