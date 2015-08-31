#!/usr/bin/ python3
#
######### Script Header #########
#  
#::Script Name::
#  TAL_EpiDownload.py
#  
#  
#::About Author::
#  Miles Nielsen
#  MilesNielsen.net
#  Miles.Nielsen@swe.org
#  
#  
#::Legal::
#  This script is Copyright 2014 Miles Nielsen.
#  
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  See <http://www.gnu.org/licenses/> for a copy of the GNU General Public License.
#  
#  
#::Script Purpose::
#  To download one [1] or more episodes of the radio show 'This American Life' from their website.
#  
#  
#::Philosophy of the Script::
#  It is assumed that TAL episodes are and shall remain numerically sequential.
#  It is the responsibility of the User to know which episode(s) s/he wants to download, by episode number.
#  
#  
#::Restrictions::
#  The webmaster(s) behind 'This American Life' sometimes alter the download URL.
#  The URL below is the most current correct URL format, dated Fri 13Mar2015.
## http://audio.thisamericanlife.org/EPISODENUMBER/EPISODENUMBER.mp3
## ("http://audio.thisamericanlife.org/" + str(EpisodeNumber) + "/" + str(EpisodeNumber) + ".mp3")
# 
## Olde Download URL
## http://audio.thisamericanlife.org/jomamashouse/ismymamashouse/EPISODENUMBER.mp3
#  
#  The URL for T.A.L. radio archives is:
## http://www.thisamericanlife.org/radio-archives
#  
#  
#::Notes::
#  None.
#  
#  
#::Sample Usage::
#  1) Open Terminal
#  2) Execute "python3 '/location/of/the/script/TAL_Epi_Download.py'"
#  3) Follow instructions within the script
#
#  
#::Back to the Future::
#  *Find out when today's episode is available for download... today, or tomorrow
#  |--> once found out, add in appropriate action at keyword-location GetTheTodayActionStarted
#  |--> current today-action is to assume "wait until tomorrow" and provide the previous episode for download
#  
#  
#::Revision History::
#  v1.0 - Initial release;
#              Miles Nielsen [.net]. 2015.08.31
#  
#  
#  
#  
#  
#  
#  
#  
######### End Script Header #########

#Thy Pound-Includes
import getpass
import datetime
import urllib, urllib.request
import os, sys
from random import randint
from shutil import copyfileobj
from html.parser import HTMLParser

#Time, Right Now.
now = datetime.datetime.now()

#Get local username
UserName = getpass.getuser()

#Define End-Of-Script Quit-Action
def quitting_time():
     print()
     print()
     print("Your Precious Cargo Is On Your Desktop, Inside The Folder 'ThisAmericanLife'.")
     print("I Now Retire To My Humble Abode.")
     print("Thank You, User, For This Opportunity.")
     input("Press ENTER To End Program.")
     sys.exit(0)


#Change download directory to "ThisAmericanLife" on User's Desktop
if not os.access('/home/' + UserName + '/Desktop/ThisAmericanLife/', os.F_OK):
    os.mkdir('/home/' + UserName + '/Desktop/ThisAmericanLife/')

os.chdir('/home/'+ UserName +'/Desktop/ThisAmericanLife/')


#Required for parsing and stripping HTML data
class MLStripper(HTMLParser): #Supports the stripping of tags from "straight html"
     def __init__(self):
          super().__init__()
          self.reset()
          self.fed = []
     def handle_data(self, d):
          self.fed.append(d)
     def get_data(self):
          return ''.join(self.fed)

#This strips html tags from html; input must be "straight html"
def strip_tags(html):
     s = MLStripper()
     s.feed(html)
     return s.get_data()


#Define asking User what s/he wants to do
def what_to_do (retries=4, complaint='Answer With A Number Between 1 and 5, Please'):
     Option_01 = set(['1', '01', 'one'])
     Option_02 = set(['2','02','two'])
     Option_03 = set(['3','03','three'])
     Option_04 = set(['4','04','four'])
     Option_05 = set(['5','05','five'])

     while True:
          we_are_doing = input("Answer With Numbers 1 thru 5 >> ").lower()
          if we_are_doing in Option_01:
               print("We'll now download one episode of your choice.")
               print()
               One_OneEpisode()
          if we_are_doing in Option_02:
               print("We'll now download your choice of a block of episodes.")
               print()
               Two_EpisodeBlock()
          if we_are_doing in Option_03:
               print("We'll now download episodes from your choice to the current episode.")
               print()
               Three_ScatteredEpisodes()
          if we_are_doing in Option_04:
               print("We'll now download a smattering of episodes of your choice.")
               print()
               Four_EpiChoiceToCurrent()
          if we_are_doing in Option_05:
               print("We'll now download five random episodes for you.")
               print()
               Five_5RandomEpis()
          retries = retries - 1
          if retries < 0:
               print("You Are Incapable Of Following Instructions.")
               print("I'm Done Trying To Help You.")
               input("Press ENTER To Quit, As I Have.")
               sys.exit(0)
          print(complaint)


