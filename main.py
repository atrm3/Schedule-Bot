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

#Schedules an event for a single day
@bot.tree.command(name="schedule_day", description= "Hours must be in 24 hours time and earliest and latest start time must be within 12 hours")
async def schedule_day(interaction, earliest_start_time: int, latest_start_time: int, month: int, day : int, event_name: str) -> None:
    global all_schedule_events
    id_number = len(all_schedule_events) + 1
    users_available_time = {"id_number": id_number, "earliest_start_time": str(earliest_start_time)+":00", "latest_start_time": str(latest_start_time)+":00", "month": month, "day": day, "event_name" : event_name}
    all_schedule_events.append(users_available_time)
    times = []

    #Make sure that the start and end time are within 24
    if earliest_start_time < 0 or earliest_start_time > 23:
        await interaction.response.send_message("Please enter a valid earliest starting time")
        return

    if latest_start_time > 24 or latest_start_time < 1:
        await interaction.response.send_message("Please enter a valid latest starting time")
        return

    if earliest_start_time + 12 < latest_start_time:
        await interaction.response.send_message("Latest start time cannot be more than earliest start time by 13 or more")
        return

    if earliest_start_time >= latest_start_time:
        await interaction.response.send_message("Earliest start time can not be more or equal than latest start time")
        return
    
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

#Show the availability of users for a certain event
@bot.tree.command(name="show_availability_day")
async def show_availability_day(interaction, event_name: str) -> None:
    global all_schedule_events
    message = event_name + " could not be found"
    for event in range(len(all_schedule_events)):
        if all_schedule_events[event]["event_name"] == event_name:
            #Construct the message to be sent
            message = "```Possible Starting Time | Date  | Event Name\n"
            date = str(event["month"]) +"/" + str(event["day"])
            possible_stating_time = event["earliest_start_time"]+ " - " + event["latest_start_time"]
            message += (possible_stating_time.ljust(23)+ "| " + date.ljust(5) + " | " + event["event_name"]+"\n")
            message += "```"
            break
    await interaction.response.send_message(message)
    return

#Show all events and their respective information
@bot.tree.command(name="show_all_schedule_event_day")
async def show_all_schedule_event_day(interaction) -> None:
    global all_schedule_events

    #If there are no events say there is no events
    if all_schedule_events == []:
        await interaction.response.send_message("No events have been scheduled")
        return

    #Format the message to be sent
    message = ("```Possible Starting Time | Date  | Event Name\n")

    for event in all_schedule_events:
        date = str(event["month"]) +"/" + str(event["day"])
        possible_stating_time = event["earliest_start_time"]+ " - " + event["latest_start_time"]
        message += (possible_stating_time.ljust(23)+ "| " + date.ljust(5) + " | " + event["event_name"]+"\n")
    
    #Add quotes so dicord actually spaces thing evenly
    message += "```"
    await interaction.response.send_message(message)
    return

#Clear all schedule event
@bot.tree.command(name="delete_all_schedule_event_day")
async def delete_all_schedule_event_day(interaction) -> None:
    global all_schedule_events
    all_schedule_events = []
    await interaction.response.send_message("All events have been deleted")
    return

#Delete a single event
@bot.tree.command(name="delete_schedule_event_day")
async def delete_all_schedule_event_day(interaction, event_name: str) -> None:
    global all_schedule_events
    message = event_name +" could not be found"
    for event in range(len(all_schedule_events)):
        if all_schedule_events[event]["event_name"] == event_name:
            all_schedule_events.pop(event)
            message = event_name+" has been deleted"
            break
    await interaction.response.send_message(message)
    return

def main() -> None:
    bot.run("Token goes here")
    return

if __name__ == "__main__": 
    main()