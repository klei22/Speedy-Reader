# ⚡ Speedy-Reader ⚡

![banner](./img/speedreader_banner.png)

Speedy-Reader is a Textual/Rich based speed reading cli app.

Read faster within the command line.

Nice and centered within the terminal, foldable sidebar with statistics.

Can accept both piped input as well as text input, with features for saving and resuming from bookmarks.

## Basic Usage

After app starts, press `r` to start the auto-scroller.

```sh
python3 speedreader.py -s 300 -c 3 -f README.md
```
- Press `p` to pause auto scrolling `r` to resume auto scrolling.
- Press `f` to toggle fullscreen (hides the sidebar and recenters text)
- While paused, use `+`/`-` to manually scroll (still really great)
- Press `s` to save bookmark at current location for later reading

# Demo

![demo](./img/high_res_demo.gif)

## Basic Flags

- `-s <wpm> ` speed of reading in words-per-minute (defaults to 300)
- `-f <filename>` text based file to read (stdout also supported, see next section)
- `-c <chunk-size>` number of words to show per frame ('word-chunk' size)
- `-b <bookmark>` designate bookmark file to use to resume reading

###  Websites, PDFs and piped inputs

From website:
```sh
w3m --dump url | python3 speedyreader.py -s 400 -c 3
```

From pdf:
```sh
lesspipe test.pdf | python3 speedyreader.py -s 400 -c 3
```
## In App Commands - Full Listing

- `s` -  save location bookmark (saves to file in same directory)
- `f` -  toggle fullscreen mode
- `p` -  pause playing
- `r` -  unpause playing
- `+` -  move forward _ words (defaults to chunksize if -i not set)
- `-` -  move backward _ words (defaults to chunksize if -i not set)
- `T` -  go to start of the text
- `q` -  quit

## References

- Highlighting, Color, Font-Style: [Rich Text](https://rich.readthedocs.io/en/stable/text.html?highlight=Text)
- Python CLI TUI Framework: [Textualize](https://github.com/Textualize)

