from django.http import HttpResponse
import requests
import hashlib
import json
from django.views.decorators.csrf import csrf_exempt
from apps.e_commerce.models import *

# AUTHORIZING AND SIGNING REQUESTS:
PUBLIC_KEY = '2155d3484959d692ee57107833220e88'
PRIVATE_KEY = 'ef5564b7ab99468f30662443281847d7fe6615e6'
TS = 1
    
TO_HASH = str(TS) + PRIVATE_KEY + PUBLIC_KEY 
HASHED = hashlib.md5(TO_HASH.encode())

URL_BASE = 'https://gateway.marvel.com/v1/public/'
SERVICE_ENDPOINT = 'comics'

PARAMS = {
            'ts': TS,
            'apikey': PUBLIC_KEY,
            'hash': HASHED.hexdigest()
        }


@csrf_exempt
def get_comics(request):

    data = {}
    html_code_block = ''

    # Creo listas que van a ser los contenedores
    # de los parámetros de los comics.
    ids = []
    titles = []
    descriptions = []
    prices = []
    thumbnails = []

    comics = []     # Lista que va a contener los comics de marvel

    # Inicialización para el paginado.
    limit = 20
    offset = 0

    # Obtengo los parámetros para realizar el paginado.
    if request.GET.get('limit') != None and request.GET['limit'].isdigit() is True:
        limit = request.GET['limit']
    else:
        limit = 15

    if request.GET.get('offset') != None and request.GET['offset'].isdigit() is True:
        offset = request.GET['offset']
    else:
        offset = 0

    # Actualizo los parametros con los valores de limit y offset.
    aditional_params = {'limit': limit, 'offset': offset}
    params = PARAMS
    params.update(aditional_params)

    # Me conecto a la URL de marvel para obtener los comics.
    response = requests.get(url=URL_BASE+SERVICE_ENDPOINT, params=params)

    if response.status_code == 200:
        data = json.loads(response.text)

    # Creo un archivo json con el contenido de la request.
    with open('get_all_comics.json', 'w') as jfile:
        jfile.write(json.dumps(data, indent=4))

    comics = data.get('data').get('results')    # Obtengo los resultados de los comics

    # Recorro los comics obtenidos y voy guardando sus propiedades en listas.
    for comic in comics:
        ids.append(comic.get('id'))
        titles.append(comic.get('title'))
        descriptions.append(comic.get('description'))
        prices.append(comic.get('prices')[0].get('price'))
        thumbnails.append(comic.get('thumbnail').get('path') + '/standard_xlarge.jpg')


    for i in range(len(ids)):

        id = ids[i]
        title = titles[i]
        
        if descriptions[i] == None:
            description = "Description Not Available"
        else:
            description = descriptions[i]
        
        if prices[i] == 0.00:
            visibility = 'hidden'   # Sirve para ocultar el button de compra del comic.
            price = "N/A"
        else:
            price = prices[i]
            visibility = 'visible'
        
        thumbnail = thumbnails[i]

        # Obtengo el bloque de código a insertar dentro del template.
        html_code_block += f'''
                                <tr>
                                    <td>
                                        <img src="{thumbnail}"">
                                    </td>
                                    <td>
                                        <ul>
                                            <li>{title}</li>
                                            <li>{description}</li>
                                            <li>{price} USD</li>
                                        </ul>
                                    </td>
                                    <td>
                                        <form action="http://localhost:8000/e_commerce/purchased_item/" method="post" style="visibility: {visibility};">
                                            <label for="quantity"><h3>Enter Quantity</h3></label>
                                            <input type="number" name="quantity" min="0" max=15">
                                            <input type="submit" value="Buy">
                                            <input type="text" name="id" value="{id}" style="visibility: hidden;">
                                            <input type="text" name="title" value="{title}" style="visibility: hidden;">
                                            <input type="text" name="description" value="{description}" style="visibility: hidden;">                                                                                        <input type="text" name="title" value="{title}" style="visibility: hidden;">
                                            <input type="text" name="price" value="{price}" style="visibility: hidden;">
                                            <input type="text" name="thumbnail" value="{thumbnail}" style="visibility: hidden;">
                                        </form>
                                    </td>
                                </tr>
                        '''

    # Realizo el template para mostrar al usuario:
    template = f'''
                    <html>
                        <head>
                            <title>Buy Comics</title>
                        </head>
                        <body>
                            <header>
                            </header>
                            <article style="background: darkred">
                                <section>
                                    <div align="center">
                                        <h1>Comics Shop</h1>
                                    </div>
                                        <p>
                                            <div style="height:90%; width:90%; overflow:auto; background:yellow">
                                                <table border="1px">
                                                    {html_code_block}
                                                </table>
                                            </div>
                                        </p>
                                </section>
                            </article>
                            <footer align="center" style="background: cyan;">
                                <form action="http://localhost:8000/e_commerce/get_comics/" method="get">
                                    <label for="limit"><b>Limit</b></label>
                                    <input type="number" name="limit">
                                    <label for="offset"><b>Offset</b></label>
                                    <input type="number" name="offset">
                                    <input type="submit" value=Submit>
                                </form>
                            </footer>
                        </body>
                    </html>
    
                '''

    return HttpResponse(template)


