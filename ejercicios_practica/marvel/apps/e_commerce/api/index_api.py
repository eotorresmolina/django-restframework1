from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes


@api_view(['GET', 'POST'])
@permission_classes([])
def hello_user(request):

    # Inicializo el nombre.
    name = 'Django'

    # Pregunto si el nombre del usuario fue pasado
    # como parámetro a través de un POST.
    # Usar POSTMAN para probarlo.
    if request.data.get('user_name') != None:
        name = request.data.get('user_name')
    
    template = f'''
                <html>
                    <head>
                        <title>Index</title>
                    <head>
                    <body style='background: blue'>
                        <div style='background: darkblue'>
                            <h1>Hello {name}!</h1>
                        <div>
                    <body>
            </html>
        '''


    print(template)

    return HttpResponse(template)