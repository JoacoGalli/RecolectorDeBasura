# TrabajoProfesional

1)nos conectamos a mosquitto, con un usario y password para que sea mas seguro nuestra conexion, levantamos el docker-compose con docker-compose up -d (el -d es para que se ejecute en modo demonio, lo que hace es ejecutarse pero en background)
2) Nos conectamos a Node Red para eso levantamos el docker-compose (tenemos que estar parados en la carpeta donde esta el achivo docker-compose.yaml)
entramos en localhost:1880 y tenemos la version grafica de node red, levantamos el flowgraph que arme con sensores que depositan las mediciones en influx (darle arriba a la derecha a Deploy)
3) Influxdb. Para activar influx, tenemos que correr el docker-compose que esta en la carpeta influx1. Corriendo Node red, mandamos por mqtt las mediciones y se guardan en influxdb. Para saber que base de datos tenemos creada, corremos:
• influx -username admin -password 123456
• use sensores
• show measurements
• select * from "sensor/sensor1" limit 5
estos pasos son para poder ver que mediciones esta guardando en la base de datos (tambien se pueden ver en node-red agregando un degug y observando en la solapa debug arriba a la derecha)
4) Conviero la data de mqtt a json (para eso agrego un bloque json en nodered y lo pongo que siempre convierta la data a string)
