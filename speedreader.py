import argparse
from datetime import datetime
from rich.align import Align

from textual.app import App
from textual.widget import Widget


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
    file_handle = None
    line_buffer = ''
    num_lines = 0
    output = ''

    @classmethod
    def increment_wpm(cls, delta):
        cls.reader_speed += delta
        cls.refresh_rate = 60 / (cls.reader_speed)

    @classmethod
    def open_file(cls, filename):
        cls.file_handle = open(filename, "r")
        cls.line_buffer = cls.file_handle.readlines()
        cls.num_lines = len(cls.line_buffer)
        cls.file_handle.close()

    @classmethod
    def pause(cls):
        cls.pause_flag = True

    @classmethod
    def resume(cls):
        cls.pause_flag = False

    def on_mount(self):
        self.set_interval(self.refresh_rate, self.refresh)

    def render(self):
        if self.counter < self.num_lines and not self.pause_flag:
            self.output = "%s %s %f %d" % (
                self.line_buffer[self.counter],
                str(self.counter),
                self.refresh_rate,
                self.reader_speed,
            )
            self.counter += 1
        else:
            self.output = "%s %s %f %d" % (
                self.line_buffer[self.counter - 1],
                str(self.counter),
                self.refresh_rate,
                self.reader_speed,
            )
        return Align.center(self.output, vertical="middle")


def parse_args():
    parser = argparse.ArgumentParser(description="Speed Reader")

    parser.add_argument(
        "-s",
        "--speed",
        type=int,
        default=300,
        help="wpm of the reader, defaults to 300",
    )
    parser.add_argument(
        "-f",
        "--input-file",
        type=str,
        help="input file",
        required=True,
    )

    return parser.parse_args()


class SpeedReaderApp(App):
    async def on_load(self) -> None:
        """bind keys"""
        await self.bind("q", "quit", "Quit")
        await self.bind("f", "increase_speed", "Increase Speed")
        await self.bind("j", "decrease_speed", "Decrease Speed")
        await self.bind("p", "pause", "pause playing")
        await self.bind("r", "resume", "unpause playing")

    def action_increase_speed(self) -> None:
        """increase speed reader speed"""
        SpeedReader.increment_wpm(50)
        SpeedViewer.increment_speed(50)

    def action_decrease_speed(self) -> None:
        """decrease speed reader speed"""
        SpeedReader.increment_wpm(-50)
        SpeedViewer.increment_speed(-50)

    def action_pause(self) -> None:
        """decrease speed reader speed"""
        SpeedReader.pause()

    async def on_mount(self) -> None:
        await self.view.dock(SpeedReader(), edge="left", size=40)
        await self.view.dock(SpeedViewer(), Clock(), edge="top")


def main():
    args = parse_args()
    SpeedReader.open_file(args.input_file)

    SpeedViewer.reader_speed = args.speed
    SpeedReader.reader_speed = args.speed

    SpeedReaderApp.run()


if __name__ == "__main__":
    main()
