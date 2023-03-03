# SaltyBot - A bot for SaltyBet.com.

#### Current state - 3/1/23:  Everything works!  :heavy_check_mark:
#### Currently Working On:  
:white_square_button: Trimming the fat of the program (Commented-out code, refactoring, etc.)  ETA = 3/15/23  
:heavy_check_mark: Collecting a DB sizable enough to test out betting patterns and accuracy of win-probability.  ETA = Ongoing, mostly done!  
:x: Bug:  Last match of tournaments doesn't record still  
:x: Bug:  Outliers for matchTime every last-match of a game mode (Tourney or MM)

#### What This Bot Does:

* Records its own database  
* Pulls records from the database  
* Assigns its own ratings to players (via Microsoft TrueSkill)
* Gathers a suggested winner (via probability of a win, difference in skill variance, and winstreaks)
* Bets automatically (via probability of a win, difference in winstreaks, and the amount of salt in your balance)

**Special Thanks:  DukeOfEarl for teaching me everything I know about programming, and some coding help with this program.**

# Instructions for use

## Step 0:  Login and Python Prerequisites

### **Login Prerequisites:**

Create a file called just ".env" in the working-directory of SaltyBot (without quotes).  In this .env file, include your personal strings for the following variables (INCLUDE QUOTES):

email = "your_saltyBet.com_email_here"  
password = "your_saltyBet.com_password_here"  
token = "your_Twitch_oauth_token_here" (Get one here: https://twitchapps.com/tmi/)  
user = "your_Twitch_username_here"


### **Python Prerequisites:**  

To install: `pip install -r requirements.txt`

Alive Progress  
Beautiful Soup  
Dot Env  
TrueSkill  
Requests  
Urllib3

## Step 1:  GOGOGOGOGOGOGO

Run "SaltyStateMachine.py" to run the program until:
* The heat-death of the universe
* Your power supply/internet connection fails
* The SaltyBet JSON/Twitch servers shut down  
  
---

# Details on betting and rankings

## How are rankings assigned, and how do I get the probability of a winner?

Using the Xbox Live Matchmaking system (MS TrueSkill), default ratings are assigned to each new player the database hasn't found.  If they've been found, it uses their latest record/ratings, and "updates" them based off of the result of their upcoming match.

Since TrueSkill uses the Bayesian inference algorithm, I use the cumulative distribution function of this normalized Gaussian distribution to give me a probability of player 1 winning the current match.  

* The suggested winner is the fighter with the higher probability of winning.

* If the probability of winning is 50%, this bot then looks at difference in rating variation.  
The suggested winner is the fighter with the lower rating variation.

* Lastly, if the variations are both the same, this bot looks at the fighters' winstreaks.  
The suggested winner is the fighter with the higher winstreak.

## How does betting work in Matchmaking?  

In MM, if your balance is < 10,000, this bot will wager the entire balance.  It takes money to make money, heh. :slightly_smiling_face:

If your balance is > 10,000 in MM:

### If the probability of winning != 50%:  

This bot bets an amount based off of the difference in win-probability against 50%.  The amount wagered in this comparison is NEVER LARGER than 1/2 your balance.  
(This is very rare:  when the best player ever recorded in DB plays against the worst player ever recorded in DB).  

* Typical wager amounts in this comparison are around 1/300th of your balance during early stages of database building.

### If the probability of winning == 50% (both new players, or both with the same rating pulled from the DB):

This bot then looks at winstreaks found in the database.  If they've been found, it bets an amount ALMOST NEVER LARGER than 10% of your balance based off of the difference in winstreaks found in the DB.  
(This is still very rare:  when the winstreak difference is 100 (insanity).  If we see a winstreak difference > 100 we'll see wagers > 10% of your balance).  

* Typical wager amounts in this comparison are a little higher than based off of probability, at roughly 1/100th of your balance during ANY time this condition hits.  (Will probably be reworked later) 

## What happens when ratings or winstreaks haven't been found in the DB?

In both Matchmaking and Tournaments, if ratings or winstreaks haven't been found in the database, or are all equal to one another, it wagers $1 on a randomly-selected fighter.

## How does betting work in Tournaments?

In Tournaments, this bot wagers your entire tournament-balance up to $20,000 every round through the same probability logic that MM does.  Once $20,000 is hit, the betting-system will limit wagers based on rankings or winstreaks (instead of entire balance) like in MM (to ensure keeping of at least roughly $20,000).

## How does betting or match-recording work in Exhibitions?

It doesn't, lol.

Exhibitions are so fucking wacky, that for right now, I'm just ignoring them completely.  
No bets, no database recording, no nothing. I have the ability to do this, I just haven't implemented it, and don't know if I will.

## Important note - PATIENCE IS A VIRTUE!

Because of the way this bot assigns ratings and probabilities of winning, ratings gain confidence with time.  You'll find the most success of this bot once your database reaches ~20,000+ entries (roughly 30 days straight of logging).  I know...I know...but k'mon, you're building your own database of ongoing fights!  It'll take a bit!  

Realistically, it'll probably wager $1 on all bets up to ~1000 entries in the DB, you'll probably come out a little <50% on bets from about 1000-3000 entries (due to it betting on a ranked fighter when it finds them, against a new fighter with an assigned default ranking), then it'll only get better from there.

Significant confidence ratings start appearing after roughly 12-15 matches recorded per-figher.  Patience!
