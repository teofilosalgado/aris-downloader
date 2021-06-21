# Aris Downloader
An automated solution to download ARIS models using Selenium. 
This script collection was intended to traverse entire ARIS databases downloading all model files in a single execution, saving a lot of time. In the end, it also generates a graph allowing for advanced visualization of the current scenario.

## How it works?
It works by traversing all the groups and models in an ARIS database using Selenium, building a tree-like structure in a local SQLite database. After that, you will be able to choose to download those models in .png or .pdf.

## How to run it?
The execution of this tool can be divided into two steps: traversing and downloading. Both steps will be explained below.

- ### Traversing
  Execute `traverse.py` found inside the `src` folder like so:
  ```
  traverse.py [-h] base_url database_name username password item_url item_title
  ```
  Where:
  - `base_url`
  Base URL before '/'.
  - `database_name`
  Database name as you can see in the right corner of ARIS connect.
  - `username`
  User authentication name.
  - `password`
  User authentication password.
  - `item_url`
  Unique root item URL. Normally found after '/#insights/item/'.
  - `item_title`
  Item title. You can copy it from your browser.

  As an example:
  ```
  traverse.py 
    "https://modeling.domain.tenant.com" 
    "My TOM Database" 
    "My user" 
    "My password" 
    "c.group.My TOM Database.9VXcoVbREeoGPAANOirxQA.-1" 
    "Item Name"
  ```

  After that, you will found an SQLite database in the `output` folder, inside the cloned repository. This database contains all the visited models and pages in a tree structure made by `node` and `edge` tables.
  

- ### Downloading
  **TBD**

## Minimum requirements:
 - Python: 3.5

ARIS is a trademark of Software AG and is used here to refer to specific technologies. No endorsement by Software AG is implied.
