import os
import re


def find_path(directory):
    match = re.search(directory, os.getcwd())
    if not match:
        raise IOError('{} is not in current working directory of {}'.format(directory, os.getcwd()))
    return os.getcwd()[:match.span()[0]] + directory


def accuracy(acc, file):
    writer = open(file + '.acc', 'w')
    # New sorted acc
    sorted_acc = {}
    # Store correct and incorrect results
    acc_total = [0, 0]

    # Store labels and sort them
    for label in acc.keys():
        values = []
        for key in acc[label]:
            if key == label or key == '<correct>' or key == 'standard':
                acc_total[0] += acc[label][key]
            else:
                acc_total[1] += acc[label][key]
            values.append((key, acc[label][key]))
        values = sorted(values, key=lambda x:x[1], reverse=True)
        sorted_acc[label] = values

    # Print out accuracy results
    try:
        accuracy = acc_total[0]/(float(acc_total[0]+acc_total[1]))
    except:
        accuracy = 0.0
    writer.write('Accuracy: ' + str(accuracy) + '\n\n')

    # Process for each label
    for label in sorted(sorted_acc.keys()):
        writer.write(str(label) + '\n')
        for value in sorted_acc[label]:
            writer.write('\t{0:20s}\t{1:8d}'.format(value[0], value[1]) + '\n')
        writer.write('\n')
    writer.close()
    return True


# Function to combined weighted dictionaries
def combine_weight(D, weights):
    final = {}
    for method in weights:
        if method in D:
            for entry in D[method]:
                final[entry] = final.get(entry, 0) + (D[method][entry] * weights[method])
    return final


# Function to select maximum value in a dictionary
def max_value(D, tie=False):
    max_value = ('', 0)
    for key in D:
        if D[key] > max_value[1]:
            max_value = (key, D[key])
        elif tie:
            if key == tie:
                if D[key] == max_value[1]:
                    max_value = (key, D[key])
    return max_value


# Function to convert a dictionary's values to probabilities
def prob_conversion(D, retotal=False):
    if not isinstance(D, dict):
        raise TypeError('Data structure is not a dictionary')
    probD = {}
    total = 0.0
    # Add every value in the dictionary to a total variable
    for key in D:
        total += float(D[key])
    # For each value, divide by total for the probability conversion
    for key in D:
        try:
            probD[key] = float(D[key])/total
        except ZeroDivisionError:
            probD[key] = 0.0
    # Return only probD if retotal is False
    if retotal == False:
        return probD
    elif retotal == True:
        return probD, total

def levenshtein(a, b):
    """This function applies the levenshtein algorithm between an
    the object's gloss and a leipzig or gold tag.
    """
    # Reset to calculate whereas b has greater length
    if len(a) < len(b):
        return levenshtein(b, a)
    # If b has length of 0 return length of a
    if len(b) == 0:
        return len(a)
    previous_row = range(len(b) + 1)
    for i, c1 in enumerate(a):
        current_row = [i + 1]
        for j, c2 in enumerate(b):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]
