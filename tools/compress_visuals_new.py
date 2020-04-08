import matplotlib.pyplot as plt
from logger_default.logger import get_clean_date


def get_data():
    points = []
    with open('../image_optimiser/quality+.webp.log', mode='r') as file:

        for i, line in enumerate(file):
            line = line.split('\t')
            size = line.pop(0)
            max_perception = line.pop(0)
            perception, webp = [], []
            while line:
                webp.append(int(line.pop(0)))
                perception.append(-1 * float(line.pop(0)))
                # points.append((int(size), perception[-1]))
                # break
            # draw_graph()
            points.append((perception, webp))

            # if i > 100:
            #    return points

    return points


def old():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    n = 100

    xs, ys, zs = get_data()
    ax.scatter(xs, ys, zs, c='r', marker='o')

    ax.set_xlabel('SIZE')
    ax.set_ylabel('JPEG')
    ax.set_zlabel('SSIM')


def draw_graph(x, y, c='#BAE6FF'):
    plt.plot(x, y, c=c, marker='o')

    plt.xlabel('size ')
    plt.ylabel('webp')
    plt.title('About as simple as it gets, folks')
    plt.grid(True)

    return plt


# plt.show()

# size, webp = zip(*get_data())
# plt = draw_graph(size, webp)
for perception, webp in get_data()[230:]:
    plt = draw_graph(perception[:-1], webp[:-1])
    plt = draw_graph(perception[-1:], webp[-1:], c='#FFC5C4')
plt.savefig(get_clean_date() + ".png", dpi=500)
plt.show()
