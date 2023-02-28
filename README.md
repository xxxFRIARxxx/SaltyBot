# SaltyBot - A bot for SaltyBet.com.

This bot records its own database, and bets automatically based off of your balance (and whether it's a tournament or not).

Only ever bets max 1/2 your balance in MM. (Rare:  When the best player recorded in DB plays against the worst player recorded in DB)
Bets smaller amounts once balance is over 20k in Tournaments.  (for now)

Steps for use:
-----
Create a file called just ".env".  In this .env file, include your personal strings for the following variables:

email = ""

password = ""

token = ""

user = ""


Where:

EMAIL = Your email to login to SaltyBet.com

PASSWORD = Your password to login to SaltyBet.com

token = Your personal oauth token to login to Twitch (Get one here:  https://twitchapps.com/tmi/)

user = Your username for Twitch
