import os
import logging
import base64

from datetime import datetime

import glib
glib.threads_init()

import pygst
pygst.require('0.10')
import gst


RTSP_URL = "rtsp://%s:554/cam/realmonitor?channel=%d&subtype=00&authbasic=%s"
USERNAME = "admin"
PASSWORD = "random"
HOSTNAME = "127.0.0.1"

class ChannelRecorder(object):
    def __init__(self, channel, directory="/tmp"):
        self.channel = channel
        self.pipeline = None
        self.current_file_handle = None
        self.current_filename = None
        self.directory = directory
        self.logger = logging.getLogger("ChannelRecorder_%d" % (self.channel,))

    def record(self):
        self.logger.debug("Initialising pipeline to start recording")
        pipeline_src = RTSP_URL % (HOSTNAME, self.channel, base64.encodestring("%s:%s" % (USERNAME, PASSWORD)[:-1]))
        pipeline_src += " ! rtph264depay ! h264parse ! matroskamux streamable=1 ! multifdsink name=fdsink sync-method=2 mode=1 sync=false"
        self.pipeline = gst.parse_launch(pipeline_src)
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)
        self.pipeline.set_state(gst.STATE_PLAYING)

    def on_message(self, bus, message):
        self.logger.debug("Message arrived on channel %d pipeline: %s" % (self.channel, message))
        if message.type == gst.MESSAGE_STATE_CHANGED:
            old, new, pending = message.parse_state_changed()
            if new == gst.STATE_PLAYING and message.src == self.pipeline:
                # connect a file to the multifdsink
                self.change_filename()

        if message.type == gst.MESSAGE_ERROR:
            self.on_error(message)

    def on_error(self, error):
        self.logger.warning("Error occurred %s" % (error,))
        if self.current_file_handle:
            self.current_file_handle.close()
            self.current_file_handle = None
        self.pipeline.set_state(gst.STATE_NULL)
        self.record()

    def change_filename(self):
        now = datetime.utcnow().timetuple()
        new_filename = "%d%02d%02d_%02d%02d.mkv" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)
        self.logger.info("Changing filename that is being recorded to: %s" % (new_filename,))
        handle = self._open_file(os.path.join(self.directory, new_filename), "wb")
        sink = self.pipeline.get_by_name('fdsink')
        sink.emit('add', handle.fileno())
        if self.current_file_handle:
            self._stop_recording(self.current_file_handle)
        self.current_file_handle = handle
        self.current_filename = new_filename

    def _open_file(self, location, mode):
        try:
            handle = open(location, mode)
            return handle
        except IOError, e:
            self.logger.warning("Could not open file %s" % (location,))
            return None

    def _stop_recording(self, handle):
        sink = self.pipeline.get_by_name('fdsink')

        if handle:
            handle.flush()
            sink.emit('remove', handle.fileno())


class Recorder(object):

    def __init__(self, channel_range, initial_directory):
        self.channels = []
        if not os.path.exists(initial_directory):
            os.mkdir(initial_directory)
        for channel in channel_range:
            directory = os.path.join(initial_directory, str(channel))
            if not os.path.exists(directory):
                os.mkdir(directory)
            channel_recorder = ChannelRecorder(channel, directory)
            channel_recorder.record()
            self.channels.append(channel_recorder)
        dt = datetime.utcnow()
        nsecs = dt.minute*60+dt.second+dt.microsecond*1e-6
        self.logger = logging.getLogger("OverallRecorder")
        glib.timeout_add_seconds(int(60 * 60 - nsecs), self._initial_change_recording)
        self.logger.info("Set initial change filename timeout to %d seconds" % (int(60 * 60 - nsecs)))

    def _initial_change_recording(self):
        self.logger.info("Initial change recording")

        for channel in self.channels:
            channel.change_filename()
        glib.timeout_add_seconds(60*60, self._on_hour_change_recording)
        return False

    def _on_hour_change_recording(self):
        self.logger.info("On hour change recording")
        for channel in self.channels:
            channel.change_filename()
        return True

def main():
    logging.basicConfig(filename="/tmp/cctv.log", format='%(asctime)s %(name)-20s %(levelname)-8s %(message)s', level=logging.INFO)

    recorder = Recorder(range(1, 6), "/tmp/cctv")
    ml = glib.MainLoop()
    ml.run()

if __name__ == '__main__':
    main()