import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


filename = "sifted22-10-18-16-52.txt"  # This is the name of the file to be read

xColumn = 1  # Specify the column containing the x data points
yColumn = 2  # Specify the column containing the y data points
include_x_errors = True  # Enter True or False only (True if x errors needed on plot)
include_y_errors = True  # Enter True or False only (True if y errors needed on plot)
xErrColumn = 0  # Specify the column containing the x errors
yErrColumn = 3  # Specify the column containing the y errors
header = (
    False  # Does your data file contain one of more header lines (e.g. column titles)
)
head_lines = 0  # Enter the number of header lines in your data file
save_graph = True  # Enter True or False only (True if you wish to save the figure)
CSV = False  # Is the data separated by commas (True if yes - e.g. a .csv file)

fig_file = "figure.png"


def fit_function(t, A0, tau, B, C, D):
    # In the brackets should be the x parameter (the dependent variable) followed by
    # the parameters of the equation to be extracted from the fit

    global args  # This is needed to allow the function to access the global variable args
    args = (
        fit_function.__code__.co_varnames
    )  # This extracts the names of the parameters from the function definition

    return (
        A0 * np.exp(-t / (tau)) + B + (C * t) + (D * t**2)
    )  # This is the equation to be fitted to the data


guess = (
    1000,
    2.2,
    0,
    0,
    0,
)  # This is the initial guess for the parameters of the fit function

fit_function(
    1, *guess
)  # This is needed to extract the names of the parameters from the function definition


if len(args) - 1 != len(
    guess
):  # Checks the number of parameters and the number of guesses
    print("ERROR - mismatch between number of parameters and number of guesses")
else:
    print("This code will fit the specified function and extract")
    print(len(args) - 1, "parameters with the following inital guesses:\n")
    for i in range(len(guess)):  # For each parameter....
        print(
            args[i + 1], "=", guess[i]  # Prints the name of the parameter and its guess
        )


raw_data = open(filename, "r")
lines = 0

i = 0
for data_line in raw_data:
    lines += 1  # Count the number of lines in the file
raw_data.seek(0)
# print(lines)

# Create an array to store all the time values
times = np.zeros(lines)

# Read the data: store all the time values in an array
for data_line in raw_data:
    row = data_line.strip()
    data = row.split()
    times[i] = float(data[0]) / 1000
    i = i + 1
    # print(i,times[i-1],float(data[0])/1000)        #!Error will appear about index out of range if blank lines are at the end of the data file
print(i, "rows of data successfully stored in array")
raw_data.close()

# converts to a histogram with X (first number) bins in the range (Y,Z) microseconds
y, edges = np.histogram(times, 20, range=(0, 20))

if min(y) == 0:
    print("TOO MANY BINS, one of the bins has zero counts!!")

# converts the bin "edges" in x values that correspond to the centre of the bin
x = edges[:-1].copy()
binWidth = x[1] - x[0]  # the width of the bins
x += binWidth / 2  # the x values are now the centre of the bin

# y and x are now arrays of the histogram values (y) and times in microseconds (x). This can now be plotted.


xError = np.zeros(len(x))
xError.fill(binWidth / 2)  # the x errors are half the bin width
yError = np.sqrt(y)  # the errors in y are the square root of the number of counts

# Performs a fit calling the numpy polyfit function (polynomial order 1):

# If y errors are included, they will be used as weights in the fit calculation:

if include_y_errors:  # Are y errors are included?
    para, covar = curve_fit(fit_function, x, y, p0=guess, sigma=yError)
else:
    para, covar = curve_fit(
        fit_function, x, y, p0=guess
    )  # Performs an "unweighted" fit

# Extract the parameters from the fit:

errors = np.sqrt(np.diag(covar))  # This extracts the errors from the covariance matrix

x_fit = np.linspace(
    min(x), max(x), 1000
)  # Creates an x array to be used for drawing the fitted curve
y_fit = fit_function(x_fit, *para)  # Creates a y array containing the fitted curve

print("Para:", para)

plt.rcParams[
    "figure.dpi"
] = 150  # Controls the size and resolution of the figures as displayed in Jupyter

plt.errorbar(
    x,
    y,
    yerr=yError,
    xerr=xError,
    fmt="s",
    color="black",
    markersize=4,
    elinewidth=1,
    capsize=2,
    label="data",
)
plt.plot(x_fit, y_fit, "-", color="blue", linewidth=1, label="linear fit")

# plt.xlim(0,2.5)
# plt.ylim(0,25)
plt.xlabel("X-Axis Label (units)", fontsize=14)
plt.ylabel("Y-Axis Label (units)", fontsize=14)
plt.title("This is a title", fontsize=16, loc="center")
# plt.minorticks_on()
# plt.text(7.5,95,"Here is some text on the graph",color='red',fontsize=10,weight="normal",fontstyle="italic")
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.legend()
# plt.grid(True)

if save_graph:
    plt.savefig(fig_file, dpi=500)

plt.show()

print("\nFit Results:\n")
for i in range(len(para)):
    print(args[i + 1], "=", para[i], "+/-", errors[i])
