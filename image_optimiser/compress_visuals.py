from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

def randrange(n, vmin, vmax):
    '''
    Helper function to make an array of random numbers having shape (n, )
    with each number distributed Uniform(vmin, vmax).
    '''
    return (vmax - vmin) * np.random.rand(n) + vmin


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

n = 100

# For each set of style and range settings, plot n random points in the box
# defined by x in [23, 32], y in [0, 100], z in [zlow, zhigh].
#for c, m, zlow, zhigh in [('r', 'o', -50, -25), ('b', '^', -30, -5)]:
#    xs = randrange(n, 23, 32)
#    ys = randrange(n, 0, 100)
#    zs = randrange(n, zlow, zhigh)
#    ax.scatter(xs, ys, zs, c=c, marker=m)
def get_data():
    points = defaultdict(list)
    with open('./quality.log', mode='r') as file:
        x = 0
        try:
            for i, line in enumerate(file):
                print(line[2:4:1])
                if '\t' in line[2:3:1]:
                    y, z = line.split('\t')
                    y, z = int(y), int(float(z)*-1000000000)

                    points[x].append((y ,z))
                else:
                    x = int(line)
        except Exception as e:
            print(z)

        return zip(*[(x, y ,z/x) for y, z in points[x] for x in sorted(points)[2::10]])

xs, ys, zs = get_data()
ax.scatter(xs, ys, zs, c='r', marker='^')

ax.set_xlabel('SIZE')
ax.set_ylabel('JPEG')
ax.set_zlabel('SSIM')

plt.show()
