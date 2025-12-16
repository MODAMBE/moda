# messages/consumers.py

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

# ================================
# Chat Consumer
# ================================
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.discussion_id = self.scope['url_route']['kwargs']['discussion_id']
        self.room_group_name = f"discussion_{self.discussion_id}"

        user = self.scope.get('user')
        if not user or user.is_anonymous:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        try:
            await self.send_pending_messages_for_user(user.id)
        except Exception as e:
            logger.exception("Erreur send_pending_messages_for_user: %s", e)

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        except Exception:
            pass

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            data = json.loads(text_data)
        except Exception:
            return

        # ACK message
        if data.get("ack"):
            message_id = data["ack"]
            await self.mark_message_read(message_id)
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "ack_event", "message_id": message_id}
            )
            return

        # PAGINATION
        if data.get("action") == "paginate":
            try:
                page = int(data.get("page", 1))
            except Exception:
                page = 1

            msgs = await self.get_old_messages(page=page)
            await self.send(text_data=json.dumps({"type": "paginate", "messages": msgs}))
            return

        # NOUVEAU MESSAGE
        try:
            user = self.scope.get("user")
            expediteur_id = data.get("expediteur_id") or (user.id if user else None)
            if expediteur_id is None:
                return

            contenu = data.get("message", "") or ""
            fichier_url = data.get("fichier_url")
            mtype = data.get("type_message") if data.get("type_message") is not None else data.get("type", "texte")

            msg = await self.create_message(expediteur_id, contenu, fichier_url, mtype)

        except Exception as e:
            logger.exception("Erreur create_message: %s", e)
            return

        payload = {
            "event": "message",
            "message_id": msg["id"],
            "expediteur": msg["expediteur_username"],
            "expediteur_id": msg["expediteur_id"],
            "message": msg["contenu"],
            "fichier_url": msg["fichier_url"],
            "type_message": msg["type"],
            "date_envoye": msg["date_envoye"],
            "lu": msg["lu"],
        }

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "chat_message", "payload": payload}
        )

    async def chat_message(self, event):
        try:
            await self.send(text_data=json.dumps(event["payload"]))
        except Exception as e:
            logger.exception("Erreur envoi chat_message: %s", e)

    async def ack_event(self, event):
        try:
            await self.send(text_data=json.dumps({
                "event": "ack",
                "message_id": event["message_id"]
            }))
        except Exception as e:
            logger.exception("Erreur envoi ack_event: %s", e)

    # ---------------------------
    # Helpers DB (imports paresseux)
    # ---------------------------
    @database_sync_to_async
    def create_message(self, expediteur_id, contenu, fichier_url, mtype):
        User = get_user_model()
        from .models import Discussion, Message

        expediteur = User.objects.get(id=expediteur_id)
        discussion = Discussion.objects.get(id=self.discussion_id)

        msg = Message.objects.create(
            discussion=discussion,
            expediteur=expediteur,
            contenu=contenu or "",
            type=mtype
        )

        if fichier_url:
            try:
                msg.fichier = fichier_url
                msg.save()
            except Exception:
                pass

        return {
            "id": msg.id,
            "expediteur_username": expediteur.username,
            "expediteur_id": expediteur.id,
            "contenu": msg.contenu,
            "fichier_url": (msg.fichier.url if getattr(msg, "fichier", None) else fichier_url),
            "type": msg.type,
            "date_envoye": msg.date_envoye.isoformat(),
            "lu": msg.lu,
        }

    @database_sync_to_async
    def mark_message_read(self, message_id):
        from .models import Message
        try:
            m = Message.objects.get(id=message_id)
            m.lu = True
            m.save()
            return True
        except Exception:
            return False

    @database_sync_to_async
    def get_old_messages(self, page=1, page_size=20):
        from .models import Message

        qs = Message.objects.filter(
            discussion__id=self.discussion_id
        ).order_by("-date_envoye")

        start = max((page - 1) * page_size, 0)
        slice_qs = qs[start:start + page_size]

        items = [{
            "id": m.id,
            "expediteur": m.expediteur.username,
            "expediteur_id": m.expediteur.id,
            "message": m.contenu,
            "fichier_url": m.fichier.url if getattr(m, "fichier", None) else None,
            "type_message": m.type,
            "date_envoye": m.date_envoye.isoformat(),
            "lu": m.lu,
        } for m in slice_qs]

        return list(reversed(items))

    @database_sync_to_async
    def fetch_pending_for_user(self, user_id):
        from .models import Message

        qs = Message.objects.filter(
            discussion__id=self.discussion_id,
            lu=False
        ).exclude(expediteur__id=user_id).order_by("date_envoye")

        return [{
            "id": m.id,
            "expediteur": m.expediteur.username,
            "expediteur_id": m.expediteur.id,
            "message": m.contenu,
            "fichier_url": m.fichier.url if getattr(m, "fichier", None) else None,
            "type_message": m.type,
            "date_envoye": m.date_envoye.isoformat(),
            "lu": m.lu,
        } for m in qs]

    async def send_pending_messages_for_user(self, user_id):
        pending = await self.fetch_pending_for_user(user_id)
        for m in pending:
            try:
                await self.send(text_data=json.dumps({
                    "event": "message",
                    "message_id": m["id"],
                    "expediteur": m["expediteur"],
                    "expediteur_id": m["expediteur_id"],
                    "message": m["message"],
                    "fichier_url": m["fichier_url"],
                    "type_message": m["type_message"],
                    "date_envoye": m["date_envoye"],
                    "lu": m["lu"],
                }))
            except Exception as e:
                logger.exception("Erreur envoi pending message: %s", e)


# ================================
# Call (Audio / Video) Consumer
# ================================
class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.appel_id = self.scope['url_route']['kwargs']['appel_id']
        self.room_group_name = f"call_{self.appel_id}"

        user = self.scope.get('user')
        if not user or user.is_anonymous:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        try:
            payload = {
                "event": "participant_connected",
                "user_id": user.id,
                "username": user.username,
                "avatar": (
                    user.profile.image.url
                    if getattr(user, "profile", None)
                    and getattr(user.profile, "image", None)
                    else None
                ),
                "numero": getattr(user.profile, "telephone", "") if getattr(user, "profile", None) else ""
            }
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "call_status", "message": payload}
            )
        except Exception as e:
            logger.exception("Erreur envoi call connect status: %s", e)

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        except Exception:
            pass

        user = self.scope.get("user")
        if user and not user.is_anonymous:
            payload = {
                "event": "participant_disconnected",
                "user_id": user.id,
                "username": user.username
            }
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "call_status", "message": payload}
            )

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            data = json.loads(text_data)
        except Exception:
            return

        msg_type = data.get("type")

        if msg_type in ["offer", "answer", "candidate", "ice"]:
            if msg_type == "ice":
                data["type"] = "candidate"

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "call_message", "message": data, "sender": self.channel_name}
            )

        elif msg_type == "hangup":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "call_message",
                    "message": {"type": "hangup", "user_id": self.scope["user"].id},
                    "sender": self.channel_name
                }
            )
        else:
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "call_message", "message": data, "sender": self.channel_name}
            )

    async def call_message(self, event):
        if event.get("sender") == self.channel_name:
            return

        try:
            await self.send(text_data=json.dumps(event["message"]))
        except Exception as e:
            logger.exception("Erreur envoi call_message: %s", e)

    async def call_status(self, event):
        try:
            msg = event.get("message")
            if isinstance(msg, str):
                await self.send(text_data=msg)
            else:
                await self.send(text_data=json.dumps(msg))
        except Exception as e:
            logger.exception("Erreur envoi call_status: %s", e)
