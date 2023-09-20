import irc.bot
import os
import re
import time

class IRC(irc.bot.SingleServerIRCBot):
    thread_lock = None
    running = True

    settings = None
    connection = None
    discord = None

    def __init__(self, settings):
        irc.client.ServerConnection.buffer_class.encoding = "latin-1"
        irc.bot.SingleServerIRCBot.__init__(
            self,
            [(settings["irc"]["server"], int(settings["irc"]["port"]))],
            "Discord",
            "Discord",
        )

        self.settings = settings["irc"]

    def set_discord(self, discordc):
        self.discord = discordc

    def set_thread_lock(self, lock):
        self.thread_lock = lock

    def send_my_message(self, message):
        self.connection.privmsg("#" + self.settings["channel"], message.strip())

    def close(self):
        self.running = False
        self.connection.quit()

    def set_running(self, value):
        self.running = value  # Set the running flag

    def on_nicknameinuse(self, connection, event):
        connection.nick(connection.get_nickname() + "_")

    def on_welcome(self, connection, event):
        self.connection = connection
        channel = "#" + self.settings["channel"]

        connection.join(channel)

        with self.thread_lock:
            print("[IRC] Connected to server")

    def on_join(self, connection, event):
        with self.thread_lock:
            if "#" + self.settings["channel"] == "#":
                print("[ERROR] IRC Channel Invalid")
                os._exit(1)
            else:
                print("[IRC] Connected to channel")

    def on_pubmsg(self, connection, event):
        message = event.arguments[0].strip()
        message = "**[{:}]** {:s}".format(
            re.sub(r"(]|-|\\|[`*_{}[()#+.!])", r"\\\1", event.source.nick), message
        )

        with self.thread_lock:
            print("[IRC] " + message)

        self.discord.send_my_message(message)

    def run(self):
        self.start()