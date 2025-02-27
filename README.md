
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
        "soporte_general": {
            "category_id": "1343259614258528357",
            "support_role_id": "1344736498829758584",
            "display_name": "🔧 Soporte General"
        },
        "apelaciones": {
            "category_id": "1343259614258528357",
            "support_role_id": "1344736498829758584",
            "display_name": "Apelaciones"
        },
        "compras": {
            "category_id": "1343259614258528357",
            "support_role_id": "1344736498829758584",
            "display_name": "Compras"
        }
    },

    "log_channel_id": "1344736498829758584"
}
```

Ejecuta el bot:
```
py .\bot.py
```
