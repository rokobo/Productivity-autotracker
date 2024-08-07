# **Productivity autotracker**

<p align="center">
  <img src="https://github.com/rokobo/Productivity-autotracker/blob/main/thumbnail.png?raw=true"/>
</p>

This project began with a desire to have a time tracking software with the automatic nature of Rescuetime, the flexibility of Toggl and a custom-made data analysis.

- [**Productivity autotracker**](#productivity-autotracker)
  - [**Running the app**](#running-the-app)
  - [**How it works**](#how-it-works)
    - [**Configuration files**](#configuration-files)
    - [**Idle detection**](#idle-detection)
  - [**Pages**](#pages)
  - [**Flashcards**](#flashcards)
  - [**Redundancies and error management**](#redundancies-and-error-management)
  - [**Crowns and study advisor**](#crowns-and-study-advisor)
  - [**Backup system**](#backup-system)
  - [**Browser URL problem**](#browser-url-problem)
  - [**Audio detection problem**](#audio-detection-problem)

## **Running the app**

You need to have `docker` and `docker-compose` installed on your computer. Navigate to the root directory `Productivity-autotracker/`, activate the virtual environment:

```bash
source .venv/bin/activate
```

then run the start script `start.sh`:

```bash
./start.sh
```

This script will start the docker containers and run the app. Stopping the app will not stop the docker containers, you need to do it manually. However, if you stop the app and not the containers, the `start.sh` script can still be used normally.

## **How it works**

This program works by having it constantly running (I run it in VSCode to expose the ports to the flashcards). It is periodically getting your active window and other pieces of information to determine what you are doing and if you are idle.

Having the window information, the program will try to classify it using the rules defined in the `config/categories.yml` and `config/config.yml`.

To make this program work, `PyWinCtl` was used to capture the window information.

### **Configuration files**

1. `config/categories.yml`:
    + This file has `RegEx` patterns used to match your current activity to either the personal or work category.
    + Any activity that does not match is considered neutral.
    + An example file is provided in the `config` folder. Do note that the file has to be named `categories.yml` and placed in the `config` folder for it to work.

2. `config/config.yml`:
    + This file has some values that can be personalized, including color, intervals, spacings and others.

### **Idle detection**

If the program detects you are idle, it will display a blinking warning overlay. You also have the option to set your status as idle with the top-right button of the main page. Do note that the idle detection uses multiple sources of activity detection, specifically: audio, keyboard and mouse. If you press the button and move your mouse or forget to pause music, the idle status will be reverted.

## **Pages**

Pages are divided into three categories: Productivity, Analytics and Troubleshooting.

+ **Productivity pages**:
  + `Dashboard page` - Contains the categoried and aggregated events, along with a graph with the total daily time of each category.
  + `Flashcards page` - Contains an interface for studying your flashcards.

+ **Analytics pages**:
  + `Goals page` - Contains heatmaps that track progress on a number of goals defined by the user.
  + `Trends page` - Contains bar graphs for work and personal activity in three different time ranges.
  + `All events page` - Contains all recorded events separated into categories and sorted by time. Can help see what you spend most time on and serves to see if there are any neutral events that should be categorized.

+ **Customization pages**:
  + `Configuration page` - Offers ways to modify the contents of `config.yaml`.
  + `Categories page` - Offers ways to modify the contents of `categories.yaml`.

+ **Troubleshooting pages**:
  + `Activity table` - Contains a scrollable version of the `activity.db` file.
  + `Categories table` - Contains a scrollable version of the `categories.db` file.
  + `URLs table` - Contains a scrollable version of the `urls.db` file.
  + `Input tables` - Contains a scrollable version of the `audio.db`, `backend.db`, `frontend.db`, `mouse.db`, `keyboard.db` and `date.db` files.
  + `Milestones table` - Contains a scrollable version of the `milestones.db` file.

+ **Credits**:
  + `Attributions page` - Contains image attributions for assets used in this project.

## **Flashcards**

Flashcards can be created in the `/flashcards` directory. There, you can create a markdown file, whose name will be the name of the deck of the flashcards. Inside the markdown file, you can add flashcards by putting a question as a header and the answer under it. For example:

```markdown
# Question 1 ...?

Answer 1

# Question 2...?

Answer 2
```

You can use markdown normally in the files. This was done so that the flashcards can be easily modified and added to the program, as well as for aesthetic reasons. You can even add images to the file, just put them in the `/flashcards/images` directory.

Additionally, one thing I personally do to enhance my experience with this functionality is to enable port forwarding in Visual Studio Code. This way, I can access the flashcards from my phone, tablet, or laptop.

## **Redundancies and error management**

The program uses a configuration file to define various parameters like database paths, schema file locations, and retry attempts as well as database schemas, which are defined in separate SQL files and are loaded to create and test the main `activity.db` database.

The program consistently checks for the existence of database files before attempting operations, ensuring that it does not proceed on invalid paths. This is done with the retry decorator `@retry`, which is implemented to handle transient issues like temporary database locks or momentary I/O interruptions. In case of failure, the program uses a clear messaging system for errors, making it easier for users to understand the nature of the failure. Additional error information can be found in the log file `./logs/retry.log`.

Upon exhausting all retries, the program either exits the thread or core gracefully (indicating an unresolved issue that requires attention) or simply does nothing if the failure is not catastrophic. The `main.py` script then ensures that all background processes and threads are continually monitored and maintained. Its robust error handling and restart mechanisms aim to provide a stable and resilient operation of the application, adapting to any runtime anomalies or failures.

## **Crowns and study advisor**

On the background, the study advisor routine is running. It sends desktop notifications when you reach certain goals or pass the daily personal activity limit.

Additionally, the main dashboard page has crowns that represent the percentage of your daily study goals over different intervals. It will sum how much of each day's goal you achieved. Depending on your percentage, a different crown will appear. Settings changes the percentage values for each crown.

## **Backup system**

To prevent possible data deletion, the `activity.db` file is periodically backed up in the `backup` folder. Interval between backups and number of stored backups can be changed in settings.

This program was done in such a way that the only fundamental database is the activity database. All other databases can be deleted and no data loss will occur.

The backup system is handled by Apache Airflow.

## **Browser URL problem**

One of the most important features of a time tracker, in my opnion, is the ability to match browser usage with a specific site. On this project I simplified things a bit and I organize the events based on domain (since any small update would create a new event).

To match the URL, I initially create a browser extension that downloads the URL and title of all opened tabs. It downloads again every time there is a tab open, tab close or tab update. Naturally, having to manually accept each download would be a hassle, so unfortunately I had to disable the option: `Ask where to save each file before downloading` in my browser's settings. Which did impact the UX significantly.

So I arrived at a better solution, I created a custom browser extension that sends a GET request to my dash server. The GET request sends all titles and URLs of the opened sites through the GET request parameters. This solution proved excellent, since it had negligible impact on performance and memory usage.

## **Audio detection problem**

I could not find a good way to detect if audio was playing. After messing with a lot of libraries and ending up with `winrt`, I noticed that it worked extremely well for some apps, however, did not detect anything from other apps. So I needed a better solution.

After some thought, I decided to go a different direction and record the audio from from the desktop and analyze the volume of the recording later. However, in doing so, I arrived at a better solution. I decided to stream the data from the recording, but bypass the recording entirely. Therefore I simply converted the binary data that was supposed to be a recording into volume intensity, which I then used to determine if any sound was playing.
