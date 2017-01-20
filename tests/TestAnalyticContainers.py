
import unittest
import os.path
import subprocess

def is_container(path):
	return os.path.isdir(path) and \
		os.path.isfile(os.path.join(path,'Dockerfile')) and \
		os.path.isfile(os.path.join(path,'run.sh'))

def find_containers(base_path):
	return [p for p in \
		[os.path.join(base_path,c) for c in os.listdir(base_path)] \
		if is_container(p)]

def test_generator(container):

	def test_container(self):

		c_path = os.path.abspath(container)
		sh_path = os.path.join(c_path,'run.sh')

		proc = subprocess.Popen(sh_path,cwd=c_path,stdout=self.fd,stderr=self.fd)

		ret_code = proc.wait()

		self.assertEqual(0,ret_code)

	return test_container

class TestAnalyticContainers(unittest.TestCase):

	def setUp(self):
		test_name = self._testMethodName
		print '%s.%s - setUp ' % (self.__class__.__name__,test_name)

		self.output_file = open(test_name +'.log','w')
		self.fd = self.output_file.fileno()

	def tearDown(self):
		self.fd = None
		self.output_file.close()

for c in find_containers('..'):
	test = test_generator(c)
	test_name = 'test'+c.replace('.','').replace('/','_')
	setattr(TestAnalyticContainers,test_name,test)

if __name__ == '__main__':
	unittest.main()
