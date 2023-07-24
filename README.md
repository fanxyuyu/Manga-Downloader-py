## About

This is just a simple program made entirely in python that allows the download of manga chapters from [mangakakalot](https://ww5.mangakakalot.tv/). Everything was made with the intention of learning more about python in a fun and interactive way!

**Disclaimer**


## How to start

To get the bot to work you should download the source code and follow the next steps:
  1. Create a Heroku account and create a new project
  2. Create a git repository with the same files (you'll just need to add the Procfile and requirements files besides the base code)
  3. Deploy directly from the repository link on the heroku project page and be happy :)


## List of Commands

**bot prefix: !** - every command should be like !command

**Admin** (limited by role or id)
  - clear *<quantity>*: deletes an specific amount of messages
  - close: forces the bot to close
 
**Text**
  - say: the bot sends the message for you
  - embed: same as above but with embed format
 
**Basic:**
  - help: shows a list with all the commands
  - ping: shows bot ping
  - italy: shows current time in Italy
  - avatar *<user>*: shows user avatar - *leave user empty to see your own*
  
**Fun:**
  - 8ball *<question>*: answer your question with a phrase from a random set
  - names: shows a text with all names commands avaliable
  - reverse: reverse a text
  - fact: shows a random fact *fun api that's constantly updating*
 
**Anime:**
- anime: shows a list with all anime commands
  
  interaction:
  - senpai: makes a user notice you
  - hug: hugs another user
  - kiss: kisses another user
  - slap: slaps another user
  - pat: pats another user
  - kill: kills another user
  - lick: licks another user
  - cuddle: cuddles with another user
  - insult: insult another user
  
  Reaction
  - blush
  - cry
  - dance
  - pout
  - smug
  
*all the interaction have different results deppeding on the user being targeted, give it a try it's fun :)*
  
**Others:**
- 24 hour loop: a reminder message that shows every day at the same time

## TODO
- [x] Anime interactions
- [x] Djando database interaction *(currently learning by doing on another project [here](https://github.com/fanxyuyu/DiscordQuizWithDjango))*
- [ ] Web Scraping
