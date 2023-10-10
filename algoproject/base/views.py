from django.shortcuts import render

# Create your views here.


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