####### Subroutine: Get Latest Episode Number #######
def get_latest_episode_number():
#Note: this subroutine creates and deletes a temporary txt file, "TAL_Archive_HTML.txt"

     ###Global Variables###
     #this is required because we need to know what the latest episode number is Everywhere
     global LatestEpisodeNumber
     ###Global Variables###


     #Get the HTML source code from T.A.L.'s Archive URL
     website = urllib.request.urlopen("http://www.thisamericanlife.org/radio-archives").read()

     #Save Website to risk_reward.txt [file will be removed when the data is retrieved]
     strip_write = open('/home/' + UserName + '/Desktop/ThisAmericanLife/TAL_Archive_HTML.txt', 'w')
     strip_write.write(strip_tags(website.decode('utf-8')))
     strip_write.close()


     #Search through HTML-stripped source data for the latest episode, keying off the first instance of "Share"
     with open('/home/' + UserName + '/Desktop/ThisAmericanLife/TAL_Archive_HTML.txt', 'r+') as TAL_Archive_HTML:
          for line in TAL_Archive_HTML:
               if "Share" in line:
                    #Assign the latest episode's information [number, title, date] without leading spaces to variable CurrentEpisodeLineInfo
                    CurrentEpisodeLineInfo = TAL_Archive_HTML.__next__().lstrip()

                    #Assign the last 10 characters of space-stripped CurrentEpisodeLineInfo to LatestEpisodeDate [DD.MM.YYYY]
                    LatestEpisodeDate = CurrentEpisodeLineInfo[-11:-1]

                    #Check if the latest queue'd episode is available today, keying off date information
                    if now.strftime("%m.%d.%Y") < LatestEpisodeDate:
                         LatestEpisodeNumber = int(CurrentEpisodeLineInfo[0:3]) - 1
                    elif now.strftime("%m.%d.%Y") == LatestEpisodeDate:
                         #We need to find out when today's episode is released for download... today, or tomorrow.
                         #GetTheTodayActionStarted
                         LatestEpisodeNumber = int(CurrentEpisodeLineInfo[0:3]) - 1
                         pass
                    elif now.strftime("%m.%d.%Y") > LatestEpisodeDate:
                         LatestEpisodeNumber = CurrentEpisodeLineInfo[0:3]
                    else:
                         print()
                         print()
                         print("Call The Doctor.")
                         print("I Now Hide Behind Cpt. Jack Harkness For Safety.")
                         input("Press ENTER To Escape Your Doom.")
                         sys.exit(0)

                    break


     print("The latest episode in the queue is " + CurrentEpisodeLineInfo)
     print()
     print("The latest available episode is Episode #" + str(LatestEpisodeNumber))
     print()


     #Remove the temporary txt file TAL_Archive_HTML.txt
     os.remove("/home/" + UserName + "/Desktop/ThisAmericanLife/TAL_Archive_HTML.txt")


####### Subroutine: Get Episode Number From User #######
def get_episode_number_from_user():

     ###Global Variables###
     #This is required because we need to know the episode number Everywhere
     global EpisodeNumber
     #This is required in case User enters "0" for the episode number
     global nakednumber
     ###Global Variables###

     number = input("Give Me An Episode Number >> ")
     print()

     nakednumber = number.lstrip("0")

     if nakednumber == "":
	      print("You told me to download 'Episode 0', which does not exist.")
	      get_episode_number_from_user()
     else:
          pass

     EpisodeNumber = int(nakednumber)

     if(EpisodeNumber >= 1):
          pass
     else:
	      print("You didn't give me a positive whole number.")
	      get_episode_number_from_user()


####### Subroutine: Generate Random Episode Number #######
def generate_random_episode_number():

     ###Global Variables###
     #This is required because we need to know the episode number Everywhere
     global EpisodeNumber
     ###Global Variables###

     RandomEpisodeNumber = randint(0,int(LatestEpisodeNumber))

     EpisodeNumber = RandomEpisodeNumber


####### Subroutine: Check Number Is Valid #######
def check_epi_number_validity():

     if EpisodeNumber >= int(LatestEpisodeNumber):
          while (EpisodeNumber >= int(LatestEpisodeNumber)):
               print("The episode number you have chosen is in the Future.")
               print()
               get_episode_number_from_user()
     else:
          pass


####### Subroutine: Download The Episode #######
def download_the_episode():
     ###Global Variables###
     #this is required because we need to know the episode number Everywhere
     global EpisodeNumber
     ###Global Variables###

     mp3 = str(EpisodeNumber) + ".mp3"


     with urllib.request.urlopen(("http://audio.thisamericanlife.org/" + str(EpisodeNumber) + "/" + str(EpisodeNumber) + ".mp3")) as in_stream, open(mp3, 'wb') as out_file:
         copyfileobj(in_stream, out_file)

     print()
     print("I have finished downloading episode #" + str(EpisodeNumber) + " of This American Life.")
     print()


