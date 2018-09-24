
# Alright everyone, I know what its like to have your family living away long distance. In an effort to help families stay connected, I will be sending a gentle reminder to people that aren't following family members on twitter.

#---------------------------------------------------------#
# Imports
#-------------------------------------
#--------------------#
import tweepy
import time
import sys
import requests
import os
import datetime
import random
from random import randint

from secrets import *

#---------------------------------------------------------#
# Define Functions
#---------------------------------------------------------#

def tweet_image(url, message, replyto):
    filename = 'temp.jpg'
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        with open(filename, 'wb') as image:
            for chunk in request:
                image.write(chunk)

        api.update_with_media(filename, status=message, in_reply_to_status_id=replyto)
        os.remove(filename)
    else:
        print("Unable to download image")

def tweet_message(message, replyto):
    api.update_status(status=message, in_reply_to_status_id=replyto)

def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.datetime.fromtimestamp(now_timestamp) - datetime.datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset	

def to_alternating_case(string):
	temp = ""
	i=0
	for character in string:
		if i==1:
			temp += character.upper()
			i = 0
		else:
			temp += character.lower()
			i += 1

	return temp

#---------------------------------------------------------#
# Begin Script
#---------------------------------------------------------#

print("-------------------------------------------------------------------------------------")

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

CurrentDateTime = datetime.datetime.now()
ClientList = []
RelativeList = []
RelativesComplete = []
#RelationTypeList = []

FollowedFamilyMember = []

RequestReponseAcknowledge = ['Sure thing', 'Will do', 'Okay', 'Alright', 'Can do', 'Challenge accepted', 'No worries', 'No problem']
RequestResponseReference = ['buddy', 'mate', 'champ', 'legend', 'chief', 'boss']

#--------------------------------------------------------------------------------
# Find Requests for Family Connections.
#--------------------------------------------------------------------------------	

for Tweet in tweepy.Cursor(api.search, q='@LeafyGreeans Connect', lang='en').items():
	#print('-------------Tweet--------------------')
	print('Tweeted By: ' + Tweet.author.screen_name)
	#print(Tweet.id)
	print(Tweet.text)

	TweetActioned = False

	# Switch to lower to stop differences in capitalisations causing duplicate tweets to Relatives.
	TweetText = Tweet.text.lower()

	#Remove Reference to bot before processing.
	TweetText=TweetText.split("@leafygreeans", 1)[1]

	# Identify Relatives in Tweet Text and append to list.
	while '@' in TweetText:
	
		# Collect Target Username.
		Relative = TweetText.split("@", 1)[1]
	
		# Remove any extra text after the relatives username.
		Relative = Relative.split(" ", 1)[0]

		ClientList.append(Tweet.author.screen_name)
		RelativeList.append(Relative)

		# Remove processed Relative from text.
		TweetText = TweetText.split("@", 1)[1]

	
	# Check for previous acknowledgement
	for Reply in tweepy.Cursor(api.search,q='#FamilyConnections',result_type='recent',since_id=Tweet.id).items(1000):
						if hasattr(Reply, 'in_reply_to_status_id_str'):
							if (Reply.in_reply_to_status_id==Tweet.id
							and Reply.author.screen_name=='LeafyGreeans'):
								TweetActioned = True

	# Reply with acknowledgement
	if TweetActioned == False:

		ReplyText = '@' + Tweet.user.screen_name + ' ' + random.choice(RequestReponseAcknowledge) + ' ' + random.choice(RequestResponseReference) + '. \n\n#FamilyConnections'
		
		print('Reply with: ' + ReplyText)
		print('Reply_to: ')
		print(Tweet.id)

		tweet_message(ReplyText, Tweet.id)

		#print('-------------End of Tweet--------------------')
	else:
		print('Tweet already acknowledged.')

