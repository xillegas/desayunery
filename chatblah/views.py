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

#apikey
API_KEY = os.getenv('API_KEY')
authenticator = IAMAuthenticator(API_KEY)
assistant = AssistantV2(
    version='2022-01-11',
    authenticator=authenticator
)

# URL del servicio
assistant.set_service_url('https://api.us-south.assistant.watson.cloud.ibm.com/instances/f8645673-ac5f-480d-be7a-12046e73996a')

# Asunto de SSL
#assistant.set_disable_ssl_verification(True)

# Crear la sesion
#  Se utiliza una sesión para enviar la entrada del usuario
# a un conocimiento y recibir respuestas.
#  También mantiene el estado de la conversación.
ASSISTANT_ID = os.getenv('ASSISTANT_ID')
def crear_sesion_watson():
    response = assistant.create_session(
        assistant_id=ASSISTANT_ID
        ).get_result()

    Sesiones.objects.create(identificador=response['session_id'])
    return 'OK'

# Enviar entrada de usuario al asistente
#  y recibir una respuesta, con estado de conversación
# (incluyendo datos de contexto) almacenado por Watson
# Assistant durante el tiempo de duración de la sesión.
def enviar_a_watson(mensaje):
    mensaje['options'] = {
        'return_context': True
    }
    mi_sesion = Sesiones.objects.values().first()
    session_id = mi_sesion['identificador']
    response = assistant.message(
        assistant_id=ASSISTANT_ID,
        session_id=session_id,
        input=mensaje
    ).get_result()
    return response

#print(json.dumps(response, indent=2))

def saludo(request):
    Sesiones.objects.all().delete()
    crear_sesion_watson()
    return render(request,'index.html')

def mi_sesion(request):
    mi_sesion = Sesiones.objects.values().first()
    session_id = mi_sesion['identificador']
    datos = {
        'result': session_id,
    }
    return JsonResponse(datos)

def consultas_db(respuesta_watson):
    # if Existe una descripción de producto
    if respuesta_watson['output']['generic'][0]['text'].find('[VARIABLE_DESC') != -1:
        # Consulta en DB y reescribe la respuesta de Watson
        nombre_producto = respuesta_watson['output']['entities'][0]['value'].capitalize()
        mi_prod = Productos.objects.filter(nombre=nombre_producto)
        respuesta_watson['output']['generic'][0]['text'] = 'Ofrecemos ' + mi_prod[0].descripcion + ' por tan solo ' + str(mi_prod[0].precio) + ' Bs.'

    # Caso donde la descripción del producto no está en el primer mensaje
    if respuesta_watson['output']['generic'][0]['text'].find('Sí, tenemos') != -1:
        for entidad in respuesta_watson['output']['entities']:
            if entidad['entity'] == 'producto':
                nombre_producto = entidad['value'].capitalize()
        mi_prod = Productos.objects.filter(nombre=nombre_producto)
        respuesta_watson['output']['generic'][1]['text'] = 'Ofrecemos ' + mi_prod[0].descripcion + ' por tan solo ' + str(mi_prod[0].precio) + ' Bs.'

    # if Cliente termina de comprar:
    if 'Excelente, su compra es' in respuesta_watson['output']['generic'][0]['text']:
        # Crea instancia de Pedidos con la sesion actual
        ped_cliente = respuesta_watson['context']['skills']['main skill']['user_defined']
        pedido=Pedidos(objeto=ped_cliente['objeto_de_interes'],cantidad=ped_cliente['cantidad'],email=ped_cliente['correo_cliente'],telefono=ped_cliente['tlf_cliente'],direccion=ped_cliente['dir_cliente'])
        pedido.save()

    return respuesta_watson

@csrf_exempt
def mi_mensaje(request):
    mi_respuesta = {}
    if request.method == 'POST':
        mensaje=json.loads(request.body)

        mi_respuesta = enviar_a_watson(mensaje['input'])

        mi_nueva_respuesta = consultas_db(mi_respuesta)
    return JsonResponse(mi_nueva_respuesta)
