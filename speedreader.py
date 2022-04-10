import argparse
import sys

from datetime import datetime
from datetime import timedelta
from rich.align import Align

from textual.app import App
from textual.widget import Widget
import time

import json

initial_time = datetime.now()


def get_time():
    return datetime.now().strftime("%c")


class SpeedViewer:

    # speed in wpm
    reader_speed = 300

    # TODO: add feature to increment/decrement speed while reading
    # @classmethod
    # def increment_speed(cls, delta):
    #     cls.reader_speed += delta

    @classmethod
    def get_current_speed(cls):
        return str(cls.reader_speed)


class SpeedReader(Widget):

    reader_speed = 300
    refresh_rate = 60 / reader_speed
    fast_forward_amount = 30
    rewind_amount = 30
    counter = 0
    pause_flag = False
    filename = ""
    text_blob = ""
    num_tokens = 0
    chunk = 1
    output = ""

    # TODO: add increment decrement wpm feature
    # @classmethod
    # def increment_wpm(cls, delta):
    #     cls.reader_speed += delta
    #     cls.refresh_rate = 60 / (cls.reader_speed)

    @classmethod
    def open_file(cls, filename):
        cls.filename = filename
        with open(filename, "r") as f:
            cls.text_blob = f.read().split()
            cls.num_tokens = len(cls.text_blob)
            f.close()

    @classmethod
    def read_stdin(cls, stdin):
        cls.text_blob = stdin.read().split()
        cls.num_tokens = len(cls.text_blob)

    @classmethod
    def pause(cls):
        cls.pause_flag = True

    @classmethod
    def resume(cls):
        cls.pause_flag = False

    @classmethod
    def go_forward(cls):
        cls.counter += cls.fast_forward_amount
        # attempts to go past the end will reroute to last token
        if (cls.counter + cls.chunk - 1) > cls.num_tokens:
            cls.counter = cls.num_tokens - 1

    @classmethod
    def go_back(cls):
        cls.counter -= cls.rewind_amount
        if (cls.counter) < 0:
            cls.counter = 0

    @classmethod
    def go_to_top(cls):
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
        next_position = SpeedReader.counter + SpeedReader.chunk
        if (next_position) < self.num_tokens and not SpeedReader.pause_flag:
            self.output = " ".join(
                self.text_blob[
                    SpeedReader.counter : SpeedReader.counter + SpeedReader.chunk
                ]
            )
            SpeedReader.counter += SpeedReader.chunk
        else:
            self.output = " ".join(
                self.text_blob[
                    SpeedReader.counter : SpeedReader.counter + SpeedReader.chunk
                ]
            )
        return Align.center(self.output, vertical="middle")


