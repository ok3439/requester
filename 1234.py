import zipfile
import sys
IS_PY2 = sys.version_info < (3, 0)
import requests

if IS_PY2:
    from Queue import Queue
else:
    from queue import Queue

from threading import Thread

LIMIT=100000

class Worker(Thread):
    """ Thread executing tasks from a given tasks queue """
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                # An exception happened in this thread
                print(e)
            finally:
                # Mark this task as done, whether an exception happened or not
                self.tasks.task_done()


class ThreadPool:
    """ Pool of threads consuming tasks from a queue """
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """ Add a task to the queue """
        self.tasks.put((func, args, kargs))

    def map(self, func, args_list):
        """ Add a list of tasks to the queue """
        for args in args_list:
            self.add_task(func, args)

    def wait_completion(self):
        """ Wait for completion of all the tasks in the queue """
        self.tasks.join()

domains = []
zf = zipfile.ZipFile('top-1m.csv.zip')
try:
	data = zf.read('top-1m.csv')
except KeyError:
	print 'ERROR: Did not find %s in zip file' % filename
else:
	counter = 0
	for line in data.split("\n"):
		#domains.append( line.split(",")[1])
		domains.append( line.strip())
		counter = counter+1
		if counter > LIMIT:
			break


if __name__ == "__main__":

    # Function to be executed in a thread
    def getDomain(domain):
		try:
			n = int(domain.split(",")[0])
			host = domain.split(",")[1]
			response = requests.get('https://%s/favicon.ico' % host, allow_redirects=False, timeout=1.0)
			if n % 1000 == 0:
				print "Requested %s %d" % (host, n)
		except:
			pass

    pool = ThreadPool(10)

    pool.map(getDomain, domains)
    pool.wait_completion()