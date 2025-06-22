import discord
from discord.ext import commands
import re
import os
from urllib.parse import urlparse, parse_qs, urlunparse

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Domain mappings
DOMAIN_REPLACEMENTS = {
    # Twitter/X
    'twitter.com': 'fxtwitter.com',
    'www.twitter.com': 'fxtwitter.com',
    'x.com': 'fixupx.com',
    'www.x.com': 'fixupx.com',
    
    # Instagram  
    'instagram.com': 'instagramez.com',
    'www.instagram.com': 'instagramez.com',
    
    # TikTok
    'tiktok.com': 'vxtiktok.com',
    'www.tiktok.com': 'vxtiktok.com',
    
    # Reddit
    'reddit.com': 'rxddit.com',
    'www.reddit.com': 'rxddit.com',
    'old.reddit.com': 'rxddit.com',
    'new.reddit.com': 'rxddit.com',
    'm.reddit.com': 'rxddit.com',
    
    # Pinterest (commonly shared, terrible embeds)
    'pinterest.com': 'pinimg.com',
    'www.pinterest.com': 'pinimg.com',
    'pin.it': 'pinimg.com',  # Pinterest short links
    
    # Bluesky
    'bsky.app': 'cbsky.app',
    
    # Twitch (clips don't embed well)
    'twitch.tv': 'twitchtracker.com',
    'www.twitch.tv': 'twitchtracker.com',
    'clips.twitch.tv': 'twitchtracker.com',
}

# Common tracking parameters to remove
TRACKING_PARAMS = {
    'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
    'fbclid', 'gclid', 'dclid', 'mc_cid', 'mc_eid', '_ga', 'ref_src', 'ref_url',
    'igshid', 'igsh', 's', 't', 'si', 'feature', 'ref', 'source'
}

def clean_url(url):
    """Remove tracking parameters and clean up the URL"""
    try:
        parsed = urlparse(url)
        
        # Parse query parameters
        query_params = parse_qs(parsed.query)
        
        # Remove tracking parameters
        cleaned_params = {k: v for k, v in query_params.items() 
                         if k.lower() not in TRACKING_PARAMS}
        
        # Reconstruct query string
        if cleaned_params:
            # Flatten the parameter values (parse_qs returns lists)
            flat_params = []
            for k, v_list in cleaned_params.items():
                for v in v_list:
                    flat_params.append(f"{k}={v}")
            new_query = "&".join(flat_params)
        else:
            new_query = ""
        
        # Reconstruct URL
        cleaned_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            ""  # Remove fragment
        ))
        
        return cleaned_url
    except Exception:
        return url

def replace_social_urls(text):
    """Find and replace social media URLs in text"""
    # Regex pattern to match URLs
    url_pattern = r'https?://(?:(?:www\.|old\.|new\.|m\.|clips\.)?(?:reddit\.com|twitch\.tv)|(?:www\.)?(?:twitter\.com|x\.com|instagram\.com|tiktok\.com|pinterest\.com|bsky\.app)|pin\.it)[^\s]*'


    
    def replace_url(match):
        original_url = match.group(0)
        
        try:
            parsed = urlparse(original_url)
            domain = parsed.netloc.lower()
            
            # Remove www. for comparison
            if domain.startswith('www.'):
                domain_key = domain
            else:
                domain_key = domain
            
            # Check if we should replace this domain
            if domain_key in DOMAIN_REPLACEMENTS:
                new_domain = DOMAIN_REPLACEMENTS[domain_key]
                
                # Replace the domain
                new_url = original_url.replace(parsed.netloc, new_domain, 1)
                
                # Clean tracking parameters
                cleaned_url = clean_url(new_url)
                
                return cleaned_url
            
        except Exception as e:
            print(f"Error processing URL {original_url}: {e}")
        
        return original_url
    
    # Find and replace all matching URLs
    replaced_text = re.sub(url_pattern, replace_url, text, flags=re.IGNORECASE)
    
    return replaced_text

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    # Don't respond to bot messages
    if message.author.bot:
        return
    
    # Check if message contains URLs from target domains
    url_pattern = r'https?://(?:(?:www\.|old\.|new\.|m\.|clips\.)?(?:reddit\.com|twitch\.tv)|(?:www\.)?(?:twitter\.com|x\.com|instagram\.com|tiktok\.com|pinterest\.com|bsky\.app)|pin\.it)[^\s]*'

    
    if re.search(url_pattern, message.content, re.IGNORECASE):
        # Replace URLs
        new_content = replace_social_urls(message.content)
        
        # Only reply if URLs were actually changed
        if new_content != message.content:
            # Extract just the URLs for a cleaner response
            original_urls = re.findall(r'https?://(?:(?:www\.|old\.|new\.|m\.|clips\.)?(?:reddit\.com|twitch\.tv)|(?:www\.)?(?:twitter\.com|x\.com|instagram\.com|tiktok\.com|pinterest\.com|bsky\.app)|pin\.it)[^\s]*', 
                                     message.content, re.IGNORECASE)
            new_urls = re.findall(r'https?://(?:fxtwitter\.com|fixupx\.com|instagramez\.com|vxtiktok\.com|rxddit\.com|pinimg\.com|twitchtracker\.com|cbsky\.app)[^\s]*'
, 
                                new_content, re.IGNORECASE)
            
            if new_urls:
                # Create response with just the fixed URLs
                response = "It looks like you've posted a social media link that doesn't play nicely with discord. Here is a link with a working embed:\n" + "\n".join(new_urls)
                
                # Reply to the original message
                await message.reply(response, mention_author=False)
    
    # Process commands
    await bot.process_commands(message)

@bot.command(name='fix')
async def fix_urls(ctx, *, text):
    """Manually convert social media URLs"""
    fixed_text = replace_social_urls(text)
    
    if fixed_text != text:
        await ctx.send(f"Fixed URLs:\n{fixed_text}")
    else:
        await ctx.send("No social media URLs found to fix.")

# Run the bot
if __name__ == "__main__":
    # Get token from environment variable
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("Error: DISCORD_BOT_TOKEN environment variable not set!")
        exit(1)
    
    bot.run(token)
