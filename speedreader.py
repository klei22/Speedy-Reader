import argparse
import sys

from datetime import datetime
from datetime import timedelta
from rich.align import Align
from rich.text import Text

from textual.app import App
from textual.widget import Widget
import time

import json

initial_time = datetime.now()


class Sidebar(Widget):

    end_time = datetime.now()
    filename = None
    last_time_estimate = ""

    def on_mount(self):
        self.set_interval(1, self.refresh)

    def render(self):

        tokens_remaining = (SpeedReader.num_tokens - 1) - SpeedReader.counter
        tokens_per_second = (SpeedReader.reader_speed) / 60
        seconds_remaining = tokens_remaining / tokens_per_second

        text = "%s\n" % Clock.get_time()
        text += "WPM: %s\n" % SpeedViewer.get_current_speed()
        if self.filename:
            text += "Filename: %s\n" % self.filename
        else:
            text += "Reading stdin\n"
        text += "Location: %s/%s\n" % (SpeedReader.counter + 1, SpeedReader.num_tokens)
        text += "Percentage: %3.1f %%\n" % (
            100 * SpeedReader.counter / (SpeedReader.num_tokens - 1)
        )
        text += "Time Remaining: %.2f\n" % (seconds_remaining)
        text += "Tokens Remaining: %.d\n" % (tokens_remaining)

        if (not SpeedReader.pause_flag) and (tokens_remaining != 0):
            self.last_time_estimate = datetime.now() + timedelta(seconds=seconds_remaining)

        if isinstance(self.last_time_estimate, datetime):
            text += "Complete at: %s" % (self.last_time_estimate.strftime("%b %d, %H:%M:%S"))

        return Align.center(text, vertical="middle")


class Clock:
    @classmethod
    def get_time(cls):
        return datetime.now().strftime("%c")


class SpeedViewer:

    reader_speed = 300

    @classmethod
    def increment_speed(cls, delta):
        cls.reader_speed += delta

    @classmethod
    def get_current_speed(cls):
        return str(cls.reader_speed)


class SpeedReader(Widget):

    reader_speed = 300
    refresh_rate = 60 / reader_speed
    counter = 0
    pause_flag = False
    filename = ""
    text_blob = ""
    num_tokens = 0
    chunk = 1
    seconds_remaining = 0
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
        cls.text_blob = stdin.read().split()
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
        # await self.bind("f", "increase_speed", "Increase Speed")
        # await self.bind("j", "decrease_speed", "Decrease Speed")
        await self.bind("p", "pause", "pause playing")
        await self.bind("r", "resume", "unpause playing")
        await self.bind("s", "save_reading_location", "save location")
        await self.bind("c", "view.toggle('clock')", "save location")
        await self.bind("f", "view.toggle('sidebar')", "save location")

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
        self.speed_reader = SpeedReader()
        self.sidebar = Sidebar()

        await self.view.dock(self.sidebar, edge="left", size=30, name="sidebar")

        # dock body in remaining space
        await self.view.dock(self.speed_reader, edge="right")


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

    if args.input_file:
        SpeedReader.open_file(args.input_file)
        Sidebar.filename = args.input_file
    else:
        SpeedReader.read_stdin(args.stdin)
        sys.stdin = open("/dev/tty")

    if args.bookmark:
        SpeedReader.pause()
        calc_resume_location(args.bookmark)

    SpeedReaderApp.run()


if __name__ == "__main__":
    main()
