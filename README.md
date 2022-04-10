# Speedy-Reader

Speedy-Reader is a Textual/Rich based speed reading cli app.

Nice and centered within the terminal, optional non-instrusive sidebar with statistics.

Can accept both piped input as well as text input, with features for saving and resuming from bookmarks.

## Usage Automatic Reading

Press 'p' to pause auto scrolling 'r' to resume auto scrollign.

While paused, use '+'/'-' to manually scroll (still really great)

From website:
```sh
w3m --dump url | python3 speedyreader.py -s 400 -c 3
```

From pdf:
```sh
lesspipe test.pdf | python3 speedyreader.py -s 400 -c 3
```

From text file:

```sh
python3 speedyreader.py -s 400 -c 3 -f text.txt
```

## Main flags

### Speed in Words Per Minute (wpm)

The speed is in words per minute.
Typical good starting speed is 300wpm, varies with the type of content.

Use the `-s` flag to set your desired speed.


### Chunk size

Peripheral vision can often pick up side words with ease.
setting `-c` to 3, make three words appear at a time for example.

The larger the chunk size, the lower the refresh rate for the same WPM.

So -c 3 refreshes 1/3 the rate as -c 1 for example.

### Resume

Use the bookmark flag `-b` to resume from saved location

## In App Commands

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