#--------------------------------------------------------------------------------
# Loop through relatives being targeted.
#--------------------------------------------------------------------------------
RelativeIndex = 0
for Relative in RelativeList:

	ActionTarget = False

	Client = ClientList[RelativeIndex]
	FamilyList = []

	# Add Relative/Client to list to mark combination as actioned.
	if(Client + "/" + Relative not in RelativesComplete):
		
		ActionTarget = True
		
		# Add Client to list of family members.
		FamilyList=[Client]
		RelativesComplete.append(Client + "/" + Relative)

	
	# Check for other instances of the same relative being flagged by other clients.
	ClientIndex = 0 
	for Client in ClientList:

		# Collect other instances of the same relative being flagged by Clients.
		if (ClientIndex > RelativeIndex
			and RelativeList[ClientIndex] == Relative
			and ClientList[ClientIndex] not in FamilyList
			):
			
			# Add additional Relative to the list of concerned family members.
			FamilyList.append(Client)

			# Add Relative/Client combination to list.
			RelativesComplete.append(Client + "/" + RelativeList[ClientIndex])
		
		ClientIndex += 1
	
	RelativeIndex += 1

	if ActionTarget == True:

		print('Actioning: ' + Relative + ' + ')
		print(FamilyList)


		#-----------------------------------------#
		# Check the friend list of each relative
		#-----------------------------------------#
		
		print("Collecting Friends...")

		friends = tweepy.Cursor(api.friends, screen_name=Relative, count=100).items()

		Friend_Handles=[]

		i=0
		while True:
			try:
				friend = next(friends)
			except tweepy.TweepError:
				print("tweepy error, sleeping for 15min.")
				time.sleep(60*15)
				friend = next(friends)
			except StopIteration:
				break
				
			#print("@" + friend.screen_name)
			
			# Add friend to array for comparison later.
			Friend_Handles.append(friend.screen_name)
			
			#increment
			i += 1
		
		#print("Friends Collected.")

		#print("Checking friends for family member")

		for username in FamilyList:
			if username in Friend_Handles:
				print("Following " + username)
				FollowedFamilyMember.append(True)
			else:
				print("Not Following " + username)
				FollowedFamilyMember.append(False)


		#print("Finished Checking for Family Members.")

		if False in FollowedFamilyMember:

			#---------------------------------------------------------#
			# Check for new Tweets
			#---------------------------------------------------------#

			#print("check latest Tweets")

			Tweets = api.user_timeline(Relative)

			for Tweet in Tweets:

				TweetActioned=False

				#print(Tweet.text)
				# If Tweet was within the last hour.
				if datetime_from_utc_to_local(Tweet.created_at) >= CurrentDateTime - datetime.timedelta(hours=24):

					if Tweet.text[:2]=="RT":
						#print("Message is a Retweet.")
						TweetIsRetweet = True
					else:
						TweetIsRetweet = False


					if Tweet.in_reply_to_screen_name != None:
						#print("Message Is Reply.")
						TweetIsReply = True
					else:
						TweetIsReply = False


					if TweetIsRetweet == False and TweetIsReply == False:

						TweetActioned = False

						for Reply in tweepy.Cursor(api.search,q='#FamilyConnections',result_type='recent',since_id=Tweet.id).items(1000):
							if hasattr(Reply, 'in_reply_to_status_id_str'):
								if (Reply.in_reply_to_status_id==Tweet.id
								and Reply.author.screen_name=='LeafyGreeans'):
									TweetActioned = True

						if(TweetActioned==False):		

							#---------------------------------------------------------#
							# Build Comment
							#---------------------------------------------------------#	
							ReplyText = ''
							ImagePath = ''

							# Remove any link referenced by the original tweet.
							sep = 'http://'
							TweetText = Tweet.text.split(sep, 1)[0]
							sep = 'https://'
							TweetText = TweetText.split(sep, 1)[0]

							# Build list of unfollowed family members.
							FamilyIndex=0
							FamilyText=''
							for FamilyMember in FamilyList:
								if FollowedFamilyMember[FamilyIndex]==False:
									FamilyText = FamilyText + '@'+ FamilyList[FamilyIndex] + ' '
							
							FamilyText = "You should start following " + FamilyText + "#FamilyConnections"

							ReplyNumber = randint(1,4)

							if ReplyNumber==1:
								ImagePath = "https://i.imgur.com/khRpdb2.jpg"
								ReplyText = to_alternating_case(TweetText[:200]) + '-\n\nYour family misses you.'
							elif ReplyNumber==2:
								ReplyText = "What, do you think you're too cool for your family or something???"
							elif ReplyNumber==3:
								ReplyText = "Are you missing something in your life? Feling empty inside?"
							elif ReplyNumber==4:
								ReplyText = "Hah, Good one! I bet your family has some pretty good content aswell. Why not follow them to find out?"

							ReplyText = "@" + Tweet.user.screen_name + " " + ReplyText + " " + FamilyText


							#---------------------------------------------------------#
							# Tweet Image
							#---------------------------------------------------------#

							if ImagePath=='':
								print('tweet text')
								print(ReplyText)
								tweet_message(ReplyText, Tweet.id)
							else:
								print('tweet Image')
								print(ReplyText)
								tweet_image(ImagePath, ReplyText, Tweet.id)
						else:
							print("Tweet already actioned.")		

print("End.")