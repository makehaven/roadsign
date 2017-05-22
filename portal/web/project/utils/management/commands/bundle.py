# -*- coding: utf-8 -*-

import os
from collections import deque
from contextlib import contextmanager
from subprocess import check_call, Popen, PIPE

from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now

DATETIME_FORMAT = '%Y%m%d_%H%M%S'

# saves cursor position
SAVE = '\x1b7'

# restores cursor position and clears remainder of screen
RESTORE = '\x1b8\x1b[0J'


class Command(BaseCommand):
    help = 'Build/bundle the application for deployment to production.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-o', '--output', default=None, dest='output',
            help='Specifies file to which the output is written.'
        )
        parser.add_argument(
            '-r', '--git-reference', default='master', dest='ref',
            help='Git reference to bundle, e.g. a branch or commit hash.',
        )

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.rows, self.cols = self.get_terminal_size()
        self.sep = '    %s' % (u'═' * (self.cols - 8))

    def get_terminal_size(self):
        process = Popen(['stty', 'size'], stdout=PIPE)
        out, _ = process.communicate()
        return [int(v) for v in out.split()]

    @contextmanager
    def step(self, msg='', success='done', failure='fail'):
        self.stdout.write('  - %s %s' % (msg, SAVE))
        try:
            yield
        except Exception:
            self.stdout.write(RESTORE + self.style.ERROR(failure))
            raise
        self.stdout.write(RESTORE + self.style.SUCCESS(success))

    def stream(self, args, cwd=None):
        """
        Stream the output of the subprocess
        """
        process = Popen(args, cwd=cwd, stdout=PIPE)
        line_buffer = deque(maxlen=self.rows - 20)

        for line in iter(process.stdout.readline, ''):
            line_buffer.append((u'    ' + line.decode('utf-8'))[:self.cols])
            self.stdout.write(RESTORE)
            self.stdout.write(self.sep)
            self.stdout.write(''.join(line_buffer))
            self.stdout.write(self.sep)
        process.wait()

    def handle(self, *args, **options):
        ref = options['ref']
        ts = now().strftime(DATETIME_FORMAT)
        path = 'bundles/build-%(ref)s-%(ts)s' % locals()
        out = options['output'] or (path + '.zip')

        msg = 'Creating application bundle for: %s' % ref
        self.stdout.write(self.style.MIGRATE_HEADING(msg))

        # copy the project to archive directory
        with self.step('Creating build directory at...'):
            archive = Popen(['git',  'archive', ref], stdout=PIPE)
            check_call(['mkdir', '-p', path])
            check_call(['tar', '-x', '-C', path], stdin=archive.stdout)
            archive.stdout.close()
            archive.wait()
            if archive.returncode > 0:
                raise CommandError("'%s' is an invalid git reference" % ref)

        # javascript build
        if os.path.exists(os.path.join(path, 'package.json')):
            with self.step('Found \'package.json\'. Building javascript...'):
                self.stream(['npm', 'install', '--only=production'], cwd=path)
                self.stream(['npm', 'run', 'build'], cwd=path)
        else:
            self.stdout.write('  - No \'package.json\' found. Skipping javascript build.')

        # Create zip archive
        with self.step('Writing bundle...'):
            self.stream(['zip', '-r', os.path.abspath(out), '.'], cwd=path)
        self.stdout.write('')

        # write paths to stdout
        if not out.startswith(path):
            self.stdout.write('Build directory:')
            self.stdout.write(self.style.NOTICE('  %s' % path))
        self.stdout.write('Bundle path:')
        self.stdout.write(self.style.NOTICE('  %s' % out))
