import argparse
import sys

from datetime import datetime
from rich.align import Align

from textual.app import App
from textual.widget import Widget
import time

import json


class Clock(Widget):
    def on_mount(self):
        self.set_interval(1, self.refresh)

    def render(self):
        time = datetime.now().strftime("%c")
        return Align.center(time, vertical="middle")


class SpeedViewer(Widget):

    reader_speed = 300

    @classmethod
    def increment_speed(cls, delta):
        cls.reader_speed += delta

    def on_mount(self):
        self.set_interval(0.2, self.refresh)

    def render(self):
        self.str_of_reader_speed = str(self.reader_speed)
        return Align.center(self.str_of_reader_speed, vertical="middle")


class SpeedReader(Widget):

    reader_speed = 300
    refresh_rate = 60 / reader_speed
    counter = 0
    pause_flag = False
    filename = ""
    text_blob = ""
    num_tokens = 0
    chunk = 1
    output = ""

    @classmethod
    def increment_wpm(cls, delta):
        cls.reader_speed += delta
        cls.refresh_rate = 60 / (cls.reader_speed)

    @classmethod
    def open_file(cls, filename):
        cls.filename = filename
        with open(filename, "r") as f:
            cls.text_blob = f.read().split()
            cls.num_tokens = len(cls.text_blob) // cls.chunk
            f.close()

    @classmethod
    def read_stdin(cls, stdin):
        cls.text_blob  = stdin.read().split()
        cls.num_tokens = len(cls.text_blob) // cls.chunk

    @classmethod
    def pause(cls):
        cls.pause_flag = True

    @classmethod
    def resume(cls):
        cls.pause_flag = False

    @classmethod
    def go_forward(cls):
        cls.counter += 100
        if (cls.counter + cls.chunk - 1) < cls.num_tokens:
            cls.counter = cls.num_tokens - 1

    @classmethod
    def go_back(cls):
        cls.counter -= 100
        if (cls.counter) < 0:
            cls.counter = 0

    @classmethod
    def save_reading_location(cls):
        with open(cls.filename + "_location", "w") as f:
            data = {"counter": cls.counter * cls.chunk}
            json_data = json.dumps(data)
            f.write(json_data)

    def on_mount(self):
        self.set_interval(60 / (self.reader_speed / self.chunk), self.refresh)

    def render(self):
        if (
            SpeedReader.counter + SpeedReader.chunk - 1
        ) < self.num_tokens and not SpeedReader.pause_flag:
            self.output = " ".join(
                self.text_blob[
                    SpeedReader.counter : SpeedReader.counter + SpeedReader.chunk
                ]
            )
            SpeedReader.counter += SpeedReader.chunk
        else:
            self.output = self.text_blob[SpeedReader.counter - 1]
        return Align.center(self.output, vertical="middle")


class SpeedReaderApp(App):
    async def on_load(self) -> None:
        """bind keys"""
        await self.bind("q", "quit", "Quit")
        await self.bind("f", "increase_speed", "Increase Speed")
        await self.bind("j", "decrease_speed", "Decrease Speed")
        await self.bind("p", "pause", "pause playing")
        await self.bind("r", "resume", "unpause playing")
        await self.bind("s", "save_reading_location", "save location")

    def action_increase_speed(self) -> None:
        """increase speed reader speed"""
        SpeedReader.increment_wpm(50)
        SpeedViewer.increment_speed(50)

    def action_decrease_speed(self) -> None:
        """decrease speed reader speed"""
        SpeedReader.increment_wpm(-50)
        SpeedViewer.increment_speed(-50)

    def action_pause(self) -> None:
        """pause the player"""
        SpeedReader.pause()

    def action_resume(self) -> None:
        """resume from pasused state"""
        time.sleep(1)
        SpeedReader.resume()

    def action_go_forward(self) -> None:
        """go forward _ tokens"""
        SpeedReader.counter = 0

    def action_go_back(self) -> None:
        """go backwards _ tokens"""
        SpeedReader.go_back()

    def action_save_reading_location(self) -> None:
        """save reading location"""
        SpeedReader.save_reading_location()

    async def on_mount(self) -> None:
        await self.view.dock(SpeedReader(), edge="left", size=40)
        await self.view.dock(SpeedViewer(), Clock(), edge="top")

def calc_resume_location(savefile):
    with open(savefile, "r") as f:
        savepoint = json.load(f)
        SpeedReader.counter = savepoint["counter"]


def parse_args():
    parser = argparse.ArgumentParser(description="Speed Reader")

    parser.add_argument(
        "stdin", nargs="?", type=argparse.FileType("r"), default=sys.stdin
    )

    parser.add_argument(
        "-s",
        "--speed",
        type=int,
        default=300,
        help="wpm of the reader, defaults to 300",
    )
    parser.add_argument(
        "-c",
        "--chunk",
        type=int,
        default=3,
        help="number of words at a time to show",
    )
    parser.add_argument(
        "-f",
        "--input-file",
        type=str,
        help="input file",
    )
    parser.add_argument(
        "-b",
        "--bookmark",
        type=str,
        help="name of bookmark file",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    SpeedViewer.reader_speed = args.speed
    SpeedReader.reader_speed = args.speed
    SpeedReader.chunk = args.chunk

    if not args.stdin:
        SpeedReader.open_file(args.input_file)
    else:
        SpeedReader.read_stdin(args.stdin)
        sys.stdin = open('/dev/tty')


    if args.bookmark:
        SpeedReader.pause()
        calc_resume_location(args.bookmark)

    SpeedReaderApp.run()


if __name__ == "__main__":
    main()
