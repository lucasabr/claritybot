# Raffle Objects contain the author and name of the raffle as well 
# as important information on where the raffle is created such as message, guild and channel
class Raffle:
    def __init__(self, author, name, message, guild, channel):
        self.author = author
        self.name = name
        self.message = message
        self.guild = guild
        self.channel = channel
        
   


