import discord
import interactions
import datetime

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
    log(f"Logged in as {bot.me.name} (ID: {bot.me.id})")
    log('---------------------------------------------')
    global qmRole
    qmRole = await interactions.get(
        bot,
        interactions.Role,
        object_id=1023740823625543720,
        parent_id=guildID
    )


###################################
#              QUEUE              #
###################################
@bot.command(
    name='queue',
    description="Add yourself to the Question Master Queue"
)
async def queue(ctx: interactions.CommandContext):
    member = ctx.author
    log(f"Queue({member})")

    # Handle duplicate queues
    if qotdQueue.count(member):
        await ctx.send("**rofl**, you are already in the queue dummy!")
        log(f"duplicate queue from {member}")
        return

    # If no one currently queued & no current QM
    if not qotdQueue:
        await giveQM(member)
        qotdQueue.append(member)
        await ctx.send(f"Congrats {member.mention}, you are now the Question Master!")
        return
    
    qotdQueue.append(member)
    await ctx.send(f"You have joined the queue at position **{len(qotdQueue) - 1}**.")
    #TODO: send the time that their question master reign will start


###################################
#             STATUS              #
###################################
@bot.command(
    name='status',
    description="View the status of the Question Master and Queue"
)
async def status(ctx: interactions.CommandContext):
    member = ctx.author
    log(f"Status({member})")

    if qotdQueue:
        msg = f"The current Question Master is **{qotdQueue[0]}**.\n"
        if qotdQueue[1:]:
            msg += f"Queued Members: {list(map(lambda member: member.name, qotdQueue[1:]))}"
        else:
            msg += "There are no users in the queue."
        await ctx.send(msg)
        return
    
    await ctx.send("There is no current Question Master, the queue is empty.\nUse /queue to become the Question Master right now!")



###################################
#             CYCLE               #
###################################
# TODO: Trigger every midnight
@bot.command(
    name='cycle',
    description="Manually cycle in the next Question Master",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR
)
async def cycleQM(ctx: interactions.CommandContext):
    log(f"Cycle({ctx.author})")
    if qotdQueue:
        oldQM = qotdQueue.pop(0)
        await oldQM.remove_role(qmRole, guildID)
        
        if qotdQueue:
            newQM = qotdQueue[0]
            await giveQM(newQM)
            await ctx.send(f"Successfully cycled QM: **{oldQM.name}** has been dethroned. Congrats {newQM.mention}, you are now the Question Master!")
            return
        else:
            await ctx.send(f"Successfully cycled QM: **{oldQM.name}** has been dethroned, there is no new Question Master.")
            return
    
    await ctx.send("Cycle has no effect as there is no current Question Master.")



###################################
#        HELPER FUNCTIONS         #
###################################


# Give QM role to Member
async def giveQM(member: discord.Member):
    try:
        await member.add_role(qmRole, guildID)
    except interactions.api.error.LibraryException as e:
        log(f"Error giving qm role: LibraryException: {e}")


def log(msg):
    print(f"{datetime.datetime.now()} | {msg}")
    

bot.start()
