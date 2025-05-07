from itertools import product

def find_natural_number_solutions_and_print(total_sum, num_variables):
    solutions = []
    possible_values = range(0, total_sum + 2, 2)  # Each variable can be at least 1

    for combination in product(possible_values, repeat=num_variables):
        if sum(combination) == total_sum:
            solutions.append(combination)


    with open("solutions.txt", "w") as file:
        for sol in solutions:
            file.write("-".join([str(i / 10) for i in sol]) + "\n")

total_sum = 10
num_variables = 7
find_natural_number_solutions_and_print(total_sum, num_variables)
