��    1      �      ,      ,  �   -  5  �  B  �  �   9    �  @   �  O     �   e  d  	     f
  x   n
  -   �
  
     ;      /  \  �   �  /   M  F   }  �   �  �   �     V  �  c  "   G  B   j  J   �  T   �  �   M  6    F  J  �   �     v  �   �  )   o  Z   �    �  �   
  �   �    �  �   �  %  �  �   �  =  �   �  �!  �  K#  _   �$  �   D%  �   &  \   �&  2  Y'  �   �(  R  J)  ?  �*  �   �+  E  z,  @   �-  d   .  �   f.  �  */     �0  x   �0  (   ^1     �1  >   �1  '  �1  �   �2  7   �3  K   4  �   _4  �   ,5     6  .  #6  %   R8  B   x8  n   �8  a   *9  �   �9  ~  �:  �  =  �   �?     �@    �@  '   �A  o   �A  C  _B  �   �C  0  �D  7  �E  �   �F  2  �G  �   �H  o  �I  �  K  �  �L  s   �N  �   "O  �   P  Y   �P   All of the considerations taken to develop checks also apply to plugins. So if in doubt review those guidelines in the checks development section. Also note that Radar expects to find a unique plugin class per plugin directory. It is a requirement that this class to be present only in the __init__.py file in that directory. Despite this minor limitation you're allowed to code in as many different directory/files inside the plugin directory as you want. As explained before, a Radar plugin needs to comply with certain requirements. In first place every plugin must inherit from the ServerPlugin class. You achieve that by importing the ServerPlugin class and creating a new class and inheriting from ServerPlugin. This is achieved in the first two lines of the above example. Before we end up this section you may be wondering : How should I use the checks and contacts lists in the on_check_reply() method ? Contact and Check objects have some attributes that you can read to perform some work. For example : every contact object contains a name, an email and optionally a phone number. The following piece of code shows how to read any useful value (both from a contact and a check) : Create a directory called dummy-plugin (or name it as you want). Create an __init__.py file inside this directory and copy the above code to it. Even if you're not proficient with Python or object oriented programming keep reading and decide by yourself if writing a Radar plugin is a difficult task. Every plugin must have a name. We define this in the PLUGIN_NAME class attribute. Every plugin is uniquely identified by its name and a version. If you don't specify a version then it defaults to 0.0.1. To define a version you only need to overwrite the PLUGIN_VERSION class attribute with the desired value. In this exaple we only defined the plugin name. Example For example, assuming that you wrote the ProxyPlugin described above then, you could have the following file hierarchy : Given this YAML file (called udp-proxy.yml) : Guidelines If Radar is already running then you'll need to restart it. If you still want to see a more elaborate example (actually something useful, right ?) then you can take a look to an email notifier plugin `here <https://github.com/lliendo/Radar-Plugins>`_. This plugin will notify its contacts when a check has any of its status (current or previous) distinct from OK. If you want to see these replies you'll probably need a tool like `Netcat <http://nc110.sourceforge.net/>`_. If you indeed have Netcat installed on your system then open up a console and run : If you want to verify this small plugin, then : If your ProxyPlugin also depended on more modules then you could had : In a similar way the on_shutdown() method is called when Radar is shutdown, this method's purpose is to gracefully release any resources that you might have acquired during the life of the plugin. In this minimal example we're basically doing nothing, just recording a few things to the Radar log file using the log() method. A Radar plugin is just a Python class where you can code anything you want. Introduction Is that all you need to know to develop a plugin ? Basically yes, but there is one more feature that can be extremely useful in some cases. Let's say you want to allow your users configure your plugin, that is let your users modify certain parameters of your plugin. If you've just wrote a plugin that connects to a database to insert data then it is not a good practice to modify the database parameters directly from the plugin code. Radar plugins come with a YAML mapper for free. Let's adjust our initial example : Let's take a look at a minimal plugin and describe the key points. Make sure you get a new entry in the log every time a check reply arrives. Move the directory you created in step one to your Radar server's plugins directory. Note that in the above example we're only inspecting the first contact and check. Remember that you always receive two lists, so you may need to iterate them in order to achieve your plugin's task. Now take a look at the DEFAULT_CONFIG class attribute. This class attribute allows you to set default values for your plugin configuration provided that a user does not set a certain parameter. Radar (internally) will merge the values read from the file and those found in the DEFAULT_CONFIG class attribute. Setting this dictionary is completly optional. This can be very useful for example if a user forgets to create a configuration file for your plugin, by using a default config you make sure that at least your plugin won't fail due to a missing configuration. Ok, now we have a useful plugin. Every time we receive a reply we simply forward it using a UDP socket. Note in this example that I've set the PLUGIN_CONFIG_FILE to hold the filename of the YAML (udp-proxy.yml in this case) and that I use the values that were read from that file in the _forward() method. Also note the use of the get_path() static method to properly reference the YAML file and that I convert every check and contact to a dictionary before serializing and sending the data. The to_dict() method dumps every relevant attribute of each object to a Python dictionary. One last thing. If you inspect the current_status and the previous_status attributes of a check you'll notice that both of them are integers. If you need to convert those values to their respective names, here's how to do that : Plugins development Radar has (internally) among many abstractions two that you will use directly in any plugin : Contact and Check. Whenever you get a reply you get a list that contains contact objects and another list that contains check objects. Take a look a this piece of Python code : The above command will capture and display UDP datagrams destined for localhost port 2000. The conversion is done using the static Check.get_status() method. Note that I've also imported the Check class in the second line of the example. Now current_status and previous_status hold any of the valid string codes that a check can return (OK, WARINING, SEVERE or ERROR). The example shows three methods. The on_start() method is invoked by Radar when the plugin is initialized, so if you want to define any instance attributes or acquire resources, this is one place to do that. To get this example running follow the same steps we described for the DummyPlugin and also create a file named udp-proxy.yml that contains the YAML commented above. Don't forget to put this file inside the same directory where __init__.py is. To use it simply set the PLUGIN_CONFIG_FILE class attribute with the configuration filename and that's it. How do you read those values ? Easy again, just access the config dictionary. Let's see an example. Suppose you want to proxy every reply to another service using a UDP socket. We have only one remaining method: on_check_reply(). This is where the action takes place and is your entry point to perform any useful work. For every reply that the Radar server receives you'll get : We're now going to describe plugin development. Although you may think that this might be a complex task, a lot of effort has been put in the design of this part of Radar so you can easily write a plugin. You will need to at least understand a little of Python and object oriented programming. We've just described how Radar processes plugins. We're now going to take a look at how a minimal plugin is written and what considerations should be taken at development time. What does it do ? Very simple : given a YAML filename it will map it to a Python dictionary. This way you only specify the filename of your configuration file, set the values that you need in that file and then retrieve them from a dictionary. The only requirement is that this file must be in your plugin directory ! When the server receives a check reply every plugin is sequentially invoked passing it some information. That's all Radar does, from that point (when your plugin receives a check reply) you have partial control on what is done. When all plugins finish processing a certain reply, full control is regained by Radar. This process repeats indefinitely until of course you shut down Radar. When you first launch Radar all plugins are instantiated, that is for every plugin that Radar finds in its plugins directory it tries to create an object. This isn't just any object, it has to comply somehow with what Radar expects to be a valid plugin. If Radar instantiates a certain plugin without problems then it proceeds to configure it. After it has been configured it is appended to a set of plugins. address : The IP address of the Radar client that sent the check reply. This is a string value. checks : A Python list containing Check objects that were updated by the server. This list will always respond to a given monitor, that means that the list of checks you got belongs to one and only one monitor. contacts : A Python list containing Contact objects that were related due to the replied checks. This list will always respond to a given monitor, that means that the list of contacts you got belongs to one and only one monitor. port : The TCP port of the Radar client that sent the check reply. This is an integer value. Project-Id-Version: Radar 0.0.1b
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2015-09-11 17:19-0300
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: FULL NAME <EMAIL@ADDRESS>
Language-Team: LANGUAGE <LL@li.org>
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
 Todas las consideraciones que se han tomado para desarrollar chequeos también se aplican a plugins. Si estas con alguna dudas puedes volver a revisar la sección de desarrollo de chequeos. Ten en cuenta que Radar espera encontrar una única clase plugin por cada directorio de plugin. Es un requerimiento que esta clase se encuentre en el archivo __init__.py dentro del directorio del plugin. Dejando de lado esta limitación, puedes escribir código en tantos archivos/directorios dentro del directorio del plugin como desees. Como hemos explicado antes un plugin de Radar debe cumplir con ciertos requerimientos. En primer lugar todo plugin debe heredar de la clase ServerPlugin. Esto se realiza primero importando la clase ServerPlugin y luego creando una nueva clase que herede de la misma. Esto se hace en las primeras dos líneas de código. Antes de finalizar esta sección seguramente te estarás preguntando ¿Como debo utilizar las listas de chequeos y contactos en el método on_check_reply()? Tanto los objetos Contact como Check contienen ciertos atributos que puedes inspeccionar para hacer lo que necesites. Por ejemplo : cada objeto contacto tiene un nombre, un email y opcionalmente un número telefónico. El siguiente fragmento de código muestra como leer cualquier atributo (ya sea un contacto o un chequeo) : Crea un directorio llamado dummy-plugin (o nombralo como desees) Crea un archivo __init__.py dentro de este directorio y copia el contenido del código fuente en el. Aún si consideras que no tienes conocimiento de Python o programación orientada a objetos te recomiendo que continues leyendo y decidas por tu mismo si escribir un plugin es una tarea difícil. Cada plugin debe tener un nombre. Esto lo hacemos definiendo un nombre en el atributo de clase PLUGIN_NAME. Cada plugin es unívocamente identificado por su nombre y su versión. Si no especificas una versión entonces toma el valor 0.0.1 por defecto. Para definir una versión solamente debes sobreescribir el atributo de clase PLUGIN_VERSION con el valor que desees. En nuestro ejemplo solamente hemos definido el nombre del plugin. Ejemplo Asumiendo que has escrito el ProxyPlugin que comentamos arriba, entonces tendrías la siguiente jerarquía de archivos : Dado este archivo YAML (udp-proxy.yml) : Consejos Si Radar ya se encuentra ejecutando, necesitarás reiniciarlo. Si todavía quieres ver un ejemplo más elaborado (algo un poco más útil, ¿no?) puedes echar un vistazo a un plugin notificador de correo `aquí <https://github.com/lliendo/Radar-Plugins>`_. Este plugin notificará a sus contactos cuando un chequeo tiene alguno de sus estados diferente a OK. Si quieres ver los mensajes UDP que genera este plugin probablemente necesites de una herramienta como `Netcat <http://nc110.sourceforge.net/>`_. Si ya tienes Netcat instalado en tu sistema entonces abre una consola y ejecuta : Si quieres verificar el funcionamiento de este plugin : Si adicionalmente este ProxyPlugin dependiera de otros modulos, tendrías : De manera similar el método on_shutdown() es invocado cuando Radar es apagado. El propósito de este método es liberar adecuadamente cualquier recurso que pudieras haber adquirido durante su ejecución. En este ejemplo mínimo básicamente no estamos haciendo nada, solamente registrando algunas cosas en el log de Radar utilizando el método log(). Un plugin de Radar es tan solo una clase Python en donde puedes hacer lo que quieras. Introducción ¿Todo esto es lo que necesitas para desarrollar un plugin?. En principio si, pero hay una característica adicional que puede ser de mucha utilidad en algunos casos. Digamos por ejemplo que deseas permitir a tus usuarios configurar tu plugin, esto es, permitirles modificar ciertos parámetros del plugin que has desarrollado. Si has escrito por ejemplo un plugin que se conecta a una base de datos, no es una buena práctica que modifiques estos parámetros directamente desde el código fuente del plugin. Los plugins de Radar incluyen con un mapper YAML. Reajustemos nuestro ejemplo inicial : Veamos un plugin a modo de ejemplo y describamos sus puntos clave. Asegurate de que se escribe una nueva entrada al log cada vez que una respuesta de algún cliente es recibida. Mueve el directorio que has creado en el primer paso al directorio de plugins del servidor Radar. Ten en cuenta que en el ejemplo de arriba solamente estamos inspeccionando el primer contacto y chequeo. Recuerda que siempre recibes dos listas, así que probablemente necesites iterarlas para alcanzar la tarea que tu plugin se propone realizar. Ahora echa un vistazo al atributo de clase DEFAULT_CONFIG. Este atributo de clase te permite definir valores por defecto de la configuración de tu plugin si el usuario no define algún parámetro. Radar internamente une los valores por defecto con los de tu archivo de configuración. El seteo de este diccionario es completamente opcional. Definir una configuración por defecto puede ser útil ya que si por ejemplo un usuario se olvida de crear el archivo de configuración de tu plugin, al utilizar una configuración por defecto te aseguras de que al menos tu plugin no fallará debido a la falta de dicho archivo de configuración. Ahora tenemos un plugin más útil. Cada vez que recibimos una respuesta simplemente la reenviamos utilizando un socket UDP. En este nuevo ejemplo puedes notar que he seteado el atributo de clase PLUGIN_CONFIG_FILE con el nombre del archivo YAML (proxy.yml en este caso) y que utilizo los valores que fueron leidos de ese archivo en el método _forward(). También utilizo el método to_dict() para convertir un objeto check o contact en un diccionario Python (esto es necesario para poder enviar los datos a través del socket). Por último y no menos importante, fijate que hago uso del método estático get_path() para referenciar apropiadamente el archivo YAML de configuración. Una última cosa. Si inspeccionas los atributos previous_status y current_status de un chequeo te darás cuenta de que ambos contienen un valor númerico. Si necesitas convertir estos valores a sus respectivos nombres esta es la manera de hacerlo :  Desarrollo de plugins Radar (internamente) tiene entre varias de sus abstracciones dos que utilizarás directamente en cualquier plugin : Contact y Check. Cada vez que obtienes una respuesta de algún cliente recibes una lista que contiene contactos y otra lista que contiene chequeos. Mira este fragmento de código Python : Este comando capturará y mostrará todos los datagramas UDP que tienen como destino a localhost y puerto 2000. Esta conversión se hace utilizando el método estático Check.get_status(). Ten en cuenta que también he importado la clase Check en la segunda línea del ejemplo. Ahora las variables current_status y previous_status contienen alguno de los posibles códigos que un chequeo puede devolver (OK, WARINING, SEVERE or ERROR). El ejemplo nos muestra tres métodos. El método on_start() es invocado por Radar cuando el plugin es inicializado, así que si deseas definir cualquier atributo de instancia o tomar algún recurso, este es un lugar para hacerlo. Para probar este ejemplo sigue los mismos pasos que hemos hecho para probar el primer plugin, también crea el archivo udp-proxy.yml y agrega el contenido del YAML que hemos descripto más arriba. No te olvides de colocar este archivo dentro del mismo directorio donde se encuentra el archivo __init__.py Para utilizar esta funcionalidad, setea el atributo de clase PLUGIN_CONFIG_FILE con el nombre del archivo de configuración. ¿Como lees entonces estos valores?. Fácil, simplemente accedes al diccionario config. Veamos un ejemplo. Suponte que quieres reenviar cada respuesta que recibes mediante un socket UDP. Nos queda solamente un método : on_check_reply(). Aquí es donde la acción toma lugar y es tu punto de entrada para realizar cualquier cosa. Por cada respuesta que el servidor recibe obtendrás : Vamos ahora a describir el desarrollo de plugins. Aúnque creas que esta puede ser una tarea compleja, un gran esfuerzo ha sido puesto en el diseño de esta parte de Radar para que puedas fácilmente escribir plugins. Deberás tener un conocimiento mínimo de Python y de programación orientada a objetos. Hemos descripto como Radar procesa sus plugins. A continuación veremos a modo de ejemplo como se escribe un plugin mínimo y que consideraciones debemos tener en cuenta al desarrollarlo. ¿Que es lo que hace? Muy sencillo : Dado un archivo YAML, lo asociará a un diccionario Python. De esta manera tu solamente tienes que especificar el nombre del archivo de configuración de tu plugin, setear ciertos parametros en dicho archivo y luego leerlos de un diccionario. ¡El único requerimiento es que este archivo debe estar el el directorio de tu plugin! Cuando el servidor recibe una respuesta a un chequeo cada plugin es secuencialmente invocado y se le pasa cierta información. Eso es todo lo que Radar hace, de ahí en más (cuando tu plugin recibe una respuesta a un chequeo) tu tienes control parcial sobre lo que se realiza. Cuando todos los plugins terminan de procesar una respuesta, el control del flujo de ejecución vuelve a ser administrado por Radar. Este proceso se repite indefinidamente hasta que Radar es apagado.  Cuando arrancas Radar todos los plugins son instanciados, esto es, por cada uno de los plugins que Radar encuentra en su directorio de plugins intenta crear un objeto. Este no es cualquier objeto, tiene que cumplir de alguna manera con lo que Radar espera que sea un plugin válido. Si Radar logra instanciar un cierto plugin sin problemas entonces procederá a configurarlo. Luego que ha sido configurado se lo agrega a un set de plugins. address : Esta es la dirección IP del cliente Radar que envió la respuesta a un chequeo. Este valor es un string. checks : Esta es una lista Python que contiene todos los objetos Checks que fueron actualizados por el servidor. Esta lista siempre esta asociada a un monitor particular, esto significa que la lista de chequeos hace referencia a un y solo un monitor. contacts : Esta es una lista Python que contiene todos los objetos Contacts relacionados a la respuesta de uno o más chequeos. Esta lista siempre esta asociada a un y solo un monitor. port : El puerto TCP del cliente Radar que envió la respuesta. Este es un valor integer. 