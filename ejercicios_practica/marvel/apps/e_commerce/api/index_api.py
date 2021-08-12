from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes


@api_view(['GET', 'POST'])
@permission_classes([])
def hello_user(request):

    if request.data.get('user_name') is None:
    
        template = '''
                    <html>
                        <head>
                            <title>Index</title>
                        <head>
                        <body style='background: blue'>
                            <div style='background: darkblue'>
                                <h1>Hello Django!</h1>
                            <div>
                        <body>
                </html>
            '''
    else:
        template = f'''
                    <html>
                        <head>
                            <title>Index</title>
                        <head>
                        <body style='background: blue'>
                            <div style='background: darkred'>
                                <h1>Hello {request.data.get('user_name')}!</h1>
                            <div>
                        <body>
                    </html>
                '''

    print(template)

    return HttpResponse(template)