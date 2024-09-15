# Bob
Bob is a self-hosted, Ollama-powered discord AI bot, with the customizability to make him act how you want in your server.

## Usage
To use Bob, download the dependancies with `pip install -r requirements.txt`. Also make sure [Ollama](https://github.com/ollama/ollama) is installed on the bot's system and is serving (either by running the command `ollama serve` or by setting it as a startup service), and has the llama2-uncensored model installed (which can be done with the command `ollama run llama2-uncensored`). Bob also requires a discord token, which can be created in [Discord's Developer Portal](https://discord.com/developers/applications) and creating a bot (He also requires message content intents from the Bot tab of the developer portal).

For all functionality, Bob requires audio files placed in the src/audio folder, which play when Bob joins vc. These should be kept short, as playing audio is not completely asyncronous and longer files may cause delays in AI generation output.
Bob can also respond to specific message content based on phrases found in other people's messages. Bob does not need to be mentioned for these. Add more entries to the phrases.json file to add more specific responses (one such use case is sending specific gifs when someone sends a message with a certain phrase).

## Dotenv structure
To use Bob, add a .env file with the following:
```
DISCORD_TOKEN=[your-discord-token]
SYSTEM_PROMPT="[The system prompt, which guides you AI in how it should act]"
```
## The System Prompt
The System Prompt should be simple, and should direct the AI as to exactly how it should act. In my experience, Bob may output the entire system prompt, so do not put anything in here you do not want users to see (this may also be a skill issue on my part).
The model is currently hard coded to llama2-uncensored. This can be swapped out for any other model supported by Ollama.

## Hardware
I've tested the bot using a Nvidia GTX 1650 SUPER, which can handle AI generation suitably for requests one at a time (although long requests may have delays of up to 2 minutes on this hardware). The GPU is the biggest bottleneck, as that's what's used by Ollama for AI text generation. More powerful GPUs with more VRAM will handle requests quicker, however if you're using this in a small, private server almost any low or mid end gaming PCs should handle the bot without issues. If you do encounter issues, use a smaller model or try using the model directly within Ollama first to make sure it will generate text appropriately.

## Notes
This code is not particularly neat (I'm probably going to spend a little time fixing it up). This is a weeks worth of work on the bot, and I'm just about done with it, hence why it's becoming public now. Hope anyone who tries it out enjoys it :).
