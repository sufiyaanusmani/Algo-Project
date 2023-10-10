from django.shortcuts import render

# Create your views here.


def homePage(request):
    context = {'pageName': "Home Page"}
    return render(request, 'base/index.html', context)


def linesIntersectionPage(request):
    context = {'pageName': "Line Interesection Page"}
    return render(request, 'base/index.html', context)
