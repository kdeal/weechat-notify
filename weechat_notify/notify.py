import re
from argparse import ArgumentParser
from getpass import getpass
from time import sleep

from pync import Notifier
from pyweechat import WeeChatSocket

FORMATTING = re.compile(r'(\x19F?(\*|!|/|_|\|)*(\d\d|@\d\d\d\d\d)|\x1c|\x1a.?|\x1b.?)')


def strip_formatting(string):
    return FORMATTING.sub('', string)


class WeechatNotifier:

    def __init__(self, hostname, port, use_ssl=True, cafile=None):
        kwargs = {}
        if cafile is not None:
            kwargs['custom_cert'] = {'cafile': cafile}

        self.buffers = {}
        self.weechat = WeeChatSocket(
            hostname=hostname,
            port=port,
            use_ssl=use_ssl,
            **kwargs
        )

    def get_buffers(self):
        self.weechat.send_async('hdata buffer:gui_buffers(*) full_name')
        result = self.weechat.wait()
        for buf in result.get_hdata_result():
            for path in buf['__path']:
                self.buffers[path] = buf['full_name']

    def buffer_opened_cb(self, buf):
        for path in buf['__path']:
            self.buffers[path] = buf['full_name']

    def buffer_closing_cb(self, buf):
        for path in buf['__path']:
            self.buffers.pop(path, None)

    def line_added_cb(self, line):
        if line['highlight'] == b'\x01':
            channel = self.buffers.get(line['buffer'], '#unknown').rsplit('.', 1)[-1]
            Notifier.notify(
                strip_formatting(line['message']),
                title=strip_formatting(f'{line["prefix"]} in {channel}'),
                activate='com.googlecode.iterm2',
                appIcon='./weechat.png',
                contentIcon='./weechat.png',
            )

    def run(self):
        relay_pass = getpass(prompt='Relay Password:')
        self.weechat.connect(password=relay_pass)
        self.weechat.on('buffer_line_added', self.line_added_cb)
        self.weechat.on('buffer_opened', self.buffer_opened_cb)
        # TODO: test that a renamed buffer will still have the same path
        self.weechat.on('buffer_remaned', self.buffer_opened_cb)
        self.weechat.on('buffer_closing', self.buffer_closing_cb)

        self.get_buffers()

        try:
            while True:
                self.weechat.send('sync')
                while self.weechat.poll():
                    pass
                sleep(5)
        finally:
            self.weechat.disconnect()


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('relay_hostname', help='hostname relay is running on')
    parser.add_argument('port', type=int, help='port relay is running on')
    parser.add_argument(
        '--no-ssl',
        action='store_false',
        dest='use_ssl',
        help='don\'t use ssl when connecting to relay',
    )
    parser.add_argument('--ca', help='Certificate file')
    return parser.parse_args()


def main():
    args = parse_args()
    WeechatNotifier(
        hostname=args.relay_hostname,
        port=args.port,
        use_ssl=args.use_ssl,
        cafile=args.ca,
    ).run()


if __name__ == '__main__':
    main()
