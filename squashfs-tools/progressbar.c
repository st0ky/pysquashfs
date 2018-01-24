/*
 * Create a squashfs filesystem.  This is a highly compressed read only
 * filesystem.
 *
 * Copyright (c) 2012, 2013
 * Phillip Lougher <phillip@squashfs.org.uk>
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2,
 * or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 *
 * progressbar.c
 */

#include <pthread.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <signal.h>
#include <sys/time.h>
#include <stdio.h>
#include <math.h>
#include <stdarg.h>
#include <errno.h>
#include <stdlib.h>

#include "error.h"

int progress_enabled = 0;
int rotate = 0;
int cur_uncompressed = 0, estimated_uncompressed = 0;
int columns;

pthread_t progress_thread;
pthread_mutex_t progress_mutex = PTHREAD_MUTEX_INITIALIZER;


static void sigwinch_handler()
{
	struct winsize winsize;

	if(ioctl(1, TIOCGWINSZ, &winsize) == -1) {
		if(isatty(STDOUT_FILENO))
			printf("TIOCGWINSZ ioctl failed, defaulting to 80 "
				"columns\n");
		columns = 80;
	} else
		columns = winsize.ws_col;
}


static void sigalrm_handler()
{
	rotate = (rotate + 1) % 4;
}


void inc_progress_bar()
{
	cur_uncompressed ++;
}


void dec_progress_bar(int count)
{
	cur_uncompressed -= count;
}


void progress_bar_size(int count)
{
	estimated_uncompressed += count;
}


static void progress_bar(long long current, long long max, int columns)
{
	char rotate_list[] = { '|', '/', '-', '\\' };
	int max_digits, used, hashes, spaces;
	static int tty = -1;

	if(max == 0)
		return;

	max_digits = floor(log10(max)) + 1;
	used = max_digits * 2 + 11;
	hashes = (current * (columns - used)) / max;
	spaces = columns - used - hashes;

	if((current > max) || (columns - used < 0))
		return;

	if(tty == -1)
		tty = isatty(STDOUT_FILENO);
	if(!tty) {
		static long long previous = -1;

		/* Updating much more frequently than this results in huge
		 * log files. */
		if((current % 100) != 0 && current != max)
			return;
		/* Don't update just to rotate the spinner. */
		if(current == previous)
			return;
		previous = current;
	}

	printf("\r[");

	while (hashes --)
		putchar('=');

	putchar(rotate_list[rotate]);

	while(spaces --)
		putchar(' ');

	printf("] %*lld/%*lld", max_digits, current, max_digits, max);
	printf(" %3lld%%", current * 100 / max);
	fflush(stdout);
}


void enable_progress_bar()
{
	pthread_mutex_lock(&progress_mutex);
	progress_enabled = 1;
	pthread_mutex_unlock(&progress_mutex);
}


void disable_progress_bar()
{
	pthread_mutex_lock(&progress_mutex);
	if(progress_enabled)  {
		progress_bar(cur_uncompressed, estimated_uncompressed, columns);
		printf("\n");
	}
	progress_enabled = 0;
	pthread_mutex_unlock(&progress_mutex);
}


void *progress_thrd(void *arg)
{
	struct timespec requested_time, remaining;
	struct itimerval itimerval;
	struct winsize winsize;

	if(ioctl(1, TIOCGWINSZ, &winsize) == -1) {
		if(isatty(STDOUT_FILENO))
			printf("TIOCGWINSZ ioctl failed, defaulting to 80 "
				"columns\n");
		columns = 80;
	} else
		columns = winsize.ws_col;
	signal(SIGWINCH, sigwinch_handler);
	signal(SIGALRM, sigalrm_handler);

	itimerval.it_value.tv_sec = 0;
	itimerval.it_value.tv_usec = 250000;
	itimerval.it_interval.tv_sec = 0;
	itimerval.it_interval.tv_usec = 250000;
	setitimer(ITIMER_REAL, &itimerval, NULL);

	requested_time.tv_sec = 0;
	requested_time.tv_nsec = 250000000;

	while(1) {
		int res = nanosleep(&requested_time, &remaining);

		if(res == -1 && errno != EINTR)
			BAD_ERROR("nanosleep failed in progress thread\n");

		if(progress_enabled) {
			pthread_mutex_lock(&progress_mutex);
			progress_bar(cur_uncompressed, estimated_uncompressed,
				columns);
			pthread_mutex_unlock(&progress_mutex);
		}
	}
}


void init_progress_bar()
{
	pthread_create(&progress_thread, NULL, progress_thrd, NULL);
}


void progressbar_error(char *fmt, ...)
{
	va_list ap;

	pthread_mutex_lock(&progress_mutex);

	if(progress_enabled)
		fprintf(stderr, "\n");

	va_start(ap, fmt);
	vfprintf(stderr, fmt, ap);
	va_end(ap);

	pthread_mutex_unlock(&progress_mutex);
}


void progressbar_info(char *fmt, ...)
{
	va_list ap;

	pthread_mutex_lock(&progress_mutex);

	if(progress_enabled)
		printf("\n");

	va_start(ap, fmt);
	vprintf(fmt, ap);
	va_end(ap);

	pthread_mutex_unlock(&progress_mutex);
}

