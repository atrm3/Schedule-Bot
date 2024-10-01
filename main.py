import discord
from discord.ext import commands
from discord.ui import Select, View
from discord import Intents

intents: Intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

all_schedule_events = []

@bot.event
async def on_ready() -> None:
    print(f'{bot.user} is now running')

    try:
        synced = await bot.tree.sync()
        print("Synced")
    except Exception as e:
        print(e)

@bot.tree.command(name="schedule_day")
async def schedule_day(interaction, earliest_start_time: int, latest_start_time: int, month: int, day : int, event_name: str) -> None:
    global all_schedule_events
    id_number = len(all_schedule_events) + 1
    users_available_time = {"id_number": id_number, "earliest_start_time": str(earliest_start_time)+":00", "latest_start_time": str(latest_start_time)+":00", "month": month, "day": day, "event_name" : event_name}
    all_schedule_events.append(users_available_time)
    times = []

    #Make sure that the start and end time are within 24
    if earliest_start_time < 0:
        earliest_start_time = 0

    if latest_start_time > 24:
        latest_start_time = 24

    if earliest_start_time + latest_start_time > 12 or earliest_start_time >= latest_start_time:
        latest_start_time = earliest_start_time + 12

    #Create the options
    for i in range(earliest_start_time, latest_start_time):
        times.append(discord.SelectOption(label= str(i)+":00"))
        times.append(discord.SelectOption(label= str(i)+":30"))

        users_available_time[str(i)+":00"] = []
        users_available_time[str(i)+":30"] = []
    
    times.append(discord.SelectOption(label= str(latest_start_time)+":00"))
    users_available_time[str(latest_start_time)+":00"] = []


    #Make the select menu
    select = Select(placeholder="Times", min_values = 1, max_values= len(times), options = times)

    #Responds to the user after they submitted their response
    async def my_callback(interaction):
        #Whenever a new submission comes in delete the last version
        for i in range(len(all_schedule_events)):
            if all_schedule_events[i]['id_number'] == id_number:
                del all_schedule_events[i]
                break

        #If the user decide to update the time they are avaliable remove all instance of their name
        for i in users_available_time:
            if interaction.user.global_name in users_available_time[i] and i != event_name:
                users_available_time[i].remove(interaction.user.global_name)

        for i in select.values:
            users_available_time[i].append(interaction.user.global_name)

        await interaction.response.send_message(users_available_time)
        all_schedule_events.append(users_available_time)

    select.callback = my_callback
    view = View()
    view.add_item(select)

    await interaction.response.send_message("Choose times when you are avaliable for "+ event_name +" on "+ str(month) + "/"+ str(day), view=view)
    return

@bot.tree.command(name="show_all_schedule_event_day")
async def show_all_schedule_event_day(interaction) -> None:
    global all_schedule_events

    #If there are no events say there is no events
    if all_schedule_events == []:
        await interaction.response.send_message("No event has been scheduled")
        return

    message = ("```Possible Starting Time | Date | Event Name\n")

    for event in all_schedule_events:
        date = str(event["month"]) +"/" + str(event["day"])
        possible_stating_time = event["earliest_start_time"]+ " - " + event["latest_start_time"]
        message += (possible_stating_time.ljust(23)+ "| " + date.ljust(4) + " | " + event["event_name"]+"\n")
    
    #Add quotes so dicord actually spaces thing evenly
    message += "```"
    await interaction.response.send_message(message)
    return

@bot.tree.command(name="delete_all_schedule_event_day")
async def delete_all_schedule_event_day(interaction) -> None:
    global all_schedule_events
    all_schedule_events = []
    return

@bot.tree.command(name="delete_schedule_event_day")
async def delete_all_schedule_event_day(interaction, event_name: str) -> None:
    global all_schedule_events
    for event in all_schedule_events:
        if all_schedule_events[event]["event_name"] == event_name:
            all_schedule_events.remove(event)
            break
    return

def main() -> None:
    bot.run("TOKENGOESHERE")
    return

if __name__ == "__main__": 
    main()