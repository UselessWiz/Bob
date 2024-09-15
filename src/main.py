# Import all dependancies
import ollama
import discord
import os
import datetime
import math
import random
import asyncio

import json

# Audio related initialisation
import ffmpeg

# Scan the audio directory for possible audio files to use when the bot joins vc.
# These reload whenever the bot is called to vc.
voice_lines = os.listdir("src/audio")
print(f"Current possible voice lines: {voice_lines}")

# Do dotenv stuff. System prompt is in dotenv.
from dotenv import load_dotenv
load_dotenv()

# Create a discord client. This is simple enough that it doesn't need to use the bot client, plus the bot client is based around giving it
# commands, which doesn't happen with this bot.
class DiscordClient(discord.Client):
    token = os.getenv('DISCORD_TOKEN')
    system_prompt = os.getenv('SYSTEM_PROMPT')
    
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print(f'System Prompt: {self.system_prompt}')
        print('------')

    # When a message is received.
    async def on_message(self, message):
        # DO NOT RESPOND TO ITSELF
        if message.author == client.user:
            print("Message not relavent as it was sent by me")
            return
        
        # Check user defined phrases from the src/phrases.json file for specific response phrases. 
        # Bob will respond to all messages with these phrase, even if he isn't mentioned.
        if await self.check_phrases(message):
            return

        # This ain't foolproof, but if someone sends a message with the words "join" and "vc", join the vc with the most people in it and play sound.
        if (client.user.mentioned_in(message) and "join" in message.content and "vc" in message.content and isinstance(message.channel, discord.channel.TextChannel)):
            await self.join_vc(message)
            return

        # Otherwise, check if bob is mentioned normally
        if (client.user.mentioned_in(message) or isinstance(message.channel, discord.channel.DMChannel)):
            await self.send_generated_message(message)

    async def check_phrases(self, message) -> bool:
        with open('src/phrases.json', 'r') as file:
            phrases = json.load(file)

        for phrase in phrases["phrases"]:
            if phrase["phrase"] in message.content.lower():
                print(f"Phrase {(phrase['phrase'])} found in message from {message.author} to {message.channel}.")
                await message.channel.send(phrase["response"])
                return True
            
        return False
    
    # Small issue, playing audio is not asyncronous, therefore keep audio snippets short so ai generation doesnt kill itself when it gets audio
    async def join_vc(self, message):
        print(f"Request to join VC from {message.author} in {message.guild}")
        voice_lines = os.listdir("src/audio")

        channel_list = message.guild.voice_channels

        # Check which channel has the most people who will witness the chaos and join that one.
        channel_to_join = [0, 0]
        for i in range(len(channel_list)):
            if (len(channel_list[i].members) > channel_to_join[1]):
                channel_to_join = [i, len(channel_list[i].members)]

        print(f"Joining Channel {channel_list[channel_to_join[0]].id}")

        # Actually join the VC
        voice_client = await channel_list[channel_to_join[0]].connect()

        # Pick a random voice line and load it for the player.
        audio = f"src/audio/{random.choice(voice_lines)}"
        source = await discord.FFmpegOpusAudio.from_probe(audio)

        # Wait a second after joining, then play the file, then wait a second, then disconnect.
        await asyncio.sleep(0.5)
        voice_client.play(source, bandwidth='medium', bitrate=32)
        await asyncio.sleep(float(ffmpeg.probe(audio)['format']['duration']) + 0.5) 
        await voice_client.disconnect()

    async def send_generated_message(self, message) -> None:        
        # Reload dotenv to update system_prompt
        load_dotenv(verbose=True, override=True)
        self.system_prompt = os.getenv('SYSTEM_PROMPT')

        # Replace his user.id string with his name for the prompt.
        print(f'{datetime.datetime.now()} INFO \t {message.author} sent a message mentioning the bot\n\tMessage: {message.content}\n\t{message}')

        messages = [{"role": "User", "content": message.content}]
        reply = message 

        # Get all replies to messages. This may need to be capped.
        while True:
            # Stop the loop if it's at the top of the chain.
            if reply.reference == None:
                break
                
            # Get the next message
            reply = await message.channel.fetch_message(reply.reference.message_id)

            # Fill in conversation details.
            if reply.author == client.user:
                role = "Assistant"
            else:
                role = "User"

            messages.append({"role": role, "content": reply.content})

        # Add the system prompt and then reverse the list. We go from most recent to least recent, so this must be reveresed in order to get the correct conversation
        messages.append({"role": "system", "content": self.system_prompt})
        messages.reverse()
            
        # Remove any traces of the client's user id in the conversation, replacing it with the bot's name.
        for item in messages:
            item['content'].replace(f'<@!{client.user.id}>', 'Bob')

        print(messages)

        # Start typing and generate the message.
        async with message.channel.typing():
            response = await generate_chat(messages)

        # Send the message. It splits the message in multiple parts if its too long, replying to the original on only the first message.
        for part in range(len(response)):
            if response[part] != "":
                response[part].replace(f'<@!{client.user.id}>', 'Bob') # Double check and be sure only Bob is mentioned.
                await message.channel.send(response[part], reference=message)

# Generate a prompt. This does not use the history of the message, only the current message and the system prompt.
async def generate_message(prompt, system):
    response = await ollama.AsyncClient().generate(model='llama2-uncensored', prompt=prompt, system=system)
    print(f'\tResponse: {response}')
    return await process_response(response['response'])

# Generate a chat. This uses all messages.
async def generate_chat(messages):
    response = await ollama.AsyncClient().chat(model='llama2-uncensored', messages=messages)
    print(f'\tResponse: {response}')
    return await process_response(response['message']['content'])

# Format any responses received from the bot.
async def process_response(response):
    # Split the message as needed. This if else isn't strictly necessary.
    if len(response) > 2000:
        response = await chunkstring(response, 2000)
    else:
        response = [response]

    return response

# Actually handle the splitting
async def chunkstring(string, length):
    split_message = []
    for i in range(math.ceil(len(string) / 1999)):
        try: # Bad try except code, I dont care.
            split_message.append(string[2000 * i:(2000 * (i + 1)) - 1])
        except:
            pass
    return split_message

# Make sure the bot can read messages and join vc.
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# Create a client and run it using token defined in dotenv.
client = DiscordClient(intents=intents)
client.run(client.token)
