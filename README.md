# EenTegenHonderd
This Python project allows you to host one against one hundred on a Discord server. Eén tegen 100 (translated as One against one hundred) is a Dutch television game where one candidate needs to eliminate 100 other players (although this implementation allows for any arbitrary number of players). If the candidate doesn't get the question right, a new candidate will be picked from the remaining players, until only one player is left (or zero, in which case the candidate wins).

## Setup
1. Insert your bot's private token (Applications -> Eén tegen 100 -> OAuth2 -> Client Secret -> Copy);
2. Insert the ids of the channel the bot monitors. The bot can use one to two channels, one known as the _cmd_channel_, where you can send your commands and receive error messages (this channel may be hidden from the players) and the _com_channel_, where the bot sends messages to all the players; 
3. Finally, you can insert a questions.txt file. Note that I have already supplied one, but you may enter any questions of your own in this file. The bot currently only supports multiple choice questions with four answers, although this could be easily changed to allow for either less or more answers. The proper formatting for the questions.txt file is as follows:

[question + answers]/[correct answer letter]/[correct answer]

For example:

What is the capital city of Hawaii? A: Honolulu B: Lima C: Paramaribo D: Delft/A/Honolulu

Now you are ready to run the program.

## How to use
You can test whether the bot works by sending !bliep. This will also send a message in the _cmd_channel_.

A game is started by sending !start. The bot will prompt the players to join by reacting a thumbs up. Now you can choose a candidate by sending !kies. Now the game is ready to be played, and you can go through all the questions by subsequently typing:
1. !q: this will make the bot send the question;
2. !s: this will make the bot stop accepting any new answers. You can use this to build up the suspense for the answer;
3. !a: this will make the bot share the answer and share who got the answer wrong and is out of the game.

Finally, you can type !in to see which players are currently still in the game. This command will also list the candidate.

## Contributing
Pull requests are always welcome! For major changes, please open an issue first to discuss what you would like to change.
