# Instrucciones para ejecutar el Interceptor de Residuos Flotantes.

Este README proporciona instrucciones detalladas sobre cómo ejecutar el programa del IRF. Este programa automatiza el control del recolector, recopila métricas a través de MQTT, las almacena en una base de datos InfluxDB y muestra estas métricas en Grafana.

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalados los siguientes componentes en tu sistema:

- **Docker Desktop**: Descárgalo e instálalo desde la [página oficial de Docker](https://www.docker.com/products/docker-desktop).

## Ejecución en Windows

### Configuración de WSL2 y Docker para Linux

1. Inicia Windows Subsystem for Linux 2 (WSL2) abriendo una terminal y ejecutando el comando:
   
   ```
   wsl.exe --install Ubuntu
   ```
   
   Sigue las instrucciones para crear un usuario y contraseña para tu distribución de Ubuntu en WSL2.

2. Una vez instalado Ubuntu en WSL2, abre la terminal de WSL2 y instala Docker para Linux siguiendo los pasos adecuados para tu distribución. Esto permitirá ejecutar contenedores de Docker dentro de WSL2.

### Configuración mediante Docker Desktop (Interfaz Gráfica)

1. Clona el repositorio del Recolector de Basura desde GitHub.

2. Abre Docker Desktop y asegúrate de que esté en funcionamiento.

3. En la terminal de WSL2, navega hasta el directorio del repositorio clonado.

4. Ejecuta el siguiente comando para levantar los servicios de MQTT, InfluxDB y Grafana utilizando Docker Compose:

   ```
   docker-compose up -d
   ```
   
   Si aún no tienes instalado `docker-compose`, sigue las instrucciones en [este enlace](https://docs.docker.com/compose/install/) para su instalación.

5. Abre un navegador web y accede al panel de control de Grafana utilizando la URL: [http://localhost:3000](http://localhost:3000). Ingresa las credenciales de inicio de sesión si es necesario.

6. Para acceder a la base de datos InfluxDB, utiliza la URL: [http://localhost:8086](http://localhost:8086).

7. Ejecuta el script `mqtt_to_influx.py`, asegurándote de modificar la dirección IP correspondiente a la Raspberry Pi.

¡Listo! Ahora podrás visualizar las métricas que el recolector envía mediante MQTT en el panel de control de Grafana.

## Ejecución en Linux

Las instrucciones son similares en Linux, con la diferencia de que no necesitarás configurar WSL2, ya que Docker se ejecutará directamente en tu sistema.

1. Clona el repositorio del Recolector de Basura desde GitHub.

2. Abre una terminal y navega hasta el directorio del repositorio clonado.

3. Ejecuta el siguiente comando para levantar los servicios de MQTT, InfluxDB y Grafana utilizando Docker Compose:

   ```
   docker-compose up -d
   ```

4. Sigue los pasos 5, 6 y 7 de la sección anterior (Configuración mediante Docker Desktop) para acceder a Grafana y a la base de datos InfluxDB.

5. Ejecuta el script `mqtt_to_influx.py`, asegurándote de modificar la dirección IP correspondiente a la Raspberry Pi.

Ahora puedes explorar las métricas en Grafana y la base de datos InfluxDB.

**Nota**: Estas instrucciones pueden estar sujetas a cambios según las actualizaciones de las herramientas y sistemas operativos. Asegúrate de consultar la documentación oficial de Docker, Grafana e InfluxDB en caso de problemas o diferencias en las instrucciones.
