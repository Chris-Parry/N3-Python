import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons
from scipy.optimize import curve_fit
import tkinter as tk
from tkinter import filedialog as fd

root = tk.Tk()
root.withdraw()
root.update()

plt.rcParams["text.usetex"] = True

plt.rcParams["text.latex.preamble"] = "\n".join(
    [
        r"\usepackage{siunitx}",
    ]
)

filename = fd.askopenfilename()
root.update()
root.withdraw()
root.iconify()

x_column = 1
y_column = 2
include_x_errors = True
include_y_errors = True
x_err_column = 0  # Specify the column containing the x errors
y_err_column = 3  # Specify the column containing the y errors
header = (
    False  # Does your data file contain one of more header lines (e.g. column titles)
)
head_lines = 0  # Enter the number of header lines in your data file
save_graph = True  # True if you wish to save the figure, False if not
CSV = False  # Is the data separated by commas (True if yes - e.g. a .csv file)

fig_file = "figure.png"


def fit_function(t, A0, tau, B):
    # In the brackets should be the x parameter (the dependent variable) followed by
    # the parameters of the equation to be extracted from the fit

    global args
    args = (
        fit_function.__code__.co_varnames
    )  # This extracts the names of the parameters from the function definition

    return A0 * np.exp(-t / (tau)) + B


guess = (
    1000,
    2.2,
    0,
)

fit_function(1, *guess)


if len(args) - 1 != len(guess):
    print("ERROR - mismatch between number of parameters and number of guesses")
else:
    print("This code will fit the specified function and extract")
    print(len(args) - 1, "parameters with the following inital guesses:\n")
    for i in range(len(guess)):
        print(args[i + 1], "=", guess[i])


raw_data = open(filename, "r")

lines = 0
first = True
warning = False
blank_lines = 0
num_last = None
first_row = None
last_row = None

# Skip any header lines
if header:
    for i in range(head_lines):
        next(raw_data)

# Now we loop through every line in the file
for data_line in raw_data:
    row = data_line.strip()
    # "row" is now a string variable contains the text of that line

    # check for blank lines
    if row == "":  # is it blank?
        blank_lines = blank_lines + 1  # counts the number of blank lines
        continue  # skip straight to the next line (i.e. the next step of the loop)
    elif CSV and row.strip(",") == "":  # is it just commas?
        blank_lines = blank_lines + 1  # counts the number of blank lines
        continue  # skip straight to the next line (i.e. the next step of the loop)

    # for a non-blank line, split the line into columns
    lines = lines + 1  # counts the number of lines of data
    if CSV:
        data = row.split(
            ","
        )  # split line into data points ("data" is now a list of strings)
    else:
        data = (
            row.split()
        )  # split line into data points ("data" is now a list of strings)
    num_values = len(data)

    # Checks the number of data points is the same as in the last line
    if first:  # Is it the first line? (no check possible)
        first = False  # Resets the flag
        first_row = row  # Stores the first row of data
    elif (
        num_values != num_last
    ):  # checks if number of data points is different from last row
        warning = True  # Sets a warning flag
    num_last = (
        num_values  # Stores current number of data points for the next comparison
    )
    last_row = row  # Stores the most recent (i.e. last) row of data


raw_data.close()

if warning:
    print(
        """
        \n \n WARNING
        \n WARNING - COLUMNS do not have the same number of data points
        \n WARNING\n
        """
    )
print(f"\n {lines} rows of data, in {num_last} columns, found in file")
print(
    f"\n {blank_lines} blank lines found in file, and {head_lines}"
    "lines of headers skipped"
)
print("\n First data row:", first_row)
print(" Last data row:", last_row)


raw_data = open(filename, "r")

lines = 0
for data_line in raw_data:
    lines += 1
raw_data.seek(0)

times = np.zeros(lines)

# Read the data: store all the time values in an array
i = 0
for data_line in raw_data:
    row = data_line.strip()
    data = row.split()
    times[i] = float(data[0]) / 1000
    i = i + 1
    # print(
    #     i, times[i - 1], float(data[0]) / 1000
    # )  #!Error if blank lines are at the end of the data file
print(i, "rows of data successfully stored in array")

raw_data.close()

# converts to a histogram with X (first number) bins in the range (Y,Z) microseconds
y, edges = np.histogram(times, 20, range=(0, 20))

