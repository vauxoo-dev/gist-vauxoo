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
		count_col = 0
		with open(fname_path) as fin:
		    while True:
    			c = fin.read(1)
    			if not c:
      			    #print "End of file"
      			    break
			count_col += 1
			if c == '\n':
				count_newline += 1
				count_col = 0
			if c not in string.printable:
			    print "%s:%d:%d %s" %( fname_path, count_newline, count_col, [c])
			    fin.read(1) # Non-ascii char use 2 chars

def main():
    search_non_ascii_char(sys.argv[1])

if __name__ == '__main__':
    main()
