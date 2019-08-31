import os
import os.path
from sys import platform

from rivescript import RiveScript


class ChatBot(object):
    def __init__(self, guild):
        self.rive_bot = RiveScript()
        self.rive_bot.set_handler("python", None)
        self.rive_bot.load_directory('brain')
        self.rive_bot.sort_replies()
        self.rive_bot.set_global('guild', str(guild.name))

    def get_response(self, message, user):
        return self.rive_bot.reply(user.name, message)

    def load_file(self, f):
        if os.path.isfile(f):
            try:
                self.rive_bot.load_file(f)
                self.rive_bot.sort_replies()
            except Exception as e:
                if platform == "linux" or platform == "linux2":
                    os.system('rm {}'.format(f))
                elif platform == "win32":
                    os.system('del {}'.format(f.replace('/', '\\')))
                return 'ERR02', str(e)
            return 'ERR00', None
        else:
            return 'ERR01', None

    @staticmethod
    def remove_file(f):
        if os.path.isfile(f):
            try:
                if platform == "linux" or platform == "linux2":
                    os.system('rm {}'.format(f))
                elif platform == "win32":
                    os.system('del {}'.format(f.replace('/', '\\')))
            except:
                return 'ERR02'
            return 'ERR00'

        else:
            return 'ERR01'

    def reload(self, brain=True):
        srvr = self.rive_bot.get_global('guild')
        self.rive_bot = RiveScript()
        self.rive_bot.set_handler("python", None)
        if brain:
            self.rive_bot.load_directory('brain')
        self.rive_bot.sort_replies()
        self.rive_bot.set_global('guild', str(srvr))


if __name__ == '__main__':

    class Usr(object):
        def __init__(self):
            self.name = 'bain'
            self.id = '430369724275097612'


    class Gld(object):
        def __init__(self, a):
            self.name = a
            self.id = '1'


    usr = Usr()
    gld = Gld('test')

    bot = ChatBot(gld)
    while True:
        inp = input('> ')
        print(bot.get_response(inp, usr))
