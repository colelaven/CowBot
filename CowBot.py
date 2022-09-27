import pickle
import interactions
import aiocron
import os

from datetime import datetime
from os import environ
from dotenv import load_dotenv

load_dotenv()

token = environ["TOKEN"]
guildID = 491680664769265664
channelID = 851942788936630292
roleID = 976537125984038924

bot = interactions.Client(token=token)


@bot.event
async def on_ready():
    log(f"Logged in as {bot.me.name} (ID: {bot.me.id})")
    log('---------------------------------------------')
    global qmRole
    qmRole = await interactions.get(
        bot,
        interactions.Role,
        object_id=roleID,
        parent_id=guildID
    )

    global channel
    channel = await interactions.get(
        bot,
        interactions.Channel,
        object_id=channelID
    )

    # Index 0 represents current QM
    # Index 1+ are users queued for QM
    # Users cannot queue while they are already queue'd
    # QM cannot queue until their reign has ended
    global qotdQueue
    global qmStartTime
    qmStartTime = 0
    qotdQueue = []
    if os.path.exists('state.pkl'):
        try:
            qotdQueue, qmStartTime = await loadState()
            log(f"Restart Detected")
            log(f"Loaded state: Queue: {qotdQueue} | qmStartTime: {qmStartTime}")
            await removeALlQMRoles()
            if qotdQueue:
                await giveQM(qotdQueue[0])
        except Exception as e:
            log("Error loading state: " + repr(e))
            await clearHelper()
    else:
        await clearHelper()
    
    

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
        global qmStartTime
        qmStartTime = datetime.now()
        await ctx.send(f"Congrats {member.mention}, you are now the Question Master!")
    else:
        qotdQueue.append(member)
        await ctx.send(f"You have joined the queue at position **{len(qotdQueue) - 1}**.\nI will ping you when your day comes.")
    
    saveState()


###################################
#             Leave               #
###################################
@bot.command(
    name='leave',
    description="Remove yourself from the queue"
)
async def leave(ctx: interactions.CommandContext):
    member = ctx.author
    log(f"Leave({member})")

    if qotdQueue.count(member):
        if qotdQueue.index(member):
            qotdQueue.pop(qotdQueue.index(member))
            saveState()
            await ctx.send("You've successfully left the queue.")
        else:
            await ctx.send("You're the Question Master, dummy!\nDon't use leave, use /forfeit if you want forfeit the rest of your reign.")
        
    else:
        await ctx.send("You can't leave the queue if you aren't in it, dummy!")


###################################
#            Forfeit              #
###################################
@bot.command(
    name='forfeit',
    description="Forfeit the remainder of your Question Master reign"
)
async def forfeit(ctx: interactions.CommandContext):
    member = ctx.author
    log(f"Forfeit({member})")
    if qotdQueue and qotdQueue[0] == member:
        await cycleHelper(ctx)
    else:
        await ctx.send("The forfeit command is only for Question Masters, dummy!")


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
    await statusHelper(ctx)

async def statusHelper(receiver):
    if qotdQueue:
        msg = f"The current Question Master is **{qotdQueue[0]}**.\n"
        if qotdQueue[1:]:
                msg += f"Queued Members: {[user.name for user in qotdQueue[1:]]}"
        else:
            msg += "There are no users in the queue."
        await receiver.send(msg)
        return
    
    await receiver.send("There is no current Question Master, the queue is empty.\nUse /queue to become the Question Master right now!")



###################################
#             CYCLE               #
###################################
@bot.command(
    name='cycle',
    description="Manually cycle the Question Master",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR
)
async def manualCycle(ctx: interactions.CommandContext):
    log(f"Cycle({ctx.author})")
    status = await cycleHelper(ctx)
    if status == -1:
        await ctx.send("Congrats, you did nothing! There was no Question Master to begin with, dummy.")

async def cycleHelper(receiver):
    if qotdQueue:
        oldQM = qotdQueue.pop(0)
        await removeQM(oldQM)
        global qmStartTime
        qmStartTime = 0
        
        if qotdQueue:
            newQM = qotdQueue[0]
            await giveQM(newQM)
            qmStartTime = datetime.now()
            await receiver.send(f"Question Master has been cycled: **{oldQM.name}** has been dethroned.\nCongrats {newQM.mention}, you are now the Question Master!")
        else:
            await receiver.send(f"Question Master has been cycled: **{oldQM.name}** has been dethroned.\nThere is no new Question Master.")
        
        saveState()
        return 0
    else:
        return -1

# Trigger Cycle every day at Midnight
@aiocron.crontab('0 0 * * *')
async def autoCycle():
    log("AutoTriggering Cycle")
    if qotdQueue and qmStartTime:
        timedif = datetime.now() - qmStartTime
        if timedif.days == 0 and timedif.seconds < 4*3600:
            log("AutoTriggered Cycle: QM is too recent: No effect.")
            return  
    status = await cycleHelper(channel)
    if status == -1:
        log("AutoTriggered Cycle: No state: No effect.")
    else:
        log(f"AutoTriggered Cycle: case({status}).")


###################################
#             CLEAR               #
###################################
@bot.command(
    name='clear',
    description="Manually clear all Question Master related data",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR
)
async def clear(ctx: interactions.CommandContext):
    log(f"Clear({ctx.author})")
    await clearHelper()
    await ctx.send("Clear was successful")

async def clearHelper():
    await removeALlQMRoles()
    global qotdQueue
    global qmStartTime
    qotdQueue = []
    qmStartTime = 0
    saveState()




###################################
#        HELPER FUNCTIONS         #
###################################

# Clears the QM role from everyone in the server
async def removeALlQMRoles():
    guild = await interactions.get(
        bot,
        interactions.Guild,
        object_id=guildID
    )
    [await removeQM(member) for member in guild.members]


# Give QM role to Member
async def giveQM(member: interactions.api.models.Member):
    try:
        await member.add_role(qmRole, guildID)
    except interactions.api.error.LibraryException as e:
        log(f"Error giving qm role: LibraryException: {e}")

# Remove QM role from Member
async def removeQM(member: interactions.api.models.Member):
    try:
        await member.remove_role(qmRole, guildID)
    except interactions.api.error.LibraryException as e:
        log(f"Error removing qm role: LibraryException: {e}")

def saveState():
    idList = [int(user.id) for user in qotdQueue]
    state = {
        'idList' : idList,
        'qmStartTime' : qmStartTime
    }
    log('saving state, state: ' + str(state))
    with open('state.pkl', 'wb') as f:
        pickle.dump(state, f)

async def loadState():
    with open('state.pkl', 'rb') as f:
        try:
            state = pickle.load(f)
        except Exception as e:
            log('loadState exception caught: ' + repr(e))
            state = {
                'idList' : [],
                'qmStartTime' : 0
            }
        if state['qmStartTime']:
            loadedStartTime = state['qmStartTime']
        else:
            loadedStartTime = 0
        log('Loaded state, state: ' + str(state))
        return [await idToMember(id) for id in state['idList']], loadedStartTime


async def idToMember(id):
    return await interactions.get(
        bot,
        interactions.Member,
        object_id=id,
        parent_id=guildID
    )

def log(msg):
    print(f"{datetime.now()} | {msg}", flush=True)
    

bot.start()
