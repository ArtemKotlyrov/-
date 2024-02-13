from functools import reduce
from random import randint, random, sample
import math


import numpy as np

from numba import jit, prange, njit

######### "Oops, I accidently achieved state of the art results" #########
######### a fast Traveling Salesman Problem solver in Numpy and Numba. #########





# 3000 cities, with a specific seed for reproducability
# cities = np.random.RandomState(22).rand(3000, 2)
def PrepareText(line: str, Nmax=27):
    N = Nmax
    n, text = 0, ''
    for w in line.split():
        n += len(w)+1
        if n > N:
            text += '\n'+w+' '
            n = len(w)+1
        else:
            text += w+' '
    text += '\n#'

    cities = np.array([ (round(x*6/0.155), round(-y*10/0.155)) for y, line in enumerate(text.split("\n")) for x, ch in enumerate(line.rstrip()) if ch.strip()])
    recalc = np.array([ (round(x*6/0.155), round(-y*10/0.155)) for y, line in enumerate(text.split("\n")) for x, ch in enumerate(line.rstrip()) if ch.strip()])
    char = np.array([ ch for y, line in enumerate(text.split("\n")) for x, ch in enumerate(line.rstrip()) if ch.strip()])
    char[-1] = ""
    return cities, recalc, char
#cities = np.array([[17, 19], [2, 2], [8,8], [12, 14], [1, 1]])
# print(cities)


@njit(fastmath=True, parallel=False, cache=True)
def compute_path_travel_distance(cities):
    distance = 0
    for i in prange(0, len(cities) - 1):  # "parallel programming is hard"
        # distance += math.sqrt(((cities[i]-cities[i+1])**2).sum())  # euclidean distance
        distance += np.abs(cities[i]-cities[i+1]).sum()  # path distance
        # D = cities[i]-cities[i+1]
        # A = D[0]+D[1]
        # B = D[0]-D[1]
        # distance += max(abs(A), abs(B))  # path distance
    return distance
    # return reduce(lambda x, y: np.linalg.norm(x-y), cities)

# print(compute_path_travel_distance(cities))


@njit(fastmath=True, cache=True)
def reverse_random_sublist(lst):
    cities = lst

    # I read online that this was much better than a random permutation for getting convergence
    new_list = lst.copy()
    cities_len = len(cities)-1
    start = randint(1, cities_len-1)
    end = randint(start, cities_len-1)
    new_list[start:end+1] = new_list[start:end+1][::-1]
    return new_list


@njit(cache=True)
def random_permutation(iterable, r=None):
    pool = tuple(iterable)
    r = len(pool) if r is None else r
    return list(sample(pool, r))


@njit(fastmath=True, cache=True)
def acceptance_probability(old_cost, new_cost, temperature):
    res = math.exp((old_cost - new_cost) / temperature)
    return res


@njit(fastmath=True, cache=True)
def simulated_annealing(cities):
    old_cost = compute_path_travel_distance(cities)
    temperature = 1.0
    min_temperature = 0.00001
    alpha = 0.95
    #best_solution = None
    solution = cities
    while temperature > min_temperature:
        for iteration in range(1, 500):
            # canidate = random_permutation(solution, r = len(cities)) #Not NEARLY as good as the other one
            canidate = reverse_random_sublist(solution)
            new_cost = compute_path_travel_distance(canidate)
            # if new_cost < old_cost:
            #    best_solution = canidate
            if iteration % 50 == 0:
                print(iteration, temperature, old_cost)
                # f_string = f"Iteration #: {iteration}, temperature: {temperature}, solution:  {old_cost}" #numba doesn't like F strings
                # print(f_string)
            ap = acceptance_probability(old_cost, new_cost, temperature)
            if ap > random():
                solution = canidate
                old_cost = new_cost
        temperature = temperature * alpha
    return solution, compute_path_travel_distance(solution)


# res = simulated_annealing(cities)[0]
def GetPathFromRes(res, recalc, char):
    path = []
    for i in res:
        path.append((i, char[np.where(np.all(i == recalc, -1))[0]][0]))
    return path

def Print(line: str):
    pass

if __name__ == '__main__':
    text = """
    hello!
    how are you?
    so, here is some
    text
    we need to proceed
    it has multiple lines of different length
                and not always starts on the left
    """
    cities, recalc, char = PrepareText(text)
    res = simulated_annealing(cities)[0]
    print(GetPathFromRes(res, recalc, char))
