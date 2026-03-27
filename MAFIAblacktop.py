# meta developer: @ogoez1
from .. import loader, utils

@loader.tds
class MafiaTrackerMod(loader.Module):
    """Отслеживание наборов в Мафию и пересылка в выбранный чат"""
    strings = {"name": "MafiaTracker"}

    async def client_ready(self, client, db):
        self.db = db
        # Список чатов, которые МЫ СЛУШАЕМ (откуда берем)
        self.track_chats = self.db.get("MafiaTracker", "track", [])
        # Список чатов, КУДА МЫ КИДАЕМ (цель)
        self.target_chats = self.db.get("MafiaTracker", "target", [])
        # ID бота мафии
        self.bot_id = 1520369962

    @loader.command()
    async def trackchat(self, message):
        """/trackchat [id] - Добавить чат в список отслеживания (ОТКУДА ловить)"""
        args = utils.get_args_raw(message)
        cid = int(args) if args else message.chat_id
        if cid not in self.track_chats:
            self.track_chats.append(cid)
            self.db.set("MafiaTracker", "track", self.track_chats)
            await message.edit(f"<b>[Tracker]</b> Теперь слежу за чатом: <code>{cid}</code>")
        else:
            await message.edit("Этот чат уже отслеживается.")

    @loader.command()
    async def deltrack(self, message):
        """/deltrack [id] - Перестать отслеживать чат"""
        args = utils.get_args_raw(message)
        cid = int(args) if args else message.chat_id
        if cid in self.track_chats:
            self.track_chats.remove(cid)
            self.db.set("MafiaTracker", "track", self.track_chats)
            await message.edit(f"<b>[Tracker]</b> Чат <code>{cid}</code> удален из слежки.")

    @loader.command()
    async def addtarget(self, message):
        """/addtarget [id] - Куда пересылать сообщения (КУДА кидать)"""
        args = utils.get_args_raw(message)
        cid = int(args) if args else message.chat_id
        if cid not in self.target_chats:
            self.target_chats.append(cid)
            self.db.set("MafiaTracker", "target", self.target_chats)
            await message.edit(f"<b>[Tracker]</b> Наборы будут пересылаться в: <code>{cid}</code>")
        else:
            await message.edit("Этот чат уже в списке целей.")

    @loader.command()
    async def deltarget(self, message):
        """/deltarget [id] - Удалить чат из списка целей"""
        args = utils.get_args_raw(message)
        cid = int(args) if args else message.chat_id
        if cid in self.target_chats:
            self.target_chats.remove(cid)
            self.db.set("MafiaTracker", "target", self.target_chats)
            await message.edit(f"<b>[Tracker]</b> Чат <code>{cid}</code> удален из целей.")

    @loader.watcher(only_messages=True)
    async def watcher(self, message):
        # Проверяем: от нужного ли бота сообщение?
        if message.sender_id != self.bot_id:
            return
        
        # Проверяем: в том ли чате мы ловим?
        if message.chat_id not in self.track_chats:
            return

        # Проверяем текст сообщения (набор в игру)
        if "Ведётся набор в игру" in message.text:
            # Пересылаем сообщение во все целевые чаты
            for target in self.target_chats:
                try:
                    await message.forward_to(target)
                except Exception:
                    pass