class Sidebar(Widget):

    end_time = datetime.now()
    filename = None
    last_time_estimate = ""
    sidebar_message_buffer = ""

    # time calc variables
    tokens_remaining = None
    tokens_per_second = None
    seconds_remaining = None

    def on_mount(self):
        self.set_interval(0.02, self.refresh)

    def clear_sidebar_message_buffer(self):
        self.sidebar_message_buffer = ""

    def update_time_calc_variables(self):
        self.tokens_remaining = (SpeedReader.num_tokens - 1) - SpeedReader.counter
        self.tokens_per_second = (SpeedReader.reader_speed) / 60
        self.seconds_remaining = self.tokens_remaining / self.tokens_per_second

    def append_percentage_read(self):
        self.sidebar_message_buffer += "Percentage: %3.1f %%\n" % (
            100 * SpeedReader.counter / (SpeedReader.num_tokens - 1)
        )

    def append_wpm(self):
        self.sidebar_message_buffer += "WPM: %s\n" % SpeedViewer.get_current_speed()

    def append_current_time(self):
        self.sidebar_message_buffer = "%s\n" % get_time()

    def append_filename(self):
        if self.filename:
            self.sidebar_message_buffer += "Filename: %s\n" % self.filename
        else:
            self.sidebar_message_buffer += "Reading stdin\n"

    def append_fractional_progress(self):
        """Appends words_read/total_words"""
        self.sidebar_message_buffer += "Location: %s/%s\n" % (
            SpeedReader.counter + 1,
            SpeedReader.num_tokens,
        )

    def append_time_remaining(self):
        """Appends estimated remaining reading time at current wpm rate"""
        self.sidebar_message_buffer += "Time Remaining: %.2f\n" % (
            self.seconds_remaining
        )

    def append_tokens_remaining(self):
        """Appends number of tokens remaining to be read"""
        self.sidebar_message_buffer += "Tokens Remaining: %.d\n" % (
            self.tokens_remaining
        )

    def append_estimated_time_of_completion(self):
        """Appends an estimate of when reader will finish the given text, at the current rate of reading

        Designed behavior is to prevent this field from updating when the
        reader is paused (no sense to update this when the reader is not reading).

        Also no need to update when the reading is complete.
        """

        if not SpeedReader.pause_flag:
            if self.tokens_remaining != 0:
                if self.seconds_remaining != None:
                    self.last_time_estimate = datetime.now() + timedelta(
                        seconds=self.seconds_remaining
                    )

        if isinstance(self.last_time_estimate, datetime):
            self.sidebar_message_buffer += "Complete at: %s" % (
                self.last_time_estimate.strftime("%b %d, %H:%M:%S")
            )

    def render(self):

        # clear buffer used for sidebar text
        self.clear_sidebar_message_buffer()

        # update shared variables
        self.update_time_calc_variables()

        # display general info
        self.append_current_time()
        self.append_filename()

        # display reading progress stats
        self.append_percentage_read()
        self.append_fractional_progress()
        self.append_time_remaining()
        self.append_tokens_remaining()

        # appends estimate when the reader will complete the text
        self.append_estimated_time_of_completion()

        return Align.center(self.sidebar_message_buffer, vertical="middle")


class SpeedReaderApp(App):
    async def on_load(self) -> None:
        """bind keys"""
        await self.bind("q", "quit", "Quit")
        # TODO: add support for increasing and decreasing speed while reading
        # await self.bind("+", "increase_speed", "Increase Speed")
        # await self.bind("-", "decrease_speed", "Decrease Speed")
        await self.bind("p", "pause", "pause playing")
        await self.bind("r", "resume", "unpause playing")
        await self.bind("s", "save_reading_location", "save location")
        await self.bind("f", "view.toggle('sidebar')", "toggle fullscreen mode")
        await self.bind("+", "go_forward", "move forward _ words")
        await self.bind("-", "go_back", "move backward _ words")
        await self.bind("T", "go_to_top", "go to start of the text")

    # TODO: add support for increasing and decreasing speed while reading
    # def action_increase_speed(self) -> None:
    #     """increase speed reader speed"""
    #     SpeedReader.increment_wpm(50)
    #     SpeedViewer.increment_speed(50)

    # def action_decrease_speed(self) -> None:
    #     """decrease speed reader speed"""
    #     SpeedReader.increment_wpm(-50)
    #     SpeedViewer.increment_speed(-50)

    def action_pause(self) -> None:
        """pause the player"""
        SpeedReader.pause()

    def action_resume(self) -> None:
        """resume from paused state"""
        time.sleep(1)
        SpeedReader.resume()

    def action_go_forward(self) -> None:
        """go forward _ tokens"""
        SpeedReader.go_forward()

    def action_go_back(self) -> None:
        """go back _ tokens"""
        SpeedReader.go_back()

    def action_go_to_top(self) -> None:
        """go to the start of the text"""
        SpeedReader.go_to_top()

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
    parser.add_argument(
        "-i",
        "--increment-amount",
        type=int,
        help="the number of words moved when rewinding/fast-forwarding, if not set, defaults to chunksize",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    SpeedViewer.reader_speed = args.speed
    SpeedReader.reader_speed = args.speed
    SpeedReader.chunk = args.chunk


    if args.increment_amount is None:
        SpeedReader.fast_forward_amount = args.chunk
        SpeedReader.rewind_amount = args.chunk
    else:
        SpeedReader.fast_forward_amount = args.increment_amount
        SpeedReader.rewind_amount = args.increment_amount

    SpeedReader.pause()

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
