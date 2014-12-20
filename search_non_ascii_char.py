import os
import string
import sys

def search_non_ascii_char(dir_path):
    for dirname, dirnames, filenames in os.walk(dir_path):
        for filename in filenames:
	    fname_woext, fext = os.path.splitext(filename)
	    #if fext not in ['.po', '.pyc', '.jpg', '']:
            if fext in ['.py,', '.xml']:
	        fname_path = os.path.join(dirname, filename)
		count_newline = 1
		with open(fname_path) as fin:
		    while True:
    			c = fin.read(1)
    			if not c:
      			    #print "End of file"
      			    break
			if c == '\n':
				count_newline += 1
			if c not in string.printable:
			    print "file", fname_path, "has a non-ascii char", [c], "lineno", count_newline
			    #break

def main():
    search_non_ascii_char(sys.argv[1])

if __name__ == '__main__':
    main()