if min(y) == 0:
    print("TOO MANY BINS, one of the bins has zero counts!!")

# converts the bin "edges" in x values that correspond to the centre of the bin
x = edges[:-1].copy()
bin_width = x[1] - x[0]
x += bin_width / 2  # the x values are now the centre of the bin

# y and x are now arrays of the histogram values (y) and times in microseconds (x).


x_error = np.zeros(len(x))
x_error.fill(bin_width / 2)  # the x errors are half the bin width
y_error = np.sqrt(y)  # the errors in y are the square root of the number of counts

# Performs a fit calling the numpy polyfit function (polynomial order 1):
# If y errors are included, they will be used as weights in the fit calculation:
if include_y_errors:  # Are y errors are included?
    para, covar = curve_fit(fit_function, x, y, p0=guess, sigma=y_error)
else:
    para, covar = curve_fit(
        fit_function, x, y, p0=guess
    )  # Performs an "unweighted" fit

# Extract the parameters from the fit:
errors = np.sqrt(np.diag(covar))  # This extracts the errors from the covariance matrix
x_fit = np.linspace(
    min(x), max(x), 1000
)  # Creates an x array to be used for drawing the fitted curve
y_fit = fit_function(x_fit, *para)

print("Para:", para)


# Plot the data and the fit
fig, ax = plt.subplots(1, 2, figsize=(16, 8))

plt.rcParams["figure.dpi"] = 150  # Sets the resolution of the figure (dots per inch)

fig.suptitle(
    "Histogram of Muon Lifetimes recorded from 21/10/22",  # ! Change date
    fontsize=16,
)

ax[0].errorbar(
    x,
    y,
    yerr=y_error,
    xerr=x_error,
    fmt="s",
    color="black",
    markersize=4,
    elinewidth=1,
    capsize=2,
    label="Data",
)

B_values = np.full(len(x_fit), para[2])

pl0_0 = ax[0].plot(x_fit, y_fit, "-", color="blue", linewidth=1, label="Fit")
pl0_1 = ax[0].plot(x_fit, B_values, "-", color="green", linewidth=1, label="Background")
pl0_2 = ax[0].plot(
    x_fit, y_fit - B_values, "-", color="red", linewidth=1, label="Signal"
)

plots0 = [pl0_0, pl0_1, pl0_2]


ax[0].axhline(y=0, linewidth=0.5, color="black")
ax[0].axvline(x=0, linewidth=0.5, color="black")

ax[0].set_ylabel("Frequency (counts)", fontsize=14)
ax[0].set_xlabel(r"Muon Lifetime (\unit{\micro\second})", fontsize=14)

ax[0].minorticks_on()
ax[0].tick_params(axis="x", labelsize=12)
ax[0].set_title("Linear graph", fontsize=14)
ax[0].legend()
ax[0].grid(
    visible=True,
    which="both",
    axis="both",
    linestyle="--",
    linewidth=0.5,
)


ax[1].errorbar(
    x,
    y,
    yerr=y_error,
    xerr=x_error,
    fmt="s",
    color="black",
    markersize=4,
    elinewidth=1,
    capsize=2,
    label="Data",
)
pl1_0 = ax[1].plot(x_fit, y_fit, "-", color="blue", linewidth=1, label="Fit")
pl1_1 = ax[1].plot(x_fit, B_values, "-", color="green", linewidth=1, label="Background")
pl1_2 = ax[1].plot(
    x_fit, y_fit - B_values, "-", color="red", linewidth=1, label="Signal"
)
ax[1].set_yscale("log")
ax[1].axhline(y=0, linewidth=0.5, color="black")
ax[1].axvline(x=0, linewidth=0.5, color="black")
ax[1].set_ylabel("ln(Frequency (counts))", fontsize=14)
ax[1].set_xlabel(r"Muon Lifetime (\unit{\micro\second})", fontsize=14)
ax[1].tick_params(axis="x", labelsize=12)
ax[1].set_title("Log graph", fontsize=14)
ax[1].legend()
ax[1].grid(
    visible=True,
    which="major",
    axis="both",
    linestyle="--",
    linewidth=0.5,
)


print("\nFit Results:\n")
for i in range(len(para)):
    print(args[i + 1], "=", para[i], "+/-", errors[i])

if save_graph:
    plt.savefig(fig_file, dpi=500)


plt.show()

# TODO Add checkboxes for different graphs
