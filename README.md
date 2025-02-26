
# TAY-TICKETS.py

Un bot de tickets de discord programado en python


## Colaboradores

- [@TayArin](https://github.com/El-TayArin)
- [@SusoDiz](https://github.com/SusoDiz)


## Características

- Configuracion simple
- Tickets por categoria
- Logs


## Requisitos previos

- Python instalado (Probado en la v3.12)
- Un bot de Discord registrado y su token 


## Como usarlo

Clona el repositorio:
```
git clone https://github.com/El-TayArin/Tay-Tickets.py.git
```

Instala las dependencias:
```
pip -m install -r requirements.txt
```

Crear un archivo ".env" en el que añadiras:
```plaintext # .env
TOKEN=ElTokenDeTuBotDeDiscord
```
Ademas, debes editar config.json para usar las IDs de tu preferencia:
```json
{
    "bot_prefix": "!",

    "ticket_channel_id": "1343259655387746355",
    "ticket_message": "🎫 Presiona el botón para abrir un ticket y seleccionar la categoría.",

    "ticket_categories": {
        "soporte_general": "1343259614258528357",
        "apelaciones": "1343259614258528357",
        "compras": "1343259614258528357"
    },

    "log_channel_id": "1343259679295541319"
}
```

Ejecuta el bot:
```
py .\bot.py
```
