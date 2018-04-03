from logging import info


def find_minimum(x_1, x_2, f_1, max_domain, function):
    counter = 0
    while abs(x_1 - x_2) != 0:
        counter += 1
        f_2 = function(x_2)

        if (f_1 - f_2) and (x_1 - x_2):
            # x_2 = x_2 - f_2 / f_2'
            x_1, f_1, x_2 = x_2, f_2, int(x_2 - f_2 / (f_1 - f_2) * (x_1 - x_2))
        else:
            x_1, f_1, x_2 = x_2, f_2, max_domain

    info("COUNTER: " + str(counter))
    return x_1, counter
