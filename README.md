# fb-messages

Steps to run `parse-messages.py`:
1. Go download your [Facebook messaging data](http://facebook.com/dyi). Select the relevant date range and select the **JSON** data format. Under "Your Information", select only "Messages". Download & unzip.
2. Run `parse-messages.py` with the arguments:
  - Your (Facebook) name in quotations (e.g., 'Your Name')
  - A group chat max number of participants limit -- you probably don't *really* talk to anyone in a group chat of 50 people, so you can choose to discard large group chats like that. The inputted group chat limit *n* is inclusive (e.g., it includes group chats with <=n participants).
  - A list of directories containing your downloaded Facebook data. (If the data is large enough, Facebook will provide multiple folders.) Each directory should include subdirectories like `inbox`, `stickers_used`, etc...
  
  For example:
  ```
  python parse-messages.py 'Weizhen Sheng' 6 messages_2016-2020-1 messages_2016-2020-2
  ```
  
  where my Facebook messaging data for 2016-2020 is stored in two separate directories.
