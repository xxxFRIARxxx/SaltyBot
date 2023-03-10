# SaltyBot - A bot for SaltyBet.com

#### Current state - 3/6/23:  Everything works!  :heavy_check_mark:  

:heavy_check_mark: **NEW! 3/9/23  This bot bets an amount based off of the Kelly Criterion.**:heavy_check_mark: 

#### Currently Working On:  
* Trimming the fat of the program (Commented-out code, refactoring, last bugs, etc.)  ETA: 3/15/23  

:x: Bug:  Last match of tournaments doesn't record still  
:x: Bug:  Outliers for matchTime every last-match of a game mode (Tourney or MM)  
:x: Bug:  Exhib or Tourney parsing error still occurs.  Fix sometime this week?  3/6/23

#### What This Bot Does:

* Records its own database  
* Pulls records from the database  
* Assigns its own ratings to players (via [Microsoft TrueSkill](https://www.microsoft.com/en-us/research/project/trueskill-ranking-system/))
* Gathers a suggested winner (via probability of a win, difference in skill variance, and streaks)
* Bets automatically (via the [Kelly Criterion](https://en.wikipedia.org/wiki/Kelly_criterion))

**Special Thanks:  
DukeOfEarl for teaching me everything I know about programming, and some coding help with this program.**

# Instructions for use

## Step 0:  Login and Python Prerequisites

### **Login Prerequisites:**

This program requires a Twitch account to pull certain data from current matches.  
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
Tabulate  
Pandas

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

* The predicted winner is the fighter with the higher probability of winning.

* If the probability of winning is 50%, this bot then looks at difference in rating variation.  
The predicted winner is the fighter with the lower rating variation.

* Lastly, if the variations are both the same, this bot looks at the fighters' streaks.  
The predicted winner is the fighter with the higher streak.

* If the probabilities are the same, or their variances are the same, or their streaks are the same or are None:  
The predicted winner is None.

## How does betting work in Matchmaking?  

In MM, if your balance is < 10,000, this bot will wager the entire balance.  It takes money to make money, heh. :slightly_smiling_face:

If your balance is > 10,000 in MM:

### If there is a Predicted Winner:

This bot bets an amount based off of the [Kelly Criterion](https://en.wikipedia.org/wiki/Kelly_criterion)
* Typical wager amounts average 2.5% of your balance.  In this comparison, bets are NEVER LARGER than 5% of your entire balance.  

### If there isn't a Predicted Winner:

* This bot wagers $1 on a randomly selected fighter.

## How does betting work in Tournaments?

In Tournaments, this bot wagers your entire tournament-balance up to $20,000 every round.  Once $20,000 is hit, the betting-system will limit wagers based on the Kelly Criterion like in MM (instead of entire balance, to ensure keeping of at least roughly $20,000).

## How does betting or match-recording work in Exhibitions?

It doesn't, lol.

Exhibitions are so fucking wacky, that for right now, I'm just ignoring them completely.  
No bets, no database recording, no nothing. I haven't implemented it, and don't know if I will.

## What happens when Tier or True Streaks don't come back from Twitch?

If Tier or True Streaks aren't pulled from Twitch, it will not record that match.

## Important note - PATIENCE IS A VIRTUE!

Because of the way this bot assigns ratings and probabilities of winning, ratings gain confidence with time.  You'll start finding success better than 50% starting ~4000 entries, and you'll find the most success of this bot once your database reaches ~30,000+ entries (roughly 75 days of logging).  
I know...I know...but k'mon, you're building your own database of ongoing fights!  It'll take a bit!  

If you have over $10k, realistically, it'll probably wager $1 on most bets up to ~1500 entries in the DB, you'll probably come out a little <50% on bets from about 1500-3000 entries (due to it betting on a ranked fighter when it finds them, against a "new" fighter with an assigned default ranking, losing the bet), then it'll only get better from there.

I believe 95% confidence ratings start appearing after roughly 10-12 matches recorded per-figher.  
(~30,000 total matches.  Roughly 2 months of recording matches.)  
This bot will do much better than a random choice up until then, but that's when it should almost never bet incorrectly.  
Patience!