##################################################
##########Executing The User's Options############
##################################################


####### Download One Episode #######
def One_OneEpisode():
     get_latest_episode_number()

     get_episode_number_from_user()

     check_epi_number_validity()

     download_the_episode()

     quitting_time()


####### Download A Choice Block Of Episodes #######
def Two_EpisodeBlock():
     #This is required because we need to know the episode number Everywhere
     global EpisodeNumber
     ###Global Variables###

     get_latest_episode_number()


     #Get the first boarder episode number from User
     print("What episode number is at the beginning of this block of episodes?")
     get_episode_number_from_user()

     check_epi_number_validity()

     FirstNumber = EpisodeNumber


     #Get the second boarder episode number from User
     print("What episode number is at the end of this block of episodes?")
     get_episode_number_from_user()

     check_epi_number_validity()

     SecondNumber = EpisodeNumber


     #A list of the boarder episode numbers
     boarder_episodes = [FirstNumber,SecondNumber]

     #Find and establish which episode number inputted has the larger value
     HigherEpisodeNumber = max(boarder_episodes)

     #Find and establish which episode number inputted has the smaller value
     LowerEpisodeNumber = min(boarder_episodes)


     #Asshole Condition [block of 1 episode]
     #We are going to use EpisodeNumber to download, and admonish the User
     if FirstNumber == SecondNumber:
          print()
          print("You should have chosen Option #1: 'Download One Episode of your choice'.")
          print("I don't want to out of principle, but to be nice I shall help you anyway.")
          print()

          download_the_episode()

          quitting_time()
     else:
          pass


     #Calculate how many episodes to download
     DownloadCycles = int(HigherEpisodeNumber) - int(LowerEpisodeNumber) + 1

     #Prime the EpisodeNumber variable for looping
     EpisodeNumber = int(LowerEpisodeNumber)

     #Download those episodes!
     for n in range(0,DownloadCycles):
          download_the_episode()

          EpisodeNumber = EpisodeNumber + 1


     quitting_time()


####### Download Scattered Episodes #######
def Three_ScatteredEpisodes():
     get_latest_episode_number()

     HowManyEpisodes = input("How Many Episodes Would You Like To Download? >> ")

     if(int(HowManyEpisodes) >= 1):
         pass
     else:
          while (int(HowManyEpisodes) < 1):
               print()
               print("You didn't give me a counting number.")
               HowManyEpisodes = input("How Many Episodes Would You Like To Download? >> ")
               print()

     if int(HowManyEpisodes) > (int(LatestEpisodeNumber) + 1):
          while (int(HowManyEpisodes) > (int(LatestEpisodeNumber) + 1)):
               print()
               print("There are not that many episodes to download at this time.")
               print()
               print("There are " + str(LatestEpisodeNumber) + " available to download at this time.")
               print()
               HowManyEpisodes = input("How Many Episodes Would You Like To Download? >> ")
               print()

     for n in range(0,int(HowManyEpisodes)):
          get_episode_number_from_user()

          check_epi_number_validity()

          download_the_episode()

     quitting_time()


####### Download Choice To Latest Available #######
def Four_EpiChoiceToCurrent():
     ###Global Variables###
     #This is required because we need to know the episode number Everywhere
     global EpisodeNumber
     ###Global Variables###

     get_latest_episode_number()

     print("I need to know what episode you want to start with.")

     get_episode_number_from_user()

     check_epi_number_validity()

     #Calculate how many episodes to download
     DownloadCycles = int(LatestEpisodeNumber) - EpisodeNumber + 1

     #Download those episodes!
     for n in range(0,DownloadCycles):
          download_the_episode()
          EpisodeNumber = EpisodeNumber +1

     quitting_time()


####### Download Five Random Episodes #######
def Five_5RandomEpis():
     ###Global Variables###
     #This is required because we need to know the episode number Everywhere
     global EpisodeNumber
     ###Global Variables###

     get_latest_episode_number()

     for n in range(0,5):
          EpisodeNumber = randint(1,int(LatestEpisodeNumber))

          download_the_episode()

     quitting_time()


##################################################
############### Kick Off The Script ##############
##################################################


#Print-to-Screen Introduction
print('========== =========== ==========')
print("Hello " + UserName + "!")
print("The time is", now.strftime("%Y-%m-%d %H:%M")) #Print to Terminal time, time right now;
print("Let's Download Some Episodes of 'This American Life'.")
print('========== =========== ==========')


#Prompt User On What To Do
print("What Type Of Downloading Would We Like To Do? ")

print()

print("Option 1: One [1] episode of your choice.")
print("Option 2: A continuous block of episodes, your choice.")
print("Option 3: A discontinuous block of episodes, your choice.")
print("Option 4: All episodes between your choice and the current episode [inclusive].")
print("Option 5: Five [5] random episodes.")

print()

what_to_do()

#EndFile.