@csrf_exempt
def purchased_item(request):

    # Obtengo los valores de los parámetros
    # enviados por POST para luego almacenarlos
    # en la Base de Datos.
    id = request.POST.get('id')
    title = request.POST.get('title')
    description = request.POST.get('description')
    price = request.POST.get('price')
    thumbnail = request.POST.get('thumbnail')
    quantity = request.POST.get('quantity')

    print(quantity)

    # Pregunto si el comic ya está en la Base de Datos.
    # Me devuelve un resultado del tipo queryset.
    queryset = Comic.objects.filter(marvel_id=id)
    
    if len(queryset.values_list()) == 0:
        item = Comic(marvel_id=id, title=title, description=description, 
                        price=price, stock_qty=quantity, picture=thumbnail)

        item.save()
    else:
        comic = Comic.objects.get(marvel_id=id)
        actual_stock = comic.stock_qty
        actual_stock += int(quantity)
        Comic.objects.filter(marvel_id=id).update(stock_qty=actual_stock, description=description, title=title)


    # Calculamos el precio total de los comics comprados:
    try:
        total_price = float(price) * int(quantity)
    except:
        total_price = '. . .'

    # Obtengo el bloque de código a insertar dentro del template.
    html_code_block = f'''
                            <tr>
                                <td><img src="{thumbnail}"></td>
                                <td>
                                    <ul>
                                        <li><b>Title:</b> {title}</li>
                                        <li><b>ID:</b> {id}</li>
                                        <li><b>Description:</b> {description}</li>
                                        <li><b>Price:</b> {price} USD</li>
                                        <li><b>Quantity:</b> {quantity}</li>
                                        <li><b>Total Price:</b> {total_price:.2f} USD</li>
                                    </ul>
                                    <form action="http://localhost:8000/e_commerce/get_comics/" method="get">
                                        <input type="submit" value="Back">
                                    </form>
                                </td>
                            </tr>
                    '''


    # Realizo el template para mostrar al usuario:
    template = f'''
                    <html>
                        <head>
                            <title>Buyed Comic</title>
                        </head>
                        <body>
                            <header>
                            </header>
                            <article style="background: grey">
                                <section>
                                    <div align="center">
                                        <h1>Buyed Comic</h1>
                                    </div>
                                        <p>
                                            <div style="height:90%; width:90%; overflow:auto; background:cyan">
                                                <table border="1px">
                                                    {html_code_block}
                                                </table>
                                            </div>
                                        </p>
                                </section>
                            </article>
                            <footer>
                            </footer>
                        </body>
                    </html>
                '''

    return HttpResponse(template)
