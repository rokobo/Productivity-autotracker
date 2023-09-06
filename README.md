# **Productivity autotracker**

This project began with a desire to have a time tracking software with the automatic nature of Rescuetime, the flexibility of Toggl and a custom-made data analysis.

+ [How it works](#how-it-works)
  + [Configuration files](#configuration-files)
  + [Idle detection](#idle-detection)
+ [Crowns and study advisor](#crowns-and-study-advisor)
+ [Backup system](#backup-system)
+ [Pages](#pages)
+ [Browser URL problem](#browser-url-problem)

## **How it works**

This program works by having it constantly running (I always have a terminal running a couple programs). It is periodically getting your active window and other pieces of information to determine what you are doing and if you are idle.

Having the window information, the program will try to classify it using the rules defined in the `config/categories.yml` and `config/config.yml`.

### **Configuration files**

1. `config/categories.yml`:
    + This file has regex patterns used to match your current activity to either the personal or work category.
    + Any activity that does not match is considered neutral.

2. `config/config.yml`:
    + This file has some values that can be personalized, including color, intervals, spacings and others.
    + The `URLS_PATH` variable is your standard download location, which is where the custom  browser extension will save the URLs file.
    + The `HIDDEN_APPS` list is used to define processes that should have their title information hidden (E.g. `explorer.exe` shows which folder you are currently on, this may be undesirable).
    + The `FULLSCREEN_APPS` list is used to detect non-idle activity when the process is in fullscreen (if a process that is not on this list is fullscreen and the program has not detected activity for some time, it will consider the state as idle).

### **Idle detection**

If the program detects you are idle, it will display a warning modal like this:

<p align="center">
  <img src="https://github.com/rokobo/Productivity-autotracker/blob/main/images/idle_warning.png?raw=true" width="200"/>
</p>

You also have the option to set your status as idle with the top-right button of the main page. Do note that the idle detection uses multiple sources of activity detection, specifically: audio, keyboard, mouse and specific fullscreen apps. If you press the button and move your mouse or forget to pause music, the idle status will be reverted.

## **Pages**

Pages are divided into three categories: Productivity, Analytics and Troubleshooting.

+ **Productivity pages**:
  + `Dashboard page` - Contains the categoried and aggregated events, along with a graph with the total daily time of each category.

+ **Analytics pages**:
  + `Goals page` - Contains heatmaps that track progress on a number of goals defined by the user.
  + `Trends page` - Contains bar graphs for work and personal activity in three different time ranges.
  + `All events page` - Contains all recorded events separated into categories and sorted by time. Can help see what you spend most time on and serves to see if there are any neutral events that should be categorized.

+ **Customization pages**:
  + `Configuration page` - Offers ways to modify the contents of `config.yaml`.
  + `Categories page` - Offers ways to modify the contents of `categories.yaml`.
  + `Breaks page` - Offers ways to add break days without damaging streaks or achievements.

+ **Troubleshooting pages**:
  + `Activity table` - Contains a scrollable version of the `activity.db` file.
  + `Categories table` - Contains a scrollable version of the `categories.db` file.
  + `URLs table` - Contains a scrollable version of the `urls.db` file.
  + `Input tables` - Contains a scrollable version of the `audio.db`, `backend.db`, `frontend.db`, `mouse.db`, `keyboard.db`, `fullscreen.db` and `date.db` files.
  + `Milestones table` - Contains a scrollable version of the `milestones.db` file.

+ **Credits**:
  + `Attributions page` - Contains image attributions for assets used in this project.

## **Crowns and study advisor**

On the background, the study advisor routine is running. It sends desktop notifications when you reach certain goals or pass the daily personal activity limit.

Additionally, the main dashboard pages has three crowns that represent a streak of achievements. The three crowns are: Personal activity under limit, small daily work goal and full work goal. Depending on how many days in a row you have done, a different crown will appear. Settings changes how long each interval should be.

## **Backup system**

To prevent possible data deletion, the `activity.db` file is periodically backed up in the `backup` folder. Interval between backups and number of stored backups can be changed in settings.

This program was done in such a way that the only fundamental database is the activity database. All other databases can be deleted and no data loss will occur.

## **Browser URL problem**

One of the most important features of a time tracker, in my opnion, is the ability to match browser usage with a specific site. On this project I simplified things a bit and I organize the events based on domain (since any small update would create a new event).

To match the URL, I initially create a browser extension that downloads the URL and title of all opened tabs. It downloads again every time there is a tab open, tab close or tab update. Naturally, having to manually accept each download would be a hassle, so unfortunately I had to disable the option: `Ask where to save each file before downloading` in my browser's settings. Which did impact the UX significantly.

So I arrived at a better solution, I created a custom browser extension that sends a GET request to my dash server. The GET request sends all titles and URLs of the opened sites through the GET request parameters. This solution proved excellent, since it had negligible impact on performance and memory usage.

## **Audio detection problem**

I could not find a good way to detect if audio was playing in windows. After messing with a lot of libraries and ending up with `winrt`, I noticed that it worked extremely well for some apps, however, did not detect anything from other apps. So I needed a better solution.

After some thought, I decided to go a different direction and record the audio from from the desktop and analyze the volume of the recording later. However, in doing so, I arrived at a better solution. I decided to stream the data from the recording, but bypass the recording entirely. Therefore I simply converted the binary data that was supposed to be a recording into volume intensity, which I then used to determine if any sound was playing.
