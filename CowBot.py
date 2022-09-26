import discord
import interactions

from os import environ
from dotenv import load_dotenv

load_dotenv()

token = environ["TOKEN"]
guildID = 367758891179704339

bot = interactions.Client(token=token)

# Index 0 will represent person currently with QM
# rest of queue will be people waiting for QM
# Members cannot queue while they are already queue'd
# QMs cannot queue until their reign has ended
qotdQueue = []
qmRole = ''

@bot.event
async def on_ready():
    print(f"Logged in as {bot.me.name} (ID: {bot.me.id})")
    print('-------')
    global qmRole
    qmRole = await interactions.get(
        bot,
        interactions.Role,
        object_id=1023740823625543720,
        parent_id=guildID
    )


@bot.command(
    name='queue',
    description="Add yourself to the Question Master Queue"
)
async def queue(ctx: interactions.CommandContext):
    member = ctx.author
    print(f"Queue({member})")

    # Handle duplicate queues
    if qotdQueue.count(member):
        await ctx.send("rofl, you are already in the queue dummy!")
        print(f"duplicate queue from {member}")
        return

    # If no one currently queued & no current QM
    if not qotdQueue:
        await giveQM(member)
    
    qotdQueue.append(member)

# Give QM role to Member
async def giveQM(member: discord.Member):
    try:
        await member.add_role(qmRole, guildID)
    except interactions.api.error.LibraryException as e:
        print(f"Error giving qm role: LibraryException: {e}")

# Remove current QM (if exists)
# Inaugurate next QM (if exists)
async def cycleQM():
    if qotdQueue:
        member = qotdQueue.pop()
        member.remove_role(qmRole, guildID)
        
        if qotdQueue:
            newQM = qotdQueue[0]
            await giveQM(newQM)

bot.start()
