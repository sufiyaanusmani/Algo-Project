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


def onSegment(p, q, r):
    if ((q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and
            (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))):
        return True
    return False


def slope(p1, p2):
    if p1.x == p2.x:
        return float('inf')

    return (p2.y - p1.y) / (p2.x - p1.x)


def doIntersectMethod1(p1, q1, p2, q2):
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    if ((o1 != o2) and (o3 != o4)):
        return True

    if ((o1 == 0) and onSegment(p1, p2, q1)):
        return True

    if ((o2 == 0) and onSegment(p1, q2, q1)):
        return True

    if ((o3 == 0) and onSegment(p2, p1, q2)):
        return True

    if ((o4 == 0) and onSegment(p2, q1, q2)):
        return True

    return False


def doIntersectMethod2(p1, q1, p2, q2):
    x1, y1 = p1.x, p1.y
    x2, y2 = q1.x, q1.y
    x3, y3 = p2.x, p2.y
    x4, y4 = q2.x, q2.y

    denom = (y4-y3)*(x2-x1) - (x4-x3)*(y2-y1)
    if denom == 0:  # parallel
        return None
    ua = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / denom
    if ua < 0 or ua > 1:  # out of range
        return None
    ub = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / denom
    if ub < 0 or ub > 1:  # out of range
        return None
    x = x1 + ua * (x2-x1)
    y = y1 + ua * (y2-y1)
    return (x, y)


def findSide(p1, p2, p):
    val = (p[1] - p1[1]) * (p2[0] - p1[0]) - (p2[1] - p1[1]) * (p[0] - p1[0])

    if val > 0:
        return 1
    if val < 0:
        return -1
    return 0


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

    def bruteForce(self):
        self.hull = []

        h = 1
        for i in range(len(self.points)):
            for j in range(i+1, len(self.points)):
                x1, x2 = self.points[i].x, self.points[j].x
                y1, y2 = self.points[i].y, self.points[j].y
                a1, b1, c1 = y1-y2, x2-x1, x1*y2-y1*x2
                pos, neg = 0, 0
                for k in range(len(self.points)):
                    if (k == i) or (k == j) or (a1*self.points[k].x+b1*self.points[k].y+c1 <= 0):
                        neg += 1
                    if (k == i) or (k == j) or (a1*self.points[k].x+b1*self.points[k].y+c1 >= 0):
                        pos += 1
                if pos == len(self.points) or neg == len(self.points):
                    self.hull.append(self.points[i])
                    self.saveGraph(f'static/{h}bruteforce.png')
                    h += 1
                    self.hull.append(self.points[j])
                    self.saveGraph(f'static/{h}bruteforce.png')
                    h += 1

        self.hull = []
        ret = []
        for x in self.hull:
            ret.append(x)

        mid = [0, 0]
        n = len(ret)
        for i in range(n):
            mid[0] += ret[i].x
            mid[1] += ret[i].y
            ret[i].x *= n
            ret[i].y *= n
        ret = sorted(ret, key=cmp_to_key(compare))
        for i in range(n):
            ret[i] = [ret[i].x/n, ret[i].y/n]
            self.saveGraph(f'static/{h}bruteforce.png')
            h += 1

        createAnimation(output_file='static/convexhull.gif',
                        algorithm='bruteforce')

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

    def quickHull(self, a, n, p1, p2, side):

        ind = -1
        max_dist = 0

        for i in range(n):
            temp = distSq(p1, p2, a[i])

            if (findSide(p1, p2, a[i]) == side) and (temp > max_dist):
                ind = i
                max_dist = temp

        if ind == -1:
            self.hull.append("$".join(map(str, p1)))
            self.hull.append("$".join(map(str, p2)))
            return

        self.quickHull(a, n, a[ind], p1, -findSide(a[ind], p1, p2))
        self.quickHull(a, n, a[ind], p2, -findSide(a[ind], p2, p1))

    def quickElimination(self):
        n = len(self.points)
        if (n < 3):
            return

        min_x = 0
        max_x = 0
        for i in range(1, n):
            if self.points[i].x < self.points[min_x].x:
                min_x = i
            if self.points[i].x > self.points[max_x].x:
                max_x = i

        self.quickHull(
            self.points, n, self.points[min_x], self.points[max_x], 1)

        self.quickHull(
            self.points, n, self.points[min_x], self.points[max_x], -1)

        for element in self.hull:
            x = element.split("$")

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


text = ''


def linesIntersectionMethod1Page(request):
    global text
    text = ''
    if request.method == 'POST':
        p1 = Point(int(request.POST['p1x']), int(request.POST['p1y']))
        q1 = Point(int(request.POST['q1x']), int(request.POST['q1y']))
        p2 = Point(int(request.POST['p2x']), int(request.POST['p2y']))
        q2 = Point(int(request.POST['q2x']), int(request.POST['q2y']))

        if doIntersectMethod1(p1, q1, p2, q2):
            text = 'Line Segments Intersect'
        else:
            text = 'Line Segments Do Not Intersect'

        plt.clf()
        plt.plot([p1.x, q1.x], [p1.y, q1.y],
                 label='Line Segment 1', color='blue', marker='o')
        plt.plot([p2.x, q2.x], [p2.y, q2.y],
                 label='Line Segment 2', color='red', marker='s')
        plt.xlabel('x-axis')
        plt.ylabel('y-axis')
        plt.legend()
        plt.savefig('static/line.png')
        plt.clf()
        return redirect('lines-intersection-result-page')

    context = {'pageName': "Lines Interesection Method 1 Page"}
    return render(request, 'base/lines-intersection-method-1.html', context)


def linesIntersectionMethod2Page(request):
    global text
    text = ''
    if request.method == 'POST':
        p1 = Point(int(request.POST['p1x']), int(request.POST['p1y']))
        q1 = Point(int(request.POST['q1x']), int(request.POST['q1y']))
        p2 = Point(int(request.POST['p2x']), int(request.POST['p2y']))
        q2 = Point(int(request.POST['q2x']), int(request.POST['q2y']))

        point = doIntersectMethod2(p1, q1, p2, q2)
        if point is not None:
            text = 'Line Segments Intersect'
        else:
            text = 'Line Segments Do Not Intersect'

        plt.clf()
        plt.figure(figsize=(4, 4))
        plt.plot((p1.x, q1.x), (p1.y, q1.y), '.r--')
        plt.plot((p2.x, q2.x), (p2.y, q2.y), '.b--')

        if point is not None:
            plt.plot(*point, 'ok', markersize=10)
        plt.xlabel('x-axis')
        plt.ylabel('y-axis')
        plt.savefig('static/line.png')
        plt.clf()
        return redirect('lines-intersection-result-page')

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
            elif algorithm == 'bruteforce':
                convexHull.bruteForce()
            return redirect('convex-hull-result-page')
    context = {'pageName': "Convex Hull Page",
               'pointsEntered': pointsEntered, 'totalPoints': t, 'algorithm': algorithm}
    return render(request, 'base/convex-hull.html', context)


def convexHullResultPage(request):
    context = {'points': convexHull.hull}
    return render(request, 'base/convex-hull-result.html', context)


def linesIntersectionResultPage(request):
    context = {'text': text}
    return render(request, 'base/lines-intersection-result.html', context)
