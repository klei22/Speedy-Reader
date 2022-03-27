# Speedy-Reader

Textual/Rich based speed reading cli app.

## Usage with text files

From website:
```sh
w3m --dump url | python3 speedreader.py -s 400 -c 3
```

From pdf:
```sh
lesspipe test.pdf | python3 speedreader.py -s 400 -c 3
```

From text file:

```sh
python3 speedreader.py -s 400 -c 3 -f text.txt
```

## References

- Highlighting, Color, Font-Style: [Rich Text](https://rich.readthedocs.io/en/stable/text.html?highlight=Text)

