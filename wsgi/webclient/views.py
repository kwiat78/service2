 
# from django.template import RequestContext
# from django.shortcuts import render
from django.template import Context
from django.template.loader import get_template
from django.template.response import TemplateResponse

def index(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
    #context = RequestContext(request)

    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
   

    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    template = get_template('index.html')
    #return template.render({},request=request)
    return TemplateResponse(request,template)
    #return render(request,'./index.html')