import time

name = "Master Bonglord"
age = 69


def range_len_pattern():
    a = [1, 2, 3]
    # instead of for i in range (len(a)):
    #   v = a[i]
    #  we do:
    for v in a:
        print (v)
def syncing_variable():
    a = [1, 2, 3]
    b = [4, 5, 6]
    for av, bv in zip(a, b):
        print(av, bv)
def tuple_unpacking():
    mytuple = 1, 2
    # instead of x = mytuple[0], and y = mytuple[1]
    # we do:
    x, y = mytuple
    print (x, y)

def timing_with_time():  # don't use time.time to time.  Use perf_counter:
    start = time.perf_counter()
    time.sleep(1)
    end = time.perf_counter()
    print(end-start)

def to_lowercase(input):
    return input.lower()


# range_len_pattern()
# syncing_variable()
# tuple_unpacking()
# timing_with_time()


# F-STRINGS - They're evaluated at runtime, so you can put any valid Python expression in them.  Note the global variables.

# Syntax:
print(f"Hello {name + ', God of the universe'}. You are {age * 72} years old.")

# You can call functions with f-strings too
print(f"{to_lowercase(name)} is funny.")

# You can also call a method directly
print(f"{name.upper()} is funny.")


