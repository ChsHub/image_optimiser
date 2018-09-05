from logging import info


# https://de.wikipedia.org/wiki/Newton-Verfahren#Konvergenzbetrachtungen
# Das Newton-Verfahren ist ein sogenanntes lokal konvergentes Verfahren.
# Konvergenz der in der Newton-Iteration erzeugten Folge zu einer Nullstelle ist also nur garantiert,
# wenn der Startwert, d. h. das 0-te Glied der Folge, schon „ausreichend nahe“ an der Nullstelle liegt.
# Ist der Startwert zu weit entfernt, ist das Konvergenzverhalten nicht festgelegt, das heißt,
# es ist sowohl eine Divergenz der Folge möglich als auch eine Oszillation
# (bei der sich endlich viele Funktionswerte abwechseln)
# oder eine Konvergenz gegen eine andere Nullstelle der betrachteten Funktion.

def find_minimum(x_1, x_2, min_domain, max_domain, offset, function):
    counter = 0
    f_1 = function(x_1) - offset
    history = [(x_1, f_1)]

    while x_1 - x_2:  # while different
        counter += 1
        f_2 = function(x_2) - offset
        history.append((x_2, f_2))

        if f_1 - f_2:
            # x_2 = x_2 - f_2 / f_2'
            x_1, f_1, x_2 = x_2, f_2, int(x_2 - f_2 / (f_1 - f_2) * (x_1 - x_2))
        else:
            x_1, f_1, x_2 = x_2, f_2, max_domain

        x_2 = min(x_2, max_domain)
        x_2 = max(x_2, min_domain)

        if counter > 10:
            find_minimum(x_1, x_2, min_domain, max_domain, offset, function)

    info("COUNTER: " + str(counter))
    return x_1, counter
