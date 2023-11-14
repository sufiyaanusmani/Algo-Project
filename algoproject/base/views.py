from django.shortcuts import render, redirect
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull as cv
import numpy as np
import imageio
import os
from functools import cmp_to_key

# Create your views here.


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


p0 = Point(0, 0)


def createAnimation(output_file, algorithm, fps=2):
    images = []
    png_folder = 'static'
    png_files = [f for f in os.listdir(
        png_folder) if f.endswith(f'{algorithm}.png')]
    print(png_files)
    png_files.sort()

    for png_file in png_files:
        file_path = os.path.join(png_folder, png_file)
        images.append(imageio.imread(file_path))

    # Save the animation
    imageio.mimsave(output_file, images, fps=fps, loop=10)


def orientation(p, q, r):
    val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)

    if val == 0:
        return 0
    elif val > 0:
        return 1
    else:
        return 2


def distSq(p1, p2):
    return ((p1.x - p2.x) * (p1.x - p2.x) +
            (p1.y - p2.y) * (p1.y - p2.y))


def compare(p1, p2):

    # Find orientation
    o = orientation(p0, p1, p2)
    if o == 0:
        if distSq(p0, p2) >= distSq(p0, p1):
            return -1
        else:
            return 1
    else:
        if o == 2:
            return -1
        else:
            return 1


def nextToTop(S):
    return S[-2]


class ConvexHull:
    def __init__(self):
        self.points = []
        self.hull = []

    def Left_index(self, points):
        minn = 0
        for i in range(1, len(points)):
            if points[i].x < points[minn].x:
                minn = i
            elif points[i].x == points[minn].x:
                if points[i].y > points[minn].y:
                    minn = i
        return minn

    def jarvisMarch(self):
        n = len(self.points)
        if n < 3:
            return
        l = self.Left_index(self.points)

        hull = []
        self.hull = []
        p = l
        q = 0
        while (True):

            hull.append(p)
            q = (p + 1) % n

            for i in range(n):
                if (orientation(self.points[p],
                                self.points[i], self.points[q]) == 2):
                    q = i
            p = q

            if (p == l):
                break

        i = 1
        for each in hull:
            self.hull.append(Point(self.points[each].x, self.points[each].y))
            self.saveGraph(f'static/{i}jarvis.png')
            i += 1

        createAnimation(output_file='static/convexhull.gif',
                        algorithm='jarvis')

    def grahamScan(self):
        self.hull = []
        points = self.points[:]
        n = len(points)
        ymin = points[0].y
        min = 0
        for i in range(1, n):
            y = points[i].y

            if ((y < ymin) or
                    (ymin == y and points[i].x < points[min].x)):
                ymin = points[i].y
                min = i

        points[0], points[min] = points[min], points[0]

        p0 = points[0]
        points = sorted(points, key=cmp_to_key(compare))

        m = 1
        for i in range(1, n):

            while ((i < n - 1) and
                   (orientation(p0, points[i], points[i + 1]) == 0)):
                i += 1

            points[m] = points[i]
            m += 1

        if m < 3:
            return

        self.hull.append(points[0])
        self.saveGraph(f'static/1graham.png')
        self.hull.append(points[1])
        self.saveGraph(f'static/2graham.png')
        self.hull.append(points[2])
        self.saveGraph(f'static/3graham.png')
        i = 4

        for i in range(3, m):

            while ((len(self.hull) > 1) and (orientation(nextToTop(self.hull), self.hull[-1], points[i]) != 2)):
                self.hull.pop()
                i -= 1
                self.saveGraph(f'static/{i}graham.png')
            self.hull.append(points[i])
            self.saveGraph(f'static/{i}graham.png')
            i += 1

        createAnimation(output_file='static/convexhull.gif',
                        algorithm='graham')

    def quickElimination(self):
        pass

    def saveGraph(self, fileName):
        allX = []
        allY = []
        hullX = []
        hullY = []
        p = []

        for point in self.points:
            allX.append(point.x)
            allY.append(point.y)
            p.append([point.x, point.y])

        for point in self.hull:
            hullX.append(point.x)
            hullY.append(point.y)
        hullX.append(self.hull[0].x)
        hullY.append(self.hull[0].y)
        # hull = cv(p)
        # plt.plot(p[:, 0], p[:, 1], 'o')
        # for simplex in hull.simplices:
        #     plt.plot(p[simplex, 0], p[simplex, 1], 'k-')
        plt.clf()
        plt.scatter(allX, allY, color='blue')
        plt.scatter(hullX, hullY, color='red')
        plt.plot(hullX, hullY)
        plt.xlabel('x')
        plt.ylabel('y')
        plt.title('Convex Hull')
        plt.savefig(fileName)
        plt.clf()


convexHull = ConvexHull()


def homePage(request):
    context = {'pageName': "Home Page"}
    return render(request, 'base/index.html', context)


def linesIntersectionPage(request):
    context = {'pageName': "Line Interesection Page"}
    return render(request, 'base/lines-intersection.html', context)


def linesIntersectionMethod1Page(request):
    context = {'pageName': "Lines Interesection Method 1 Page"}
    return render(request, 'base/lines-intersection-method-1.html', context)


def linesIntersectionMethod2Page(request):
    context = {'pageName': "Lines Interesection Method 2 Page"}
    return render(request, 'base/lines-intersection-method-2.html', context)


def convexHullPage(request):
    totalPoints = 0
    t = []
    algorithm = ''
    pointsEntered = False
    if request.method == 'POST':
        if 'totalPoints' in request.POST:
            totalPoints = int(request.POST['totalPoints'])
            for i in range(1, totalPoints+1):
                t.append(i)
            pointsEntered = True
        else:
            p = list(dict(request.POST).values())[1:-1]
            i = 0
            algorithm = request.POST['algorithm']
            convexHull.points = []
            while i < len(p):
                # points.append([int(p[i][0]), int(p[i+1][0])])
                convexHull.points.append(Point(int(p[i][0]), int(p[i+1][0])))
                i += 2
            if algorithm == 'jarvismarch':
                convexHull.jarvisMarch()
            elif algorithm == 'grahamscan':
                convexHull.grahamScan()
            return redirect('convex-hull-result-page')
    context = {'pageName': "Convex Hull Page",
               'pointsEntered': pointsEntered, 'totalPoints': t, 'algorithm': algorithm}
    return render(request, 'base/convex-hull.html', context)


def convexHullResultPage(request):
    context = {'points': convexHull.hull}
    return render(request, 'base/convex-hull-result.html', context)
