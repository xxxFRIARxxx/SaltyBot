# SaltyBot - A bot for SaltyBet.com.

Completion Date ETA: 4/1/23

Current state:  Working!

Working on:  Trimming the fat.  Collecting a DB to test out betting patterns and accuracy of win-probability.  ETA = 3/15/23

## What This Bot Does:

* Records its own database  
* Pulls records from the database  
* Assigns its own ratings to players (via Microsoft TrueSkill)  
* Bets automatically (via probability of a win and the amount of salt in your balance)  

# Instructions for use

## Step 0:  Login and Python Prerequisites

**Login Prerequisites**

Create a file called just ".env" in the working-directory of SaltyBot (without quotes).  In this .env file, include your personal strings for the following variables (INCLUDE QUOTES):

email = "your_saltyBet.com_email_here"  
password = "your_saltyBet.com_password_here"  
token = "your_Twitch_oauth_token_here" (Get one here: https://twitchapps.com/tmi/)  
user = "your_Twitch_username_here"

**Python Prerequisites**

DotEnv:  
`pip install python-dotenv`   
Beautiful Soup:  
`pip install beautifulsoup4`   
TrueSkill:  
`pip install TrueSkill`

## Step 1:  GOGOGOGOGOGOGO

Run "SaltyStateMachine.py" to run the program until:
* The heat-death of the universe
* Your power supply/internet connection fails
* The SaltyBet JSON/Twitch servers shut down  
  
  
# Details on betting and rankings

## How are rankings assigned, and how do I get the probability of a winner?

Using the Xbox Live Matchmaking system (MS TrueSkill), ratings are assigned to each new player the database hasn't found.  If they've been found, it uses their latest record/ratings, and "updates" them based off of the result of the current match.

Since TrueSkill uses the Bayesian inference algorithm, I use the cumulative distribution function of this normalized distribution to give me a probability of player 1 winning the current match.

## How does betting work in Matchmaking?

In Matchmaking, if the probability of winning ISN'T 50%, this bot bets an amount based off of the difference in win-probability against 50%.  The amount wagered in this comparison is NEVER LARGER than 1/2 your balance (Even THIS is still very rare:  when the best player ever recorded in DB plays against the worst player ever recorded in DB).  

* Typical wager amounts in this comparison are around 1/300th of your balance during early stages of database building.

Still in Matchmaking, if the probability of winning IS 50% (both new players to the DB, or both with the same rating pulled from the DB), it looks at winstreaks found in the database.  If they've been found, it bets an amount NEVER LARGER than 10% of your balance based off of the difference in winstreaks found in the DB.  (Even THIS is very rare:  when the winstreak difference is 100).  

* Typical wager amounts in this comparison are a little higher than based off of probability, at roughly 1/100th of your balance during ANY portion of building your database.  (Will probably be reworked later) 

## What happens when ratings or winstreaks haven't been found in the DB?

In both Matchmaking and Tournaments, if ratings or winstreaks haven't been found in the database, or are all equal to one another, it wagers $1.

## How does betting work in Tournaments?

In Tournaments, this bot wagers your entire tournament-balance up to $20,000 every round through the same logic that MM does.  Once $20,000 is hit, the betting-system will limit wagers based on rankings or winstreaks like in MM (to ensure keeping of at least roughly $20,000).

## How does betting or match-recording work in Exhibitions?

It doesn't, lol.  Exhibitions are so fucking wacky, that for right now, I'm just ignoring them completely.  No bets, no database recording, no nothing. I have the ability to do this, I just haven't implemented it yet.

## Important note - PATIENCE IS A VIRTUE!

Because of the way this bot assigns ratings and probabilities of winning, ratings gain confidence with time.  You'll find the most success of this bot once your database reaches ~20,000+ entries (roughly 30 days straight of logging).  I know...I know...but k'mon, you're building your own database of ongoing fights!  It'll take a bit!  

Realistically, it'll probably wager $1 on all bets up to ~1000 entries in the DB, then you'll probably come out 50:50 until about ~3000 entries, then it'll only get better from there.
