# Bibliotecas para Python
import json
import os
from dotenv import load_dotenv
load_dotenv()
# Bibliotecas para Django
from django.http import JsonResponse
from django.template import Template, Context
from django.template import loader
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# Bibliotecas para IBM Watson
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
# Base de datos
from chatblah.models import Productos
from chatblah.models import Pedidos
from chatblah.models import Sesiones

# Apikey
API_KEY = os.getenv('API_KEY')
authenticator = IAMAuthenticator(API_KEY)
assistant = AssistantV2(
    version='2022-01-11',
    authenticator=authenticator
)

# URL del servicio
assistant.set_service_url('https://api.us-south.assistant.watson.cloud.ibm.com/instances/f8645673-ac5f-480d-be7a-12046e73996a')

ASSISTANT_ID = os.getenv('ASSISTANT_ID')

# Imprimir datos en consola
# Muestra en la consola de Django los JSON de un mensaje
def p_consola(mensaje_json, origen=""):
    print(f'**********{origen}**********')
    print(json.dumps(mensaje_json, indent=2))
    print('=======================================')

# Envía el mensaje y el contexto de la conversación
def enviar_a_watson(mensaje):
    mensaje['input']['options'] = {
        'return_context': True
    }
    p_consola(mensaje,"De Django para Watson")
    response = assistant.message_stateless(
        assistant_id=ASSISTANT_ID,
        input=mensaje['input'],
        context=mensaje['context'] if 'context' in mensaje else {}
    ).get_result()
    p_consola(response,"De Watson para Django")
    return response

# Renderiza la página principal
def saludo(request):
    return render(request,'index.html')

# Sesión de Watson
# función en desuso, borrarla requiere mantenimiento en javascript
def mi_sesion(request):
    datos = {
        'result': '',
    }
    return JsonResponse(datos)

# Realiza consulta de datos en caso de que así lo requiera el contexto
def consultas_db(respuesta_watson):
    context_cliente = respuesta_watson['context']['skills']['main skill']
    if 'user_defined' in context_cliente:
        context_cliente = context_cliente['user_defined']
        # if hay que dar una descripción de producto
        if "dar_descripcion" in context_cliente and context_cliente["dar_descripcion"] == 1:
            context_cliente["dar_descripcion"] = 0
            # Consulta en DB y reescribe la respuesta de Watson
            for entidad in respuesta_watson['output']['entities']:
                if entidad['entity'] == 'producto':
                    nombre_producto = entidad['value'].capitalize()
            mi_prod = Productos.objects.filter(nombre=nombre_producto)

            descripcion_precio = 'Ofrecemos ' + mi_prod[0].descripcion + ' por tan solo ' + str(mi_prod[0].precio) + ' Bs.'

            for burbuja in respuesta_watson['output']['generic']:
                p_consola(burbuja, 'burbuja')
                if 'text' in burbuja and burbuja['text'].find('VARIABLE') != -1:
                    burbuja['text'] = descripcion_precio

        # if Cliente termina de comprar:
        if 'Excelente, su compra es' in respuesta_watson['output']['generic'][0]['text']:
            # Crea instancia de Pedidos con la sesion actual
            pedido=Pedidos(objeto=context_cliente['objeto_de_interes'],cantidad=context_cliente['cantidad'],email=context_cliente['correo_cliente'],telefono=context_cliente['tlf_cliente'],direccion=context_cliente['dir_cliente'])
            pedido.save()

    return respuesta_watson

# Flujo de mensaje desde el usuario a Watson y su retorno a Javascript
@csrf_exempt
def mi_mensaje(request):
    mi_respuesta = {}
    if request.method == 'POST':
        mensaje=json.loads(request.body)
        p_consola(mensaje,"Javascript")
        mi_respuesta = enviar_a_watson(mensaje)

        mi_nueva_respuesta = consultas_db(mi_respuesta)
    return JsonResponse(mi_nueva_respuesta)
