# discord-url-bot
A Discord bot written in python to reply to messages containing popular social media URLs with public front ends that allow for Discord embeds.
---

Welcome to Discord URL Bot!

This README assumes that you already know how to use Docker on your server, and that you're using a Linux terminal to set it up. If you're not familiar with Docker, a good place to start is the official [Docker 101 Tutorial.](https://www.docker.com/101-tutorial/)

The first thing you need to do is make a directory for the bot.

```bash
mkdir discord-url-bot
cd discord-url-bot
```

Then, put all the files from the discord-url-bot folder in this repository into that directory.

Now, you'll need to go to the Discord Developer Portal and create your bot, then enable the required "Intents" for this bot to run.
- Visit https://discord.com/developers/applications
- Create your bot, giving it a name and, optionally, an avatar.
- Enable the Message Content Intent:
	   - Go to the "Bot" section
	   - Scroll down to "Privileged Gateway Intents"
	   - Enable "Message Content Intent"
	   - Save changes
 - On the same "Bot" section, scroll up a bit to the button that says "Reset Token" and click it. Save this token, you'll need it.

Next, you'll build and run the container using the docker-compose.yml file:

```bash
# Make sure your .env file has the correct token
echo "DISCORD_BOT_TOKEN=your_actual_bot_token_here" > .env

# Build and run
docker-compose up -d
```

If you want to use different front ends, you would need to update not only the code section under "DOMAIN REPLACEMENTS" but also the RegEx that is listed with "url_pattern" twice and "original_urls" once.
