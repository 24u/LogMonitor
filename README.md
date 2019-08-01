Get notified (only) when your server needs your attention
----

To maintain any kind of server efficiently, LogMonitor allows you to get quickly notified when the server needs your immediate attention and NOT notified about things that are not important to you.


Watch FileMaker Server
-

FileMaker Server used to have the option to send e-mail notifications about errors and warnings. Version 17 removed the option for warning notifications. With LogMonitor you get this feature back in an even more flexible alternative. You can get notified even about scripting errors if they are important for you.


Watch other server apps
-

LogMonitor lets you define multiple different log files to monitor and different patterns to look for in the logs, so you can use it to monitor any app that logs important events to a readable text file. LogMonitor is even able to handle log rolling, as long as you can define name pattern for the log files.


Get notified fast via push notifications
-

In addition to sending e-mails, LogMonitor can send push notifications to your smart phone via [Pushover](https://pushover.net). You can enable push notifications separately for each pattern, so you can get push notifications for urgent issues and only e-mail notifications about things that do not require immediate attention.


Get notified, not spammed
-

LogMonitor does not send an e-mail and push notification for every single log entry that matches your pattern. Instead, it sends a single notification as a digest of all issues it has discovered since last check, sorted by importance.


Open Source
-

We at 24U believe that not only server admins, but everyone will benefit from server admins being able to address issues efficiently and in timely manner, for instance by experiencing shorter downtimes of our favorite online services, therefore we decided to make LogMonitor available as Open Source, under the GNU LGPLv3 license. We will, of course, appreciate any feedback or suggestions how to make it even better.

We will greatly appreciate your contributions, although we cannot provide free support for the tool. You may, however, hire us to help you with your projects for money by purchasing our services at [https://www.24uSoftware.com/LogMonitor](https://www.24uSoftware.com/LogMonitor#buy) or by utilizing our custom development services, available at [https://www.24uSoftware.com/custom-apps](https://www.24uSoftware.com/custom-apps).


Requirements
--

* Python3.6
* or macOS python3 must be installed at /usr/local/bin
* Note: if you need python3 to be installed at different location it is necessary to modify the script manually


How to install LogMonitor
--

To install LogMonitor, follow these steps:

1. If you did not do this yet, download and unzip the LogMonitor distribution archive (DA)
2. Open the Installer
3. Fill out the LogMonitorConfig.txt

How to uninstall LogMonitor
--

To uninstall LogMonitor on macOS, follow these steps:

~~~
sudo launchctl unload /Library/LaunchDaemons/com.24usoftware.LogMonitor.plist

sudo rm -r "/Library/Application Support/24U/LogMonitor"
~~~

To uninstall LogMonitor on Windows, follow these steps:

1. Open "Task Scheduler"
2. Select the "Task Scheduler Library". You should see the list of current tasks
3. Select "LogMonitor" task
4. Click at "Delete" and confirm
5. In the "Command Prompt" enter "rmdir /s /q %appdata%\24u\LogMonitor"

Default settings
--

If the "regex_row" options in the datasets in the configuration file are unchanged then LogMonitor attempts to send all warnings except for warning 31 and all scripting errors per email.
Install the latest version with:

License
--

LogMonitor is licensed under the "GNU LGPLv3" License.









