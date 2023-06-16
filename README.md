# Productivity autotracker

This project began with a desire to have a time tracking software with the automatic nature of Rescuetime, the flexibility of Toggl and a custom-made data analysis.

## How it works

This program works by having it constantly running (I always have a terminal running a couple programs). It is periodically getting your active window and other pieces of information to determine what you are doing and if you are idle.

Having the window information, the program will try to classify it using the rules defined in the `config/categories.yml` and `config/config.yml`.

### Configuration files

1. `config/categories.yml`:
    - This file has regex patterns used to match your current activity to either the personal or work category.
    - Any activity that does not match is considered neutral.

2. `config/config.yml`:
    - This file has some values that can be personalized, including color, intervals, spacings and others.
    - The `URLS_PATH` variable is your standard download location, which is where the custom  browser extension will save the URLs file.
    - The `HIDDEN_APPS` list is used to define processes that should have their title information hidden (E.g. `explorer.exe` shows which folder you are currently on, this may be undesirable).
    - The `FULLSCREEN_APPS` list is used to detect non-idle activity when the process is in fullscreen (if a process that is not on this list is fullscreen and the program has not detected activity for some time, it will consider the state as idle).

### Idle detection

If the program detects you are idle, it will display a warning modal like this:

<p align="center">
  <img src="https://github.com/rokobo/Productivity-autotracker/blob/main/images/idle_warning.png?raw=true"/>
</p>

You also have the option to set your status as idle with the top-right button of the main page.

## Pages

Pages are divided into three categories: Productivity, Analytics and Troubleshooting.

- **Productivity pages**:
  - `Dashboard page` - Contains the categoried and aggregated events, along with a graph with the total daily time of each category.

- **Analytics pages**:

- **Troubleshooting pages**:
  - `Activity table` - Contains a scrollable version of the `activity.db` file.
  - `Categories table` - Contains a scrollable version of the `categories.db` file.
  - `Input tables` - Contains a scrollable version of the `audio.db`, `backend.db`, `frontend.db`, `mouse.db`, `keyboard.db`, `fullscreen.db` and `date.db` files.

## Browser URL problem

One of the most important features of a time tracker, in my opnion, is the ability to match browser usage with a specific site. On this project I simplified things a bit and I organize the events based on domain (since any small update would create a new event).

To match the URL, I had to create a custom browser extension that downloads the URL and title of all opened tabs. It downloads again every time there is a tab open, tab close or tab update.

Naturally, having to manually accept each download would be a hassle, so unfortunately I had to disable the option: `Ask where to save each file before downloading` in my browser's settings. I have yet to find a better and more **reliable** way to get the URL.
